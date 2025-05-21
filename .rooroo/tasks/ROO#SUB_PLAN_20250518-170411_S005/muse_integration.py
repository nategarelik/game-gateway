import uuid
import json
from queue import Queue
from concurrent.futures import Future
from threading import Thread
from datetime import datetime

# Assumed to be defined elsewhere or provided by the MCP framework
# from mcp_server_core import MCPServer # Example, actual import might differ

class MuseToolchainBridge:
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server  # Instance of MCPServer
        self.unity_process = None  # Placeholder for managing Unity process if needed
        self.command_queue = Queue()
        self.response_handlers = {} # Stores handlers for specific response types from Muse
        # As per design doc, Unity Muse API endpoint. This might be configured from MCPServer or constants.
        self.muse_api_endpoint = "http://localhost:8080/muse/api" # Default from C# MuseAPI

    def register_response_handler(self, response_type, handler_func):
        """Register a function to handle specific response types."""
        self.response_handlers[response_type] = handler_func
        
    def send_command(self, command_type, command_text, agent_id=None):
        """Send a command to Unity Muse and return a future for the response."""
        command_id = str(uuid.uuid4())
        future = Future()
        
        # Create the command payload
        payload = {
            "id": command_id,
            "type": command_type,
            "command": command_text,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store the future for later resolution
        self.command_queue.put((payload, future))
        
        # Trigger the command processing
        self._process_command_queue()
        
        return future
        
    def _process_command_queue(self):
        """Process the command queue in a separate thread."""
        def worker():
            while not self.command_queue.empty():
                payload, future = self.command_queue.get()
                try:
                    # Send the command to Unity Muse
                    # Response is expected to be a JSON string from Unity
                    response_json_str = self._send_to_unity(payload) 
                    
                    # Parse the response
                    response_data = json.loads(response_json_str) # Assuming Unity sends JSON
                    
                    # Handle the response
                    self._handle_response(response_data, future)
                    
                except Exception as e:
                    # Log error, e.g., self.mcp_server.logger.error(...)
                    print(f"Error processing Muse command {payload.get('id')}: {e}")
                    future.set_exception(e)
                finally:
                    self.command_queue.task_done()
        
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def _send_to_unity(self, payload):
        """
        Send a command to Unity Muse via HTTP.
        This method should use an HTTP client (e.g., requests library)
        to POST the payload to the Unity Muse API endpoint.
        The Unity Muse C# MuseAPI class listens at http://localhost:8080/muse/api by default.
        It expects a JSON payload and returns a JSON string response.
        """
        # Placeholder implementation:
        print(f"MuseToolchainBridge: Sending command to Unity (placeholder): {payload}")
        # import requests # Example:
        # try:
        #     response = requests.post(self.muse_api_endpoint, json=payload, timeout=10)
        #     response.raise_for_status() # Raise an exception for HTTP errors
        #     return response.text # MuseAPI SendCommand returns string content
        # except requests.exceptions.RequestException as e:
        #     print(f"MuseToolchainBridge: HTTP request failed: {e}")
        #     raise # Re-raise the exception to be caught by _process_command_queue
        
        # Simulate a successful response for now
        mock_response = {
            "type": payload.get("type", "UNKNOWN_RESPONSE"),
            "status": "success",
            "message": "Command processed by Unity (mock)",
            "scene_id": str(uuid.uuid4()) if payload.get("type") == "ASSEMBLE_SCENE" else None,
            "original_command_id": payload.get("id")
        }
        return json.dumps(mock_response)
        
    def _handle_response(self, response_data, future):
        """Handle a response from Unity Muse."""
        response_type = response_data.get("type", "unknown")
        
        # Call the registered handler if available
        if response_type in self.response_handlers:
            try:
                result = self.response_handlers[response_type](response_data)
                future.set_result(result)
            except Exception as e:
                # Log error
                print(f"Error in response handler for type {response_type}: {e}")
                future.set_exception(e)
        else:
            # Default handling: resolve future with the full response data
            future.set_result(response_data)

MUSE_COMMAND_TEMPLATES = {
    "ASSEMBLE_SCENE": "{description} -Style:{style} -CollisionType:{collision_type}",
    "MODIFY_OBJECT": "Modify {object_id} to {modification} -Constraints:{constraints}",
    "CREATE_OBJECT": "Create {description} -Style:{style} -Position:{position}",
    "DELETE_OBJECT": "Remove {object_id} from scene"
}

def format_muse_command(command_type, **kwargs):
    """Format a command for Unity Muse using the standard templates."""
    if command_type not in MUSE_COMMAND_TEMPLATES:
        raise ValueError(f"Unknown Muse command type: {command_type}")
        
    template = MUSE_COMMAND_TEMPLATES[command_type]
    # Provide default empty strings for missing KWARGS to prevent KeyErrors if not all args are always passed
    # This makes the formatting more robust if some optional parameters in templates are not provided.
    # However, the C# side templates seem to expect all args.
    # For safety, ensure all template keys are present in kwargs or have defaults.
    # Example: style = kwargs.get('style', 'DefaultStyle')
    return template.format(**kwargs)

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    class MockMCPServer:
        def __init__(self):
            self.logger = print # Basic logger

    mock_mcp = MockMCPServer()
    muse_bridge = MuseToolchainBridge(mock_mcp)

    def my_scene_handler(response_data):
        print(f"Custom ASSEMBLE_SCENE handler received: {response_data}")
        return {"processed_scene_id": response_data.get("scene_id")}

    muse_bridge.register_response_handler("ASSEMBLE_SCENE", my_scene_handler)

    # Test formatting
    try:
        formatted_command = format_muse_command(
            "ASSEMBLE_SCENE",
            description="a dark forest",
            style="RetroPixel",
            collision_type="Grid2D"
        )
        print(f"Formatted command: {formatted_command}")

        # Test sending command
        future_response = muse_bridge.send_command("ASSEMBLE_SCENE", formatted_command, agent_id="LevelArchitectAgent_01")
        print("Command sent, waiting for response...")
        
        response = future_response.result(timeout=5) # Wait for the future to complete
        print(f"Response from Muse: {response}")

        formatted_create = format_muse_command(
            "CREATE_OBJECT",
            description="a treasure chest",
            style="Fantasy",
            position="10,5,2"
        )
        print(f"Formatted command: {formatted_create}")
        future_create = muse_bridge.send_command("CREATE_OBJECT", formatted_create, agent_id="DesignerAgent_01")
        response_create = future_create.result(timeout=5)
        print(f"Response from Muse (Create): {response_create}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Ensure threads can exit if queue processing was started
    import time
    time.sleep(0.1) # Give time for thread to process if it was very fast
    print("Example usage finished.")