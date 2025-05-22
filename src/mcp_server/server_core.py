from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file at the very beginning
print("[DEBUG] mcp_server_core.py execution started...")
import sys
import os
import re
import random # Added for AutonomousIterationWorkflow
import time # Added for AutonomousIterationWorkflow
from typing import List, Dict, Any, Optional, Callable # Added Optional, Callable for protocols
import json # For direct JSON manipulation if needed
import logging # Added for better logging

from fastapi import FastAPI
from src.mcp_server.api.routes import router as api_router
from src.mcp_server.core.state_manager import StateManager
from src.mcp_server.core.prompt_registry import PromptRegistry
from src.mcp_server.models.api_models import AgentInfo

# --- Path Setup (REMOVED as per relocation to src/mcp_server) ---
# The old sys.path manipulation is no longer suitable here.
# Agent and toolchain imports will need to be resolved via standard Python packaging
# or a different mechanism at a higher level of the application.

# --- Agent and Toolchain Imports ---
# These imports will likely fail until agents/toolchains are properly packaged
# or their paths are managed externally.
# Actual class names within these modules must match.

# Import MCPClient from its new dedicated file (now relative)
try:
    from .client import MCPClient
    print("[INFO] Successfully imported MCPClient.")
except ImportError as e:
    print(f"[ERROR] Failed to import MCPClient from mcp_client.py: {e}. This is critical.")
    MCPClient = None # Ensure it's defined, even if None, to prevent further NameErrors

_agent_classes = {}
_toolchain_classes = {}

try:
    from src.agents.level_architect_agent import LevelArchitectAgent
    _agent_classes["level_architect"] = LevelArchitectAgent
    print("[INFO] Successfully imported LevelArchitectAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import LevelArchitectAgent: {e}. This agent will not be available.")

try:
    from src.agents.code_weaver_agent import CodeWeaverAgent
    _agent_classes["code_weaver"] = CodeWeaverAgent
    print("[INFO] Successfully imported CodeWeaverAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import CodeWeaverAgent: {e}. This agent will not be available.")

try:
    from src.agents.pixel_forge_agent import PixelForgeAgent
    _agent_classes["pixel_forge"] = PixelForgeAgent
    print("[INFO] Successfully imported PixelForgeAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import PixelForgeAgent: {e}. This agent will not be available.")

try:
    from src.agents.documentation_sentinel_agent import DocumentationSentinelAgent
    _agent_classes["documentation_sentinel"] = DocumentationSentinelAgent
    print("[INFO] Successfully imported DocumentationSentinelAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import DocumentationSentinelAgent: {e}. This agent will not be available.")

# try:
#     from src.toolchains.muse_bridge import MuseToolchainBridge
#     _toolchain_classes["muse_bridge"] = MuseToolchainBridge
#     print("[INFO] Successfully imported MuseToolchainBridge.")
# except ImportError as e:
#     print(f"[Warning] Failed to import MuseToolchainBridge: {e}. Muse toolchain will not be available.")

# try:
#     from src.toolchains.retro_diffusion_bridge import RetroDiffusionToolchainBridge
#     _toolchain_classes["retro_diffusion_bridge"] = RetroDiffusionToolchainBridge
#     print("[INFO] Successfully imported RetroDiffusionToolchainBridge.")
# except ImportError as e:
#     print(f"[Warning] Failed to import RetroDiffusionToolchainBridge: {e}. Retro Diffusion toolchain will not be available.")

try:
    from src.toolchains.unity_bridge import UnityToolchainBridge # Corrected to absolute import
    _toolchain_classes["unity_bridge"] = UnityToolchainBridge
    print("[INFO] Successfully imported UnityToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import UnityToolchainBridge: {e}. Unity toolchain will not be available.")

# Import KnowledgeManagementSystem
from src.systems.knowledge_management_system import KnowledgeManagementSystem
# Import AutonomousIterationWorkflow
from src.workflows.autonomous_iteration import AutonomousIterationWorkflow
# Import Emergent Behavior Protocols
from src.protocols.emergent_behavior_protocols import CreativeConflictResolver, DynamicToolComposer, Tool, DesignProposal
# Import Advanced Collaboration Protocols
from src.protocols.advanced_collaboration_protocols import CollaborationManager, AgentEventBus, AgentProfile, TaskAssistanceRequest, AgentEvent
# Import Extensibility and Integration components
from src.systems.extensibility_integration import ToolRegistry, AbstractToolInterface, MockImageResizerTool

logger = logging.getLogger(__name__) # Initialize logger for this module

# MCPClient class has been moved to mcp_client.py
class MCPServer:
    """
    The Master Control Program (MCP) Server.

    This class orchestrates the interactions between various agents and toolchains
    within the game development ecosystem. It manages workflows, prompt generation,
    API requests, and integration with external services like Muse and Retro Diffusion.
    """
    def __init__(self):
        """
        Initializes the MCPServer instance.

        Sets up the workflow engine, prompt registry, and instantiates available
        toolchain bridges and agents.
        """
        self.mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:5000") # Added for agent instantiation
        self.knowledge_management_system = KnowledgeManagementSystem(mcp_server_url=self.mcp_server_url) # Instantiate KMS
        self.autonomous_iteration_workflow = AutonomousIterationWorkflow(mcp_task_dispatcher=self._dispatch_mcp_task) # Instantiate AIW
        self.creative_conflict_resolver = CreativeConflictResolver(mcp_event_notifier=self._post_mcp_event) # Instantiate CCR
        self.agent_event_bus = AgentEventBus() # Instantiate AgentEventBus
        self.collaboration_manager = CollaborationManager(mcp_interface=self) # Instantiate CollaborationManager, pass self as MCP interface
        
        # Prepare tools for DynamicToolComposer
        available_tools = []
        # Add toolchain bridges as tools
        # if hasattr(self, 'muse_bridge') and self.muse_bridge:
        #     available_tools.append(Tool("muse_toolchain", "Muse Toolchain", ["conceptual_generation", "text_generation"], {}))
        # if hasattr(self, 'retro_diffusion_bridge') and self.retro_diffusion_bridge:
        #     available_tools.append(Tool("retro_diffusion_toolchain", "Retro Diffusion Toolchain", ["image_generation", "texture_generation"], {}))
        
        # This is where self.unity_bridge would be initialized if MCPServer instance was used by FastAPI app state
        self.unity_bridge = None # Initialize to None
        if "unity_bridge" in _toolchain_classes:
            try:
                self.unity_bridge = _toolchain_classes["unity_bridge"](self) # Pass MCPServer instance
                print("[INFO] MCPServer.__init__: UnityToolchainBridge initialized.")
                available_tools.append(Tool("unity_toolchain", "Unity Toolchain", ["scene_manipulation", "script_execution", "asset_placement"], {}))
            except Exception as e:
                 print(f"[ERROR] MCPServer.__init__: Failed to initialize UnityToolchainBridge: {e}")
        else:
            print("[Warning] MCPServer.__init__: UnityToolchainBridge class not found in _toolchain_classes.")

        
        # Add conceptual tools from agents (this would be more dynamic in a real system)
        available_tools.append(Tool("level_architect_agent_tool", "Level Architect Agent", ["level_design", "procedural_generation_guidance"], {}))
        available_tools.append(Tool("code_weaver_agent_tool", "Code Weaver Agent", ["script_generation", "game_logic_implementation", "ui_scripting"], {}))
        available_tools.append(Tool("pixel_forge_agent_tool", "Pixel Forge Agent", ["asset_generation_2d", "asset_generation_3d_placeholder", "asset_placement"], {}))
        available_tools.append(Tool("documentation_sentinel_agent_tool", "Documentation Sentinel Agent", ["documentation_monitoring", "knowledge_update_trigger", "script_documentation_generation"], {}))

        self.dynamic_tool_composer = DynamicToolComposer(available_tools=available_tools) # Instantiate DTC
        self.tool_registry = ToolRegistry() # Instantiate ToolRegistry

        # Register example external tools
        self.tool_registry.register_tool(MockImageResizerTool())
        logger.info("Example external tools registered with ToolRegistry.")

        # Instantiate Toolchain Bridges - Unity bridge is now handled above
        # if "muse_bridge" in _toolchain_classes:
        #     self.muse_bridge = _toolchain_classes["muse_bridge"](self)
        #     print("[INFO] MuseToolchainBridge initialized.")
        # else:
        #     self.muse_bridge = None
        #     print("[Warning] MuseToolchainBridge not available.")

        # if "retro_diffusion_bridge" in _toolchain_classes:
        #     self.retro_diffusion_bridge = _toolchain_classes["retro_diffusion_bridge"](self)
        #     print("[INFO] RetroDiffusionToolchainBridge initialized.")
        # else:
        #     self.retro_diffusion_bridge = None
        #     print("[Warning] RetroDiffusionToolchainBridge not available.")
        
        print("MCPServer core initialized.")

        # Configure Knowledge Management System sources
        self.knowledge_management_system.add_document_source(
            path_or_url="docs/game_design_principles.md",
            source_type="local_markdown_dir",
            source_id="game_design_principles"
        )
        self.knowledge_management_system.add_document_source(
            path_or_url="docs/unity_api_best_practices.md",
            source_type="local_markdown_dir",
            source_id="unity_api_best_practices"
        )
        self.knowledge_management_system.add_document_source(
            path_or_url="docs/scripting_best_practices.md",
            source_type="local_markdown_dir",
            source_id="scripting_best_practices"
        )
        self.knowledge_management_system.add_document_source(
            path_or_url="docs/existing_assets_placeholders.md",
            source_type="local_markdown_dir",
            source_id="existing_assets_placeholders"
        )
        logger.info("Knowledge Management System sources configured.")


    def send_muse_command(self, command_type: str, command_text: str, agent_id: str = None):
        """
        Sends a command to the Muse toolchain via its bridge.

        Args:
            command_type (str): The type of command to send to Muse.
            command_text (str): The content of the command.
            agent_id (Optional[str]): The ID of the agent initiating the command.
                                      Defaults to None.

        Returns:
            Any: The response from the Muse toolchain bridge.

        Raises:
            ConnectionError: If the MuseToolchainBridge is not available.
        """
        if self.muse_bridge is None:
            print("[ERROR] MuseToolchainBridge is not available.")
            raise ConnectionError("MuseToolchainBridge not available.")
        print(f"MCPServer: Relaying command to Muse: Type='{command_type}', Agent='{agent_id}'")
        # Assuming bridge's send_command is synchronous or handles async internally for API.
        return self.muse_bridge.send_command(command_type, command_text, agent_id)

    def generate_retro_asset(self, prompt: str, parameters: Dict[str, Any] = None, agent_id: str = None):
        """
        Requests asset generation from the Retro Diffusion toolchain via its bridge.

        Args:
            prompt (str): The prompt to use for asset generation.
            parameters (Optional[Dict[str, Any]]): Additional parameters for the
                                                   generation process. Defaults to None.
            agent_id (Optional[str]): The ID of the agent initiating the request.
                                      Defaults to None.

        Returns:
            Any: The asset data or response from the Retro Diffusion toolchain bridge.

        Raises:
            ConnectionError: If the RetroDiffusionToolchainBridge is not available.
        """
        if self.retro_diffusion_bridge is None:
            print("[ERROR] RetroDiffusionToolchainBridge is not available.")
            raise ConnectionError("RetroDiffusionToolchainBridge not available.")
        print(f"MCPServer: Relaying asset generation request to Retro Diffusion: Prompt='{prompt}', Agent='{agent_id}'")
        # Assuming bridge's generate_asset is synchronous or handles async internally.
        return self.retro_diffusion_bridge.generate_asset(prompt, parameters, agent_id)

    # --- New API Request Handler ---
    def handle_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handles incoming API requests directed at agents or toolchains.

        This method routes requests to the appropriate agent's `handle_direct_request`
        method or to the relevant toolchain bridge based on the `agent_id` in the
        request data.

        Args:
            request_data (Dict[str, Any]): The JSON payload from the API request.
                                           Expected keys: "task_id", "agent_id", "parameters".

        Returns:
            Dict[str, Any]: A dictionary containing the task_id, status (success/failed),
                            result, and error information (if any).
        """
        task_id = request_data.get("task_id")
        agent_id_req = request_data.get("agent_id") # Renamed to avoid clash with toolchain agent_id param
        parameters = request_data.get("parameters", {})

        if not task_id or not agent_id_req:
            return {
                "task_id": task_id or "unknown_task",
                "status": "failed",
                "result": None,
                "error": {"code": "INVALID_REQUEST", "message": "Missing task_id or agent_id in request."}
            }

        try:
            print(f"[API Request] Task ID: {task_id}, Agent ID: {agent_id_req}, Params: {parameters}")
            # This assumes self.agents is populated, which it isn't in the current FastAPI startup.
            # This logic needs to use app.state.registered_agents
            # For now, this part of handle_api_request will likely not work as intended.
            if agent_id_req in app.state.registered_agents: # Corrected to use app.state
                agent_instance = app.state.registered_agents[agent_id_req]
                if hasattr(agent_instance, 'handle_direct_request') and callable(agent_instance.handle_direct_request):
                    # Call the agent's specific handler for direct requests
                    result_data = agent_instance.handle_direct_request(parameters) # This should be async if agent method is async
                    return {"task_id": task_id, "status": "success", "result": result_data, "error": None}
                else:
                    print(f"[ERROR] Agent '{agent_id_req}' does not have a callable 'handle_direct_request' method.")
                    raise NotImplementedError(f"Agent '{agent_id_req}' does not implement 'handle_direct_request'.")

            elif agent_id_req == "muse":
                if self.muse_bridge is None: raise ConnectionError("Muse toolchain not available.")
                command_type = parameters.get("command_type")
                command_text = parameters.get("command_text")
                if command_type is None or command_text is None:
                    raise ValueError("Missing 'command_type' or 'command_text' for Muse toolchain.")
                muse_response = self.send_muse_command(command_type, command_text, agent_id=task_id)
                return {"task_id": task_id, "status": "success", "result": {"muse_response": muse_response}, "error": None}

            elif agent_id_req == "retro_diffusion":
                if self.retro_diffusion_bridge is None: raise ConnectionError("Retro Diffusion toolchain not available.")
                prompt = parameters.get("prompt")
                if prompt is None:
                    raise ValueError("Missing 'prompt' for Retro Diffusion toolchain.")
                asset_data = self.generate_retro_asset(prompt, parameters.get("options", {}), agent_id=task_id)
                return {"task_id": task_id, "status": "success", "result": {"asset_data": asset_data}, "error": None}

            elif agent_id_req == "unity":
                # Use the unity_bridge instance from app.state if available
                unity_bridge_to_use = getattr(app.state, 'unity_bridge_instance', None)
                if unity_bridge_to_use is None: raise ConnectionError("Unity toolchain not available in app.state.")
                command_type = parameters.get("command_type")
                command_args = parameters.get("arguments", {})
                if command_type is None:
                    raise ValueError("Missing 'command_type' for Unity toolchain.")
                # Assuming send_command is synchronous or MCPClient handles async
                unity_response = unity_bridge_to_use.send_command(command_type, command_args)
                return {"task_id": task_id, "status": "success", "result": {"unity_response": unity_response}, "error": None}
            
            else:
                print(f"[ERROR] Agent or toolchain with ID '{agent_id_req}' not found.")
                return {
                    "task_id": task_id, "status": "failed", "result": None,
                    "error": {"code": "AGENT_NOT_FOUND", "message": f"Agent or toolchain ID '{agent_id_req}' not found."}
                }

        except ConnectionError as e:
            print(f"[ERROR] Toolchain Connection Error for task {task_id} (agent: {agent_id_req}): {e}")
            return {"task_id": task_id, "status": "failed", "result": None, "error": {"code": "TOOLCHAIN_CONNECTION_ERROR", "message": str(e)}}
        except ValueError as e: # For parameter validation errors
            print(f"[ERROR] Invalid Parameters for task {task_id} (agent: {agent_id_req}): {e}")
            return {"task_id": task_id, "status": "failed", "result": None, "error": {"code": "INVALID_PARAMETERS", "message": str(e)}}
        except NotImplementedError as e:
             print(f"[ERROR] Agent Interface Mismatch for task {task_id} (agent: {agent_id_req}): {e}")
             return {"task_id": task_id, "status": "failed", "result": None, "error": {"code": "AGENT_INTERFACE_ERROR", "message": str(e)}}
        except Exception as e:
            import traceback
            print(f"[CRITICAL ERROR] Unexpected error processing task {task_id} (agent: {agent_id_req}): {e}\n{traceback.format_exc()}")
            return {
                "task_id": task_id, "status": "failed", "result": None,
                "error": {"code": "EXECUTION_ERROR", "message": f"An unexpected server error occurred: {str(e)}"}
            }

    async def trigger_knowledge_update(self):
        """
        Triggers an update cycle for the Knowledge Management System.
        """
        logger.info("MCPServer: Triggering Knowledge Management System update cycle.")
        await self.knowledge_management_system.run_update_cycle()
        logger.info("MCPServer: Knowledge Management System update cycle completed.")

    async def _dispatch_mcp_task(self, task_spec: Dict[str, Any]) -> str:
        """
        Dispatches a task to the MCP server's API. This acts as the mcp_task_dispatcher
        for the AutonomousIterationWorkflow.
        """
        logger.info(f"MCPServer: Dispatching task from AutonomousIterationWorkflow: {task_spec}")
        # Assuming task_spec contains "agent_id" and "parameters"
        # We need to generate a task_id for this dispatch
        task_id = f"aiw_dispatched_task_{int(time.time())}_{random.randint(1000,9999)}"
        
        request_data = {
            "task_id": task_id,
            "agent_id": task_spec.get("target_agent_alias"), # Use target_agent_alias from AIW suggestion
            "parameters": task_spec.get("details") # Use details as parameters
        }
        
        # Call the internal handle_api_request method
        # This needs to be async if handle_api_request becomes async due to agent calls
        response = self.handle_api_request(request_data) # Assuming handle_api_request is sync for now
        
        if response.get("status") == "success":
            logger.info(f"MCPServer: Successfully dispatched task {task_id} to {task_spec.get('target_agent_alias')}.")
            return task_id
        else:
            error_msg = response.get("error", {}).get("message", "Unknown error during dispatch.")
            logger.error(f"MCPServer: Failed to dispatch task {task_id}: {error_msg}")
            raise Exception(f"Failed to dispatch task: {error_msg}")

    async def run_autonomous_iteration_cycle(self, level_ids_to_test: List[str], num_sessions_per_level: int = 3):
        """
        Runs a full autonomous iteration cycle.
        """
        logger.info("MCPServer: Starting Autonomous Iteration Workflow cycle.")
        report = await self.autonomous_iteration_workflow.run_iteration_cycle(level_ids_to_test, num_sessions_per_level)
        logger.info("MCPServer: Autonomous Iteration Workflow cycle completed.")
        return report

    async def resolve_design_conflict(self, proposals: List[Dict[str, Any]], target_element_id: str) -> Dict[str, Any]:
        """
        Receives design proposals and triggers the CreativeConflictResolver.
        """
        logger.info(f"MCPServer: Resolving design conflict for '{target_element_id}'.")
        # Convert dicts back to DesignProposal objects for the resolver
        proposal_objects = [DesignProposal(**p) for p in proposals]
        winning_proposal = await self.creative_conflict_resolver.resolve_conflicting_proposals(proposal_objects, target_element_id)
        
        if winning_proposal:
            logger.info(f"MCPServer: Conflict for '{target_element_id}' resolved. Winning proposal from {winning_proposal.agent_id}.")
            return {"status": "success", "winning_proposal": winning_proposal.__dict__}
        else:
            logger.warning(f"MCPServer: Conflict for '{target_element_id}' could not be automatically resolved.")
            return {"status": "failed", "message": "Conflict could not be automatically resolved."}

    async def compose_and_execute_tools(self, task_goal: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allows agents to request dynamic tool composition and execution.
        """
        logger.info(f"MCPServer: Composing and executing tools for goal: {task_goal}")
        try:
            composed_tool_result = await self.dynamic_tool_composer.compose_and_execute(task_goal, initial_state)
            logger.info(f"MCPServer: Tool composition and execution completed for goal: {task_goal}")
            return {"status": "success", "result": composed_tool_result}
        except Exception as e:
            logger.error(f"MCPServer: Error during tool composition and execution for goal '{task_goal}': {e}")
            return {"status": "failed", "message": str(e)}

    async def _post_mcp_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Helper method to post events back to the MCP server's /post_event endpoint.
        This acts as the mcp_event_notifier for the CreativeConflictResolver.
        """
        logger.info(f"MCPServer: Posting event to MCP: Type='{event_type}', Data='{event_data}'")
        # In a real scenario, this would make an HTTP request to the /post_event endpoint.
        # For now, we'll just log it.
        # You might want to use a dedicated client for this, e.g., self.mcp_client.post_event(...)
        # For this implementation, we'll simulate the effect or directly call the relevant StateManager method
        # if the event is meant to update a task graph.
        
        # If the event is related to a task, we should update the state manager.
        task_id = event_data.get("task_id")
        if task_id:
            # This is a simplified direct call, bypassing the API route for internal events.
            # In a more robust system, this might go through a local queue or a dedicated internal event bus.
            # For now, we assume the StateManager is directly accessible.
            # This requires the StateManager to be initialized and accessible within MCPServer.
            # This is a placeholder and needs proper integration with the FastAPI app's state.
            print(f"Simulating event post to StateManager for task {task_id}")
            # This part needs to be handled by the FastAPI app's state, not directly here.
            # The MCPServer class itself doesn't have direct access to app.state.
            # This method is called by CreativeConflictResolver, which is instantiated within MCPServer.
            # So, this needs to be a mechanism to send an event to the FastAPI app's /post_event endpoint.
            # For now, we'll just log it.
            pass # Placeholder for actual event posting logic

# FastAPI App Setup
app = FastAPI(
    title="MCP Server API",
    description="Master Control Program for Autonomous AI Agent Ecosystem",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    """
    Initializes StateManager, PromptRegistry, and registers mock agents on startup.
    """
    print("[INFO] MCP Server startup event triggered.")
    app.state.registered_agents = {} # Dictionary to store AgentInfo objects
    app.state.state_manager = StateManager(registered_agents=app.state.registered_agents) # Pass registered_agents to StateManager
    app.state.prompt_registry = PromptRegistry()

    # Instantiate and register actual agent instances
    mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:5000")
    
    # Instantiate UnityToolchainBridge and store it on app.state
    app.state.unity_bridge_instance = None # Initialize
    if "unity_bridge" in _toolchain_classes:
        try:
            # The UnityToolchainBridge expects an mcp_server_instance.
            # For now, passing None. This might need adjustment.
            app.state.unity_bridge_instance = _toolchain_classes["unity_bridge"](mcp_server_instance=None) 
            print("[INFO] UnityToolchainBridge initialized in startup_event and stored in app.state.")
        except Exception as e:
            print(f"[ERROR] Failed to initialize UnityToolchainBridge in startup_event: {e}")

    for agent_id, agent_class in _agent_classes.items():
        agent_specific_kwargs = {"agent_id": agent_id, "mcp_server_url": mcp_server_url}
        if agent_id == "level_architect":
            agent_specific_kwargs["unity_bridge"] = app.state.unity_bridge_instance # Pass the instance from app.state
            
        agent_instance = agent_class(**agent_specific_kwargs)
        app.state.registered_agents[agent_id] = agent_instance
        print(f"[INFO] Registered agent instance: {agent_id}")

    # Register Level Architect prompt
    level_architect_prompt_template = """System: You are a virtual environment architect specializing in residential spaces.
- Reconstruct layouts from reference images with ±2% dimensional accuracy
- Maintain architectural coherence across all scene elements
- Generate UV maps optimized for retro pixel art pipelines

User Input:
{{
  "reference_image": "{reference_image}",
  "style_constraints": "{style_constraints}",
  "interactive_elements": "{interactive_elements}"
}}
"""
    app.state.prompt_registry.register_prompt(
        prompt_name="level_architect_design_prompt",
        template=level_architect_prompt_template,
        required_variables=["reference_image", "style_constraints", "interactive_elements"],
        agent_type="level_architect"
    )
    print("[INFO] Registered 'level_architect_design_prompt' with PromptRegistry.")

    print("[INFO] MCP Server startup complete.")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# This block is for direct execution of the FastAPI app using Uvicorn.
# In a production setup (e.g., with Gunicorn), this block is not used.
if __name__ == "__main__":
    import uvicorn
    # Add the project root to sys.path to ensure 'src' can be found as a package
    # This is a common pattern for running uvicorn from within a sub-module
    # and ensuring imports relative to the project root work.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
        print(f"[INFO] Added {PROJECT_ROOT} to sys.path for module resolution.")

    print("[INFO] Starting Uvicorn development server...")
    uvicorn.run("src.mcp_server.server_core:app", host="0.0.0.0", port=5000, reload=True)