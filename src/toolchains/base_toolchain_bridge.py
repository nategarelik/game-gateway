import uuid
from queue import Queue
from concurrent.futures import Future
from threading import Thread, Lock
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# Configure a basic logger for the base bridge
# Applications using this bridge can configure their own logging further
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) # Default level

class BaseToolchainBridge(ABC):
    """
    A base class for toolchain bridges that interact with external tools or services asynchronously.
    It handles common functionalities like request queuing, threaded processing, and future-based responses.
    """
    def __init__(self, mcp_server):
        """
        Initializes the BaseToolchainBridge.

        Args:
            mcp_server: The Master Control Program server instance.
        """
        self.mcp_server = mcp_server # Instance of MCPServer or similar for context/logging
        self._request_queue = Queue()
        self._worker_thread = None
        self._worker_lock = Lock() # To ensure only one worker thread is started
        self.bridge_name = self.__class__.__name__
        logger.info(f"{self.bridge_name} initialized.")

    def _start_worker_if_needed(self):
        """Starts the worker thread if it's not already running."""
        with self._worker_lock:
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._worker_thread = Thread(target=self._process_request_queue, daemon=True, name=f"{self.bridge_name}Worker")
                self._worker_thread.start()
                logger.info(f"{self.bridge_name}: Worker thread started.")

    def _submit_request(self, request_type: str, payload: dict, agent_id: str = None) -> Future:
        """
        Submits a request to the toolchain.

        Args:
            request_type (str): The type of request (e.g., "ASSEMBLE_SCENE", "GENERATE_ASSET").
            payload (dict): The actual data/command for the request.
            agent_id (str, optional): The ID of the agent making the request.

        Returns:
            Future: A future that will eventually hold the result or exception.
        """
        request_id = str(uuid.uuid4())
        future = Future()
        
        request_data = {
            "id": request_id,
            "type": request_type,
            "payload": payload, # The specific command/data for the tool
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "_future": future # Internal use for linking back
        }
        
        self._request_queue.put(request_data)
        logger.debug(f"{self.bridge_name}: Queued request {request_id} of type '{request_type}'.")
        self._start_worker_if_needed()
        
        return future

    def _process_request_queue(self):
        """Continuously processes requests from the queue."""
        logger.info(f"{self.bridge_name}: Worker thread started processing queue.")
        while True: # Keep running to process new items as they arrive
            request_data = self._request_queue.get()
            if request_data is None: # Sentinel value to stop the thread (optional)
                logger.info(f"{self.bridge_name}: Worker thread received stop signal.")
                self._request_queue.task_done()
                break

            future = request_data.pop("_future") # Extract future, don't pass to subclass
            request_id = request_data["id"]
            request_type = request_data["type"]
            
            logger.info(f"{self.bridge_name}: Processing request {request_id} of type '{request_type}'.")
            try:
                # Subclasses must implement _handle_specific_request
                result = self._handle_specific_request(request_type, request_data)
                future.set_result(result)
                logger.debug(f"{self.bridge_name}: Successfully processed request {request_id}. Result set.")
            except Exception as e:
                logger.error(f"{self.bridge_name}: Error processing request {request_id} of type '{request_type}': {e}", exc_info=True)
                future.set_exception(e)
            finally:
                self._request_queue.task_done()
        logger.info(f"{self.bridge_name}: Worker thread finished.")

    @abstractmethod
    def _handle_specific_request(self, request_type: str, request_data: dict):
        """
        Handles a specific request type. Subclasses must implement this method.
        This method will be called by the worker thread.

        Args:
            request_type (str): The type of the request.
            request_data (dict): The full request data dictionary (id, type, payload, agent_id, timestamp).

        Returns:
            The result of processing the request.

        Raises:
            Exception: If an error occurs during processing.
        """
        pass

    def shutdown(self, wait=True):
        """Gracefully shuts down the worker thread."""
        logger.info(f"{self.bridge_name}: Initiating shutdown...")
        if self._worker_thread and self._worker_thread.is_alive():
            self._request_queue.put(None) # Sentinel to stop the worker
            if wait:
                self._worker_thread.join(timeout=5) # Wait for worker to finish
                if self._worker_thread.is_alive():
                    logger.warning(f"{self.bridge_name}: Worker thread did not terminate in time.")
        logger.info(f"{self.bridge_name}: Shutdown complete.")

    # Example of how a subclass might expose a specific command
    # def example_command(self, data_for_command: dict, agent_id: str = None) -> Future:
    #     return self._submit_request(request_type="EXAMPLE_COMMAND_TYPE", payload=data_for_command, agent_id=agent_id)