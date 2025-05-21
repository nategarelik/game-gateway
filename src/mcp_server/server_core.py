print("[DEBUG] mcp_server_core.py execution started...")
import sys
import os
import re
import random # Added for AutonomousIterationWorkflow
import time # Added for AutonomousIterationWorkflow
from typing import List, Dict, Any, Optional, Callable # Added Optional, Callable for protocols
import json # For direct JSON manipulation if needed

# --- Flask Import ---
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("[ERROR] Flask library not found. Please install it: pip install Flask")
    sys.exit(1)

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
    from level_architect_agent import LevelArchitectAgent
    _agent_classes["level_architect"] = LevelArchitectAgent
    print("[INFO] Successfully imported LevelArchitectAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import LevelArchitectAgent: {e}. This agent will not be available.")

try:
    from code_weaver_agent import CodeWeaverAgent
    _agent_classes["code_weaver"] = CodeWeaverAgent
    print("[INFO] Successfully imported CodeWeaverAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import CodeWeaverAgent: {e}. This agent will not be available.")

try:
    from pixel_forge_agent import PixelForgeAgent
    _agent_classes["pixel_forge"] = PixelForgeAgent
    print("[INFO] Successfully imported PixelForgeAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import PixelForgeAgent: {e}. This agent will not be available.")

try:
    from documentation_sentinel_agent import DocumentationSentinelAgent
    _agent_classes["documentation_sentinel"] = DocumentationSentinelAgent
    print("[INFO] Successfully imported DocumentationSentinelAgent.")
except ImportError as e:
    print(f"[Warning] Failed to import DocumentationSentinelAgent: {e}. This agent will not be available.")

try:
    from muse_bridge import MuseToolchainBridge
    _toolchain_classes["muse_bridge"] = MuseToolchainBridge
    print("[INFO] Successfully imported MuseToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import MuseToolchainBridge: {e}. Muse toolchain will not be available.")

try:
    from retro_diffusion_bridge import RetroDiffusionToolchainBridge
    _toolchain_classes["retro_diffusion_bridge"] = RetroDiffusionToolchainBridge
    print("[INFO] Successfully imported RetroDiffusionToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import RetroDiffusionToolchainBridge: {e}. Retro Diffusion toolchain will not be available.")

try:
    from unity_bridge import UnityToolchainBridge
    _toolchain_classes["unity_bridge"] = UnityToolchainBridge
    print("[INFO] Successfully imported UnityToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import UnityToolchainBridge: {e}. Unity toolchain will not be available.")

# Import KnowledgeManagementSystem
from systems.knowledge_management_system import KnowledgeManagementSystem
# Import AutonomousIterationWorkflow
from workflows.autonomous_iteration import AutonomousIterationWorkflow
# Import Emergent Behavior Protocols
from protocols.emergent_behavior_protocols import CreativeConflictResolver, DynamicToolComposer, Tool, DesignProposal
# Import Advanced Collaboration Protocols
from protocols.advanced_collaboration_protocols import CollaborationManager, AgentEventBus, AgentProfile, TaskAssistanceRequest, AgentEvent
# Import Extensibility and Integration components
from systems.extensibility_integration import ToolRegistry, AbstractToolInterface, MockImageResizerTool


# --- Existing GameDevState, Agent, PromptRegistry, StateGraph ---
class GameDevState:
    project_metadata: Dict[str, Any]
    assets: Dict[str, Any]
    current_tasks: List[str]
    completed_tasks: List[str]
    agent_states: Dict[str, Any]

    def __init__(self, project_metadata: Dict[str, Any] = None, assets: Dict[str, Any] = None,
                 current_tasks: List[str] = None, completed_tasks: List[str] = None,
                 agent_states: Dict[str, Any] = None):
        self.project_metadata = project_metadata if project_metadata is not None else {}
        self.assets = assets if assets is not None else {}
        self.current_tasks = current_tasks if current_tasks is not None else []
        self.completed_tasks = completed_tasks if completed_tasks is not None else []
        self.agent_states = agent_states if agent_states is not None else {}

class Agent:
    def __init__(self, role: str, prompt_template: List[str]):
        self.role = role
        self.prompt_template = prompt_template

    def execute(self, state: GameDevState) -> GameDevState:
        print(f"Agent {self.role} is executing with current state.")
        return state

    # Expected method for direct API calls
    def handle_direct_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # This method should be implemented by concrete agent classes.
        # It processes 'parameters' and returns a result dictionary.
        print(f"[Warning] Agent {self.role} handle_direct_request not implemented. Returning parameters.")
        return {"status": "default_handler", "received_parameters": parameters}


class PromptRegistry:
    def __init__(self):
        self.templates: Dict[str, List[str]] = {}

    def add_template(self, role: str, template: List[str]):
        self.templates[role] = template

    def get_template(self, role: str) -> List[str] | None:
        return self.templates.get(role)

    def resolve_prompt(self, template: List[str], variables: Dict[str, Any]) -> str:
        resolved_lines = []
        for line in template:
            placeholders = re.findall(r'\{\{(\w+)\}\}', line)
            if not placeholders:
                resolved_lines.append(line)
                continue
            if all(var_name in variables for var_name in placeholders):
                resolved_line = line
                for var_name in placeholders:
                    resolved_line = resolved_line.replace(f'{{{{{var_name}}}}}', str(variables[var_name]))
                resolved_lines.append(resolved_line)
        return "\n".join(resolved_lines)

class StateGraph:
    def __init__(self, state_schema):
        self.nodes = {}
        self.edges = {}
        self.state_schema = state_schema
        print(f"StateGraph initialized with schema: {state_schema.__name__}")

    def add_node(self, name: str, action):
        self.nodes[name] = action
        print(f"Node '{name}' added to StateGraph.")

    def add_edge(self, start_node: str, end_node: str, condition=None):
        if start_node not in self.edges:
            self.edges[start_node] = []
        self.edges[start_node].append({"to": end_node, "condition": condition})
        print(f"Edge from '{start_node}' to '{end_node}' added.")

    def run(self, initial_state: GameDevState, start_node_name: str):
        print(f"StateGraph run initiated with initial state at node '{start_node_name}'.")
        current_node_name = start_node_name
        current_state = initial_state
        while current_node_name in self.nodes:
            action = self.nodes[current_node_name]
            print(f"Executing node: {current_node_name}")
            current_state = action(current_state)
            if current_node_name in self.edges and self.edges[current_node_name]:
                next_edge = self.edges[current_node_name][0]
                print(f"Transitioning from {current_node_name} to {next_edge['to']}")
                current_node_name = next_edge['to']
            else:
                print(f"No outgoing edge from {current_node_name} or node not found. Workflow ends.")
                break
        print("StateGraph run finished.")
        return current_state

# --- MCPServer Class (Modified) ---
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
        self.workflow = StateGraph(GameDevState)
        self.prompt_engine = PromptRegistry()
        self.agents: Dict[str, Agent] = {} # Stores instantiated agents
        self.mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:5000") # Added for agent instantiation
        self.knowledge_management_system = KnowledgeManagementSystem(mcp_server_url=self.mcp_server_url) # Instantiate KMS
        self.autonomous_iteration_workflow = AutonomousIterationWorkflow(mcp_task_dispatcher=self._dispatch_mcp_task) # Instantiate AIW
        self.creative_conflict_resolver = CreativeConflictResolver(mcp_event_notifier=self._post_mcp_event) # Instantiate CCR
        self.agent_event_bus = AgentEventBus() # Instantiate AgentEventBus
        self.collaboration_manager = CollaborationManager(mcp_interface=self) # Instantiate CollaborationManager, pass self as MCP interface
        
        # Prepare tools for DynamicToolComposer
        available_tools = []
        # Add toolchain bridges as tools
        if self.muse_bridge:
            available_tools.append(Tool("muse_toolchain", "Muse Toolchain", ["conceptual_generation", "text_generation"], {}))
        if self.retro_diffusion_bridge:
            available_tools.append(Tool("retro_diffusion_toolchain", "Retro Diffusion Toolchain", ["image_generation", "texture_generation"], {}))
        if self.unity_bridge:
            available_tools.append(Tool("unity_toolchain", "Unity Toolchain", ["scene_manipulation", "script_execution", "asset_placement"], {}))
        
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

        # Instantiate Toolchain Bridges
        if "muse_bridge" in _toolchain_classes:
            self.muse_bridge = _toolchain_classes["muse_bridge"](self)
            print("[INFO] MuseToolchainBridge initialized.")
        else:
            self.muse_bridge = None
            print("[Warning] MuseToolchainBridge not available.")

        if "retro_diffusion_bridge" in _toolchain_classes:
            self.retro_diffusion_bridge = _toolchain_classes["retro_diffusion_bridge"](self)
            print("[INFO] RetroDiffusionToolchainBridge initialized.")
        else:
            self.retro_diffusion_bridge = None
            print("[Warning] RetroDiffusionToolchainBridge not available.")

        if "unity_bridge" in _toolchain_classes:
            self.unity_bridge = _toolchain_classes["unity_bridge"](self)
            print("[INFO] UnityToolchainBridge initialized.")
        else:
            self.unity_bridge = None
            print("[Warning] UnityToolchainBridge not available.")
        
        print("MCPServer core initialized.")

        # Instantiate Agents
        for agent_id, agent_class_constructor in _agent_classes.items():
            try:
                # Pass the mcp_server_url and unity_bridge to agents that need it
                if agent_id in ["level_architect", "code_weaver", "pixel_forge"]:
                    self.agents[agent_id] = agent_class_constructor(
                        agent_id=agent_id,
                        mcp_server_url=self.mcp_server_url,
                        unity_bridge=self.unity_bridge # Pass the unity_bridge instance
                    )
                else:
                    # For other agents, assume the existing constructor signature
                    self.agents[agent_id] = agent_class_constructor(role=agent_id, prompt_template=[])
                print(f"[INFO] Agent '{agent_id}' instantiated.")
            except Exception as e:
                print(f"[ERROR] Failed to instantiate agent '{agent_id}': {e}")
        
        print("MCPServer agent instantiation complete.")

        # Register agents with CollaborationManager
        for agent_id, agent_instance in self.agents.items():
            self.collaboration_manager.register_agent(agent_id, agent_instance.capabilities)
        logger.info("Agents registered with CollaborationManager.")

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


    def register_agent(self, agent: Agent):
        """
        Registers an agent with the MCPServer.

        Adds the agent's execution method as a node in the workflow and
        its prompt template to the prompt registry.

        Args:
            agent (Agent): The agent instance to register.

        Raises:
            ValueError: If the provided agent is not an instance of the Agent class.
        """
        if not isinstance(agent, Agent):
            raise ValueError("Invalid agent type. Agent must be an instance of the Agent class.")
        self.workflow.add_node(agent.role, agent.execute)
        self.prompt_engine.add_template(agent.role, agent.prompt_template)
        print(f"Agent '{agent.role}' registered with MCPServer workflow.")

    def add_workflow_transition(self, from_role: str, to_role: str, condition=None):
        """
        Adds a transition between two agent roles in the workflow.

        Args:
            from_role (str): The role of the agent from which the transition originates.
            to_role (str): The role of the agent to which the transition leads.
            condition (Optional[Callable]): A condition that must be met for the
                                           transition to occur. Defaults to None.
        """
        self.workflow.add_edge(from_role, to_role, condition)
        print(f"Workflow transition added from '{from_role}' to '{to_role}'.")

    def get_resolved_prompt_for_agent(self, role: str, variables: Dict[str, Any]) -> str | None:
        """
        Resolves a prompt template for a given agent role using provided variables.

        Args:
            role (str): The role of the agent for whom the prompt is being resolved.
            variables (Dict[str, Any]): A dictionary of variables to substitute
                                       into the prompt template.

        Returns:
            Optional[str]: The resolved prompt string, or None if no template
                           is found for the given role.
        """
        template = self.prompt_engine.get_template(role)
        if template is None:
            print(f"No prompt template found for agent role: {role}")
            return None
        resolved_prompt = self.prompt_engine.resolve_prompt(template, variables)
        print(f"Prompt resolved for agent role: {role}")
        return resolved_prompt

    def execute_workflow(self, initial_state: GameDevState, start_agent_role: str) -> GameDevState:
        """
        Executes the defined workflow starting from a specific agent role.

        Args:
            initial_state (GameDevState): The initial state for the workflow.
            start_agent_role (str): The role of the agent where the workflow execution begins.

        Returns:
            GameDevState: The final state after the workflow execution completes.

        Raises:
            ValueError: If the initial_state is not a GameDevState instance or
                        if the start_agent_role is not registered in the workflow.
        """
        if not isinstance(initial_state, GameDevState):
            raise ValueError("Initial state must be an instance of GameDevState.")
        if start_agent_role not in self.workflow.nodes:
            raise ValueError(f"Start agent role '{start_agent_role}' not registered in the workflow.")
        print(f"Executing MCP workflow starting with agent '{start_agent_role}'.")
        final_state = self.workflow.run(initial_state, start_node_name=start_agent_role)
        print("MCP workflow execution finished.")
        return final_state

    # --- Toolchain Integration Methods (Existing) ---
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
            if agent_id_req in self.agents:
                agent_instance = self.agents[agent_id_req]
                if hasattr(agent_instance, 'handle_direct_request') and callable(agent_instance.handle_direct_request):
                    # Call the agent's specific handler for direct requests
                    result_data = agent_instance.handle_direct_request(parameters)
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
                if self.unity_bridge is None: raise ConnectionError("Unity toolchain not available.")
                command_type = parameters.get("command_type")
                command_args = parameters.get("arguments", {})
                if command_type is None:
                    raise ValueError("Missing 'command_type' for Unity toolchain.")
                unity_response = self.unity_bridge.send_command(command_type, command_args)
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
        response = await self.handle_api_request(request_data)
        
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
        logger.info(f"MCPServer: Request for dynamic tool composition for goal: '{task_goal}'.")
        try:
            results = await self.dynamic_tool_composer.compose_and_execute_tool_sequence(task_goal, initial_state)
            logger.info(f"MCPServer: Dynamic tool composition completed for goal '{task_goal}'.")
            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"MCPServer: Dynamic tool composition failed for goal '{task_goal}': {e}")
            return {"status": "failed", "message": f"Dynamic tool composition failed: {str(e)}"}

    async def _post_mcp_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Internal method to post events to the MCP (e.g., for conflict resolution notifications).
        This would typically send to a dedicated event endpoint or log.
        """
        logger.info(f"[MCP Event] Type: {event_type}, Data: {event_data}")
        # In a real system, this would be sent to a message queue or a dedicated event API.
        # For now, it just logs.

    # --- Collaboration Manager Interface Methods ---
    async def register_agent_with_collab_manager(self, agent_id: str, capabilities: List[str]):
        """Registers an agent with the CollaborationManager."""
        self.collaboration_manager.register_agent(agent_id, capabilities)

    async def update_agent_status_in_collab_manager(self, agent_id: str, status: str, current_task_id: Optional[str] = None):
        """Updates an agent's status in the CollaborationManager."""
        self.collaboration_manager.update_agent_status(agent_id, status, current_task_id)

    async def request_agent_assistance(self, requesting_agent_id: str, original_task_id: str, required_capability: str, task_details: Dict[str, Any]) -> Optional[str]:
        """Handles an agent's request for assistance."""
        return await self.collaboration_manager.request_assistance(requesting_agent_id, original_task_id, required_capability, task_details)

    async def update_assistance_request_status(self, request_id: str, status: str, result_data: Optional[Dict] = None):
        """Updates the status of an assistance request."""
        self.collaboration_manager.update_assistance_request_status(request_id, status, result_data)

    # --- Agent Event Bus Interface Methods ---
    async def publish_agent_event(self, source_agent_id: str, event_type: str, data: Dict[str, Any]):
        """Publishes an event to the AgentEventBus."""
        await self.agent_event_bus.publish_event(source_agent_id, event_type, data)

    async def subscribe_to_agent_event(self, event_type: str, callback: Callable):
        """Subscribes a callback to an event type on the AgentEventBus."""
        await self.agent_event_bus.subscribe(event_type, callback)

    async def unsubscribe_from_agent_event(self, event_type: str, callback: Callable):
        """Unsubscribes a callback from an event type on the AgentEventBus."""
        await self.agent_event_bus.unsubscribe(event_type, callback)

    # --- Tool Registry Interface Methods ---
    async def register_external_tool(self, tool_instance: AbstractToolInterface) -> bool:
        """Registers an external tool with the ToolRegistry."""
        return self.tool_registry.register_tool(tool_instance)

    async def unregister_external_tool(self, tool_id: str) -> bool:
        """Unregisters an external tool from the ToolRegistry."""
        return self.tool_registry.unregister_tool(tool_id)

    async def list_external_tools(self) -> List[Dict[str, Any]]:
        """Lists metadata of all registered external tools."""
        return self.tool_registry.list_tools()

    async def execute_external_tool(self, tool_id: str, parameters: Dict[str, Any], execution_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Executes a registered external tool."""
        return await self.tool_registry.execute_tool(tool_id, parameters, execution_context)


# --- Flask Application Setup ---
app = Flask(__name__)
mcp_server_instance = None

def get_mcp_server_instance():
    """
    Retrieves or initializes the global MCPServer instance.

    This function implements a singleton pattern for the MCPServer instance
    to ensure it's created only once and shared across Flask requests.

    Returns:
        MCPServer: The singleton MCPServer instance.
    """
    global mcp_server_instance
    if mcp_server_instance is None:
        print("[INFO] Initializing MCPServer instance for Flask app...")
        mcp_server_instance = MCPServer()
        print("[INFO] MCPServer instance created.")
    return mcp_server_instance

@app.route('/execute_agent', methods=['POST'])
def execute_agent_route():
    """
    Flask route to handle agent execution requests.

    Receives a JSON POST request, validates it, and passes it to the
    MCPServer's `handle_api_request` method for processing. Returns a
    JSON response with the outcome.

    Returns:
        Tuple[Response, int]: A Flask JSON response and an HTTP status code.
    """
    if not request.is_json:
        return jsonify({
            "task_id": "unknown_task", "status": "failed", "result": None,
            "error": {"code": "INVALID_REQUEST", "message": "Request content type must be application/json."}
        }), 400
    
    request_data = request.get_json()
    task_id_from_req = request_data.get("task_id", "unknown_task_in_request")

    try:
        server = get_mcp_server_instance()
        response_data = server.handle_api_request(request_data)
        
        http_status_code = 200
        if response_data.get("status") == "failed":
            error_code = response_data.get("error", {}).get("code")
            if error_code == "AGENT_NOT_FOUND": http_status_code = 404
            elif error_code in ["INVALID_REQUEST", "INVALID_PARAMETERS"]: http_status_code = 400
            else: http_status_code = 500 # EXECUTION_ERROR, TOOLCHAIN_CONNECTION_ERROR, AGENT_INTERFACE_ERROR etc.
        
        return jsonify(response_data), http_status_code
    except Exception as e:
        import traceback
        print(f"[CRITICAL ERROR] Unexpected error in execute_agent_route: {e}\n{traceback.format_exc()}")
        return jsonify({
            "task_id": task_id_from_req,
            "status": "failed",
            "result": None,
            "error": {"code": "SERVER_ERROR", "message": f"An unexpected server error occurred: {str(e)}"}
        }), 500

@app.route('/status', methods=['GET'])
def status_route():
    """
    Provides a simple status endpoint for the MCP server.
    """
    return jsonify({"status": "running", "message": "MCP Server is operational."}), 200

@app.route('/agents', methods=['GET'])
def list_agents_route():
    """
    Lists all registered agents and their capabilities.
    """
    server = get_mcp_server_instance()
    agent_info = {agent_id: agent.capabilities for agent_id, agent in server.agents.items()}
    return jsonify({"agents": agent_info}), 200

@app.route('/toolchains', methods=['GET'])
def list_toolchains_route():
    """
    Lists all available toolchains.
    """
    server = get_mcp_server_instance()
    toolchain_info = {}
    if server.muse_bridge:
        toolchain_info["muse"] = {"available": True}
    if server.retro_diffusion_bridge:
        toolchain_info["retro_diffusion"] = {"available": True}
    if server.unity_bridge:
        toolchain_info["unity"] = {"available": True}
    return jsonify({"toolchains": toolchain_info}), 200

if __name__ == '__main__':
    # This block is for direct execution of the server for testing/development.
    # In a production environment, it might be run via a WSGI server like Gunicorn.
    host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_SERVER_PORT", 5000))
    print(f"[INFO] Starting MCP Server on {host}:{port}...")
    # Initialize the server instance to ensure agents/toolchains are loaded at startup
    get_mcp_server_instance() 
    app.run(host=host, port=port, debug=True, use_reloader=False) # debug=True for development