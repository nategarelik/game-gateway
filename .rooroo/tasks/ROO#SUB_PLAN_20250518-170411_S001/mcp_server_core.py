print("[DEBUG] mcp_server_core.py execution started...")
import sys
import os
import re
from typing import List, Dict, Any
import json # For direct JSON manipulation if needed

# --- Flask Import ---
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("[ERROR] Flask library not found. Please install it: pip install Flask")
    sys.exit(1)

# --- Path Setup ---
# Dynamically add project subdirectories to sys.path to locate agent and toolchain modules.
_current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming mcp_server_core.py is at .rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py
# Workspace root is three levels up from S001 directory.
_workspace_root = os.path.abspath(os.path.join(_current_script_dir, '..', '..', '..'))

_paths_to_add = [
    # Directory for LevelArchitectAgent
    os.path.join(_workspace_root, ".rooroo", "tasks", "ROO#SUB_PLAN_20250518-170411_S002"),
    # Directory for PixelForgeAgent
    os.path.join(_workspace_root, ".rooroo", "tasks", "ROO#SUB_PLAN_20250518-170411_S003"),
    # Directory for DocumentationSentinelAgent
    os.path.join(_workspace_root, ".rooroo", "tasks", "ROO#SUB_PLAN_20250518-170411_S004", "artifacts"),
    # Directory for Toolchain Integrations (Muse, RetroDiffusion)
    os.path.join(_workspace_root, ".rooroo", "tasks", "ROO#SUB_PLAN_20250518-170411_S005")
]

for p in _paths_to_add:
    if os.path.isdir(p):
        if p not in sys.path:
            sys.path.insert(0, p)
            print(f"[INFO] Added to sys.path: {p}")
    else:
        print(f"[Warning] Path not found, not adding to sys.path: {p}")

# --- Agent and Toolchain Imports (after sys.path setup) ---
# These imports rely on the sys.path modifications above.
# Actual class names within these modules must match.

# Import MCPClient from its new dedicated file
try:
    from mcp_client import MCPClient
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
    from muse_integration import MuseToolchainBridge
    _toolchain_classes["muse_bridge"] = MuseToolchainBridge
    print("[INFO] Successfully imported MuseToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import MuseToolchainBridge: {e}. Muse toolchain will not be available.")

try:
    from retro_diffusion_integration import RetroDiffusionToolchainBridge
    _toolchain_classes["retro_diffusion_bridge"] = RetroDiffusionToolchainBridge
    print("[INFO] Successfully imported RetroDiffusionToolchainBridge.")
except ImportError as e:
    print(f"[Warning] Failed to import RetroDiffusionToolchainBridge: {e}. Retro Diffusion toolchain will not be available.")


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
    def __init__(self):
        self.workflow = StateGraph(GameDevState)
        self.prompt_engine = PromptRegistry()
        self.agents: Dict[str, Agent] = {} # Stores instantiated agents

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
        
        print("MCPServer core initialized.")

        # Instantiate Agents
        for agent_id, agent_class_constructor in _agent_classes.items():
            try:
                # Assuming Agent base class constructor: Agent(role, prompt_template)
                # Concrete agent classes must inherit from Agent or implement handle_direct_request.
                # Pass empty prompt_template as it's not used for direct API calls.
                self.agents[agent_id] = agent_class_constructor(role=agent_id, prompt_template=[])
                print(f"[INFO] Agent '{agent_id}' instantiated.")
            except Exception as e:
                print(f"[ERROR] Failed to instantiate agent '{agent_id}': {e}")
        
        print("MCPServer agent instantiation complete.")


    def register_agent(self, agent: Agent):
        if not isinstance(agent, Agent):
            raise ValueError("Invalid agent type. Agent must be an instance of the Agent class.")
        self.workflow.add_node(agent.role, agent.execute)
        self.prompt_engine.add_template(agent.role, agent.prompt_template)
        print(f"Agent '{agent.role}' registered with MCPServer workflow.")

    def add_workflow_transition(self, from_role: str, to_role: str, condition=None):
        self.workflow.add_edge(from_role, to_role, condition)
        print(f"Workflow transition added from '{from_role}' to '{to_role}'.")

    def get_resolved_prompt_for_agent(self, role: str, variables: Dict[str, Any]) -> str | None:
        template = self.prompt_engine.get_template(role)
        if template is None:
            print(f"No prompt template found for agent role: {role}")
            return None
        resolved_prompt = self.prompt_engine.resolve_prompt(template, variables)
        print(f"Prompt resolved for agent role: {role}")
        return resolved_prompt

    def execute_workflow(self, initial_state: GameDevState, start_agent_role: str) -> GameDevState:
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
        if self.muse_bridge is None:
            print("[ERROR] MuseToolchainBridge is not available.")
            raise ConnectionError("MuseToolchainBridge not available.")
        print(f"MCPServer: Relaying command to Muse: Type='{command_type}', Agent='{agent_id}'")
        # Assuming bridge's send_command is synchronous or handles async internally for API.
        return self.muse_bridge.send_command(command_type, command_text, agent_id)

    def generate_retro_asset(self, prompt: str, parameters: Dict[str, Any] = None, agent_id: str = None):
        if self.retro_diffusion_bridge is None:
            print("[ERROR] RetroDiffusionToolchainBridge is not available.")
            raise ConnectionError("RetroDiffusionToolchainBridge not available.")
        print(f"MCPServer: Relaying asset generation request to Retro Diffusion: Prompt='{prompt}', Agent='{agent_id}'")
        # Assuming bridge's generate_asset is synchronous or handles async internally.
        return self.retro_diffusion_bridge.generate_asset(prompt, parameters, agent_id)

    # --- New API Request Handler ---
    def handle_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
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

# --- Flask Application Setup ---
app = Flask(__name__)
mcp_server_instance = None

def get_mcp_server_instance():
    global mcp_server_instance
    if mcp_server_instance is None:
        print("[INFO] Initializing MCPServer instance for Flask app...")
        mcp_server_instance = MCPServer()
        print("[INFO] MCPServer instance created.")
    return mcp_server_instance

@app.route('/execute_agent', methods=['POST'])
def execute_agent_route():
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

    except Exception as e: # Fallback for errors during server init or unexpected route issues
        import traceback
        print(f"[CRITICAL ROUTE ERROR] Unhandled exception in /execute_agent for task {task_id_from_req}: {e}\n{traceback.format_exc()}")
        return jsonify({
            "task_id": task_id_from_req, "status": "failed", "result": None,
            "error": {"code": "INTERNAL_SERVER_ERROR", "message": f"A critical error occurred in the API endpoint: {str(e)}"}
        }), 500

if __name__ == '__main__':
    # Ensure MCPServer is initialized once before starting app if not done by first request
    # get_mcp_server_instance() # Pre-initialize if desired, or let first request do it.

    host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_SERVER_PORT", 5001)) # Changed port to 5001 to avoid common conflicts
    
    print(f"[INFO] Starting MCP Server API on http://{host}:{port}")
    try:
        app.run(host=host, port=port, debug=True) # debug=True for development, consider False for production
    except Exception as e:
        print(f"[FATAL] Could not start Flask server: {e}")
        sys.exit(1)