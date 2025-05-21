# src/protocols/advanced_collaboration_protocols.py
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Set
import time
import random

logger = logging.getLogger(__name__)

# --- Conceptual Data Structures ---

class AgentProfile:
    """Represents an agent's profile, including its capabilities and current status."""
    def __init__(self, agent_id: str, capabilities: List[str], current_task_id: Optional[str] = None, status: str = "idle"):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.current_task_id = current_task_id
        self.status = status # e.g., "idle", "processing_task", "awaiting_assistance"

class TaskAssistanceRequest:
    """Represents a request from one agent to another for assistance on a task."""
    def __init__(self, requesting_agent_id: str, original_task_id: str, required_capability: str, task_details: Dict[str, Any]):
        self.request_id = f"assist_{original_task_id}_{int(time.time())}"
        self.requesting_agent_id = requesting_agent_id
        self.original_task_id = original_task_id
        self.required_capability = required_capability
        self.task_details = task_details # Specific sub-task for the assisting agent
        self.status = "pending" # "pending", "accepted", "rejected", "completed"
        self.assigned_assisting_agent_id: Optional[str] = None

class AgentEvent:
    """Represents an event posted by an agent, for real-time communication/feedback."""
    def __init__(self, event_id: str, source_agent_id: str, event_type: str, data: Dict[str, Any], timestamp: Optional[float] = None):
        self.event_id = event_id
        self.source_agent_id = source_agent_id
        self.event_type = event_type # e.g., "task_progress_update", "resource_generated", "error_encountered"
        self.data = data
        self.timestamp = timestamp or time.time()

# --- Core Protocol Components (Conceptual Implementations) ---

class CollaborationManager:
    """
    Manages multi-agent collaboration, including task assistance requests.
    This would typically interact closely with the MCP.
    """
    def __init__(self, mcp_interface: Any): # mcp_interface would be a class to interact with MCP
        self.mcp = mcp_interface # Conceptual MCP interface for tasking and agent discovery
        self.registered_agents: Dict[str, AgentProfile] = {} # agent_id -> AgentProfile
        self.pending_assistance_requests: Dict[str, TaskAssistanceRequest] = {}
        logger.info("CollaborationManager initialized.")

    def register_agent(self, agent_id: str, capabilities: List[str]):
        """Registers an agent with the collaboration manager."""
        profile = AgentProfile(agent_id=agent_id, capabilities=capabilities)
        self.registered_agents[agent_id] = profile
        logger.info(f"Agent '{agent_id}' registered with capabilities: {capabilities}")

    def update_agent_status(self, agent_id: str, status: str, current_task_id: Optional[str] = None):
        if agent_id in self.registered_agents:
            self.registered_agents[agent_id].status = status
            self.registered_agents[agent_id].current_task_id = current_task_id
            logger.debug(f"Agent '{agent_id}' status updated to '{status}' (Task: {current_task_id})")
        else:
            logger.warning(f"Attempted to update status for unregistered agent '{agent_id}'.")

    async def request_assistance(self, requesting_agent_id: str, original_task_id: str, required_capability: str, task_details: Dict[str, Any]) -> Optional[str]:
        """
        An agent requests assistance from another agent with a specific capability.
        This method finds a suitable agent and (conceptually) dispatches a new sub-task via MCP.

        Returns:
            The request_id of the TaskAssistanceRequest if successfully initiated, else None.
        """
        if requesting_agent_id not in self.registered_agents:
            logger.error(f"Unregistered agent '{requesting_agent_id}' cannot request assistance.")
            return None

        logger.info(f"Agent '{requesting_agent_id}' requests assistance for task '{original_task_id}' requiring capability '{required_capability}'.")
        
        # Find a suitable available agent (simple strategy: first available with capability)
        suitable_assisting_agent_id: Optional[str] = None
        for agent_id, profile in self.registered_agents.items():
            if agent_id == requesting_agent_id: # Agent cannot assist itself in this model
                continue
            if required_capability in profile.capabilities and profile.status == "idle":
                suitable_assisting_agent_id = agent_id
                break
        
        if not suitable_assisting_agent_id:
            logger.warning(f"No suitable idle agent found with capability '{required_capability}' for task '{original_task_id}'.")
            # TODO: Could queue the request or try other strategies
            return None

        assistance_request = TaskAssistanceRequest(requesting_agent_id, original_task_id, required_capability, task_details)
        assistance_request.assigned_assisting_agent_id = suitable_assisting_agent_id
        assistance_request.status = "pending_dispatch" # Mark as pending dispatch to MCP
        self.pending_assistance_requests[assistance_request.request_id] = assistance_request
        
        logger.info(f"Found suitable agent '{suitable_assisting_agent_id}' for assistance request '{assistance_request.request_id}'.")

        # Conceptual: Dispatch a new task to the assisting_agent_id via MCP
        # This would involve using self.mcp.create_task(...) or similar
        try:
            # sub_task_payload = {
            #     "type": "assistance_sub_task",
            #     "original_task_id": original_task_id,
            #     "requesting_agent_id": requesting_agent_id,
            #     "assistance_request_id": assistance_request.request_id,
            #     "details": task_details
            # }
            # mcp_sub_task_id = await self.mcp.create_task(target_agent_id=suitable_assisting_agent_id, task_definition=sub_task_payload)
            
            # Simulate MCP dispatch
            await asyncio.sleep(0.1)
            mcp_sub_task_id = f"mcp_subtask_{random.randint(10000,99999)}" 
            logger.info(f"Conceptually dispatched assistance sub-task '{mcp_sub_task_id}' to agent '{suitable_assisting_agent_id}' for request '{assistance_request.request_id}'.")
            assistance_request.status = "dispatched_to_mcp"
            self.update_agent_status(suitable_assisting_agent_id, "processing_task", mcp_sub_task_id)
            return assistance_request.request_id
        except Exception as e:
            logger.error(f"Failed to dispatch assistance sub-task for request '{assistance_request.request_id}': {e}")
            assistance_request.status = "dispatch_failed"
            return None

    def update_assistance_request_status(self, request_id: str, status: str, result_data: Optional[Dict] = None):
        """Callback for when an assistance sub-task is completed or fails."""
        if request_id in self.pending_assistance_requests:
            req = self.pending_assistance_requests[request_id]
            req.status = status
            logger.info(f"Assistance request '{request_id}' status updated to '{status}'. Result: {result_data}")
            # Notify the original requesting agent (conceptual)
            # self.mcp.post_event_to_agent(req.requesting_agent_id, "assistance_result", {"request_id": request_id, "status": status, "data": result_data})
            if status in ["completed", "failed", "rejected"]: # Terminal states
                if req.assigned_assisting_agent_id:
                    self.update_agent_status(req.assigned_assisting_agent_id, "idle") # Make assisting agent idle again
                # del self.pending_assistance_requests[request_id] # Or move to a completed list
        else:
            logger.warning(f"Attempted to update status for unknown assistance request '{request_id}'.")


class AgentEventBus:
    """
    A conceptual event bus for real-time communication and feedback between agents.
    Agents can publish events, and other agents (or systems) can subscribe to specific event types.
    This would typically be a core feature of the MCP.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {} # event_type -> list of async callback functions
        self.event_history: List[AgentEvent] = [] # Optional: keep a short history
        self.max_history_len = 100
        logger.info("AgentEventBus initialized.")

    async def subscribe(self, event_type: str, callback: Callable):
        """Subscribes a callback to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            logger.info(f"New subscriber for event type '{event_type}'.")
        else:
            logger.debug(f"Callback already subscribed to event type '{event_type}'.")


    async def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribes a callback from an event type."""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            logger.info(f"Unsubscribed callback from event type '{event_type}'.")
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

    async def publish_event(self, source_agent_id: str, event_type: str, data: Dict[str, Any]):
        """Publishes an event to all subscribers of that event type."""
        event_id = f"evt_{source_agent_id}_{event_type}_{int(time.time())}_{random.randint(100,999)}"
        event = AgentEvent(event_id, source_agent_id, event_type, data)
        
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_len:
            self.event_history.pop(0) # Keep history bounded

        logger.info(f"Agent '{source_agent_id}' published event '{event_type}': {data}")
        
        if event_type in self.subscribers:
            # Callbacks are async, gather them to run concurrently
            callback_tasks = [callback(event) for callback in self.subscribers[event_type]]
            await asyncio.gather(*callback_tasks, return_exceptions=True) # Log exceptions if any callback fails
            # Note: gather will log exceptions if return_exceptions=True, but won't raise them here.
            # Proper error handling for callbacks might be needed.


# --- Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Mock MCP Interface for CollaborationManager
    class MockMCP:
        async def create_task(self, target_agent_id: str, task_definition: dict):
            mcp_task_id = f"mcp_task_{target_agent_id}_{int(time.time())}"
            logger.info(f"[MockMCP] Task '{mcp_task_id}' created for agent '{target_agent_id}': {task_definition}")
            return mcp_task_id
        
        async def post_event_to_agent(self, target_agent_id: str, event_type: str, data: dict):
            logger.info(f"[MockMCP] Event '{event_type}' posted to agent '{target_agent_id}': {data}")

    mock_mcp = MockMCP()
    collab_manager = CollaborationManager(mcp_interface=mock_mcp)
    event_bus = AgentEventBus()

    # Register some agents
    collab_manager.register_agent("PixelForge_01", ["generate_texture", "generate_image"])
    collab_manager.register_agent("LevelArchitect_01", ["design_level_layout", "place_props"])
    collab_manager.register_agent("TextGenerator_01", ["generate_npc_dialogue", "create_lore_entry"])


    async def agent_alpha_behavior(agent_id: str):
        """Simulates an agent that might request assistance."""
        logger.info(f"Agent '{agent_id}' starting its main task...")
        collab_manager.update_agent_status(agent_id, "processing_task", "main_level_design_task")
        await asyncio.sleep(0.5)
        
        # AgentAlpha needs a texture, but can't make it. Requests assistance.
        assistance_req_id = await collab_manager.request_assistance(
            requesting_agent_id=agent_id,
            original_task_id="main_level_design_task",
            required_capability="generate_texture",
            task_details={"prompt": "a mossy stone wall texture", "resolution": "1024x1024"}
        )
        if assistance_req_id:
            logger.info(f"Agent '{agent_id}' successfully submitted assistance request '{assistance_req_id}'. Awaiting result...")
            # In a real agent, it would await a signal or event indicating the assistance_req_id is complete.
            # For demo, we'll simulate the assisting agent completing it.
            await asyncio.sleep(1) # Simulate PixelForge working
            collab_manager.update_assistance_request_status(assistance_req_id, "completed", {"texture_asset_id": "tex_mossy_stone_001"})
        else:
            logger.error(f"Agent '{agent_id}' failed to get assistance for texture generation.")
        
        collab_manager.update_agent_status(agent_id, "idle")
        logger.info(f"Agent '{agent_id}' finished its main task.")


    async def agent_beta_listener(event: AgentEvent):
        """Simulates an agent listening to events."""
        logger.info(f"AgentBeta_Listener received event: ID={event.event_id}, Type={event.event_type}, From={event.source_agent_id}, Data={event.data}")

    async def main_demo():
        print("\n--- Multi-Agent Collaboration (Assistance Request) Example ---")
        # Start AgentAlpha's behavior (which will request assistance)
        asyncio.create_task(agent_alpha_behavior("LevelArchitect_01"))
        await asyncio.sleep(2) # Allow time for assistance flow

        print("\n--- Real-Time Communication (Event Bus) Example ---")
        await event_bus.subscribe("asset_generated", agent_beta_listener)
        await event_bus.subscribe("task_progress", agent_beta_listener)

        # PixelForge_01 publishes an event
        await event_bus.publish_event(
            source_agent_id="PixelForge_01",
            event_type="asset_generated",
            data={"asset_id": "img_dragon_007", "type": "image", "path": "/assets/img_dragon_007.png"}
        )
        # LevelArchitect_01 publishes a progress event
        await event_bus.publish_event(
            source_agent_id="LevelArchitect_01",
            event_type="task_progress",
            data={"task_id": "main_level_design_task", "progress_percent": 75, "status_message": "Finalizing prop placement."}
        )
        await asyncio.sleep(0.1) # Allow event processing
        await event_bus.unsubscribe("task_progress", agent_beta_listener) # Beta stops listening to progress

    asyncio.run(main_demo())