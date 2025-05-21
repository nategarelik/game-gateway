# src/systems/extensibility_integration.py
import logging
from typing import List, Dict, Any, Callable, Optional, Type
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# --- Conceptual: Plug-and-Play Tool Support ---

class AbstractToolInterface(ABC):
    """
    Abstract base class for any tool that can be registered with the system.
    Defines a common interface for tool execution and metadata.
    """
    def __init__(self, tool_id: str, name: str, version: str = "1.0.0"):
        self.tool_id = tool_id
        self.name = name
        self.version = version

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata about the tool (e.g., description, parameters, capabilities)."""
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes the tool with given parameters and context."""
        pass

class ToolRegistry:
    """
    Manages the registration and discovery of pluggable tools.
    This could be part of an agent, the MCP, or a dedicated service.
    """
    def __init__(self):
        self._tools: Dict[str, AbstractToolInterface] = {}
        logger.info("ToolRegistry initialized.")

    def register_tool(self, tool_instance: AbstractToolInterface) -> bool:
        """Registers a tool instance."""
        if not isinstance(tool_instance, AbstractToolInterface):
            logger.error(f"Attempted to register an object that is not an AbstractToolInterface: {tool_instance}")
            return False
        if tool_instance.tool_id in self._tools:
            logger.warning(f"Tool with ID '{tool_instance.tool_id}' ({tool_instance.name}) is already registered. Overwriting.")
        
        self._tools[tool_instance.tool_id] = tool_instance
        logger.info(f"Tool '{tool_instance.name}' (ID: {tool_instance.tool_id}, Version: {tool_instance.version}) registered successfully.")
        return True

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregisters a tool by its ID."""
        if tool_id in self._tools:
            tool_name = self._tools[tool_id].name
            del self._tools[tool_id]
            logger.info(f"Tool '{tool_name}' (ID: {tool_id}) unregistered.")
            return True
        logger.warning(f"Attempted to unregister non-existent tool with ID '{tool_id}'.")
        return False

    def get_tool(self, tool_id: str) -> Optional[AbstractToolInterface]:
        """Retrieves a tool instance by its ID."""
        tool = self._tools.get(tool_id)
        if not tool:
            logger.warning(f"Tool with ID '{tool_id}' not found in registry.")
        return tool

    def list_tools(self) -> List[Dict[str, Any]]:
        """Lists metadata of all registered tools."""
        return [tool.get_metadata() for tool in self._tools.values()]

    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any], execution_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Finds a tool by ID and executes it."""
        tool = self.get_tool(tool_id)
        if tool:
            logger.info(f"Executing tool '{tool.name}' (ID: {tool_id}) with params: {parameters}")
            try:
                result = await tool.execute(parameters, execution_context)
                logger.info(f"Tool '{tool.name}' execution completed. Result keys: {list(result.keys()) if result else 'None'}")
                return result
            except Exception as e:
                logger.error(f"Error executing tool '{tool.name}' (ID: {tool_id}): {e}", exc_info=True)
                return {"error": str(e), "tool_id": tool_id, "status": "execution_failed"}
        else:
            return {"error": f"Tool with ID '{tool_id}' not found.", "tool_id": tool_id, "status": "tool_not_found"}


# --- Conceptual: Custom Workflow Nodes for LangGraph (within MCP StateManager) ---
# This section is highly conceptual as it depends on the specifics of LangGraph
# and how it's integrated into the MCP's StateManager.

class LangGraphNodeParameter:
    """Describes a parameter for a custom LangGraph node."""
    def __init__(self, name: str, param_type: str, description: str, required: bool = True):
        self.name = name
        self.param_type = param_type # e.g., "string", "integer", "list[string]", "AgentState"
        self.description = description
        self.required = required

class CustomLangGraphNode(ABC):
    """
    Abstract base class for a custom node that can be integrated into a LangGraph workflow
    managed by the MCP's StateManager.
    """
    node_type: str = "AbstractCustomNode" # Unique type identifier for this node
    node_description: str = "An abstract custom node."
    
    def __init__(self, node_id: str, mcp_context: Any): # mcp_context provides access to MCP services
        self.node_id = node_id
        self.mcp_context = mcp_context # e.g., for accessing agents, tools, state

    @classmethod
    def get_input_schema(cls) -> List[LangGraphNodeParameter]:
        """Defines the expected input parameters for this node."""
        return []

    @classmethod
    def get_output_schema(cls) -> List[LangGraphNodeParameter]:
        """Defines the structure of the output this node will produce."""
        return []

    @abstractmethod
    async def process(self, inputs: Dict[str, Any], current_graph_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The core logic of the node.
        
        Args:
            inputs: A dictionary of input values conforming to get_input_schema().
            current_graph_state: The current state of the LangGraph execution.
            
        Returns:
            A dictionary of output values conforming to get_output_schema().
            This output will typically update the LangGraph state.
        """
        pass

class LangGraphWorkflowManager: # Conceptually part of MCP.StateManager
    """
    Manages the registration and execution of LangGraph workflows that can include custom nodes.
    This is a highly simplified placeholder.
    """
    def __init__(self, mcp_context: Any):
        self.mcp_context = mcp_context
        self.registered_node_types: Dict[str, Type[CustomLangGraphNode]] = {}
        self.active_workflows: Dict[str, Any] = {} # workflow_id -> LangGraph instance (conceptual)
        logger.info("LangGraphWorkflowManager (conceptual) initialized.")

    def register_custom_node_type(self, node_class: Type[CustomLangGraphNode]):
        if not issubclass(node_class, CustomLangGraphNode):
            logger.error(f"Cannot register {node_class.__name__}: not a subclass of CustomLangGraphNode.")
            return
        if node_class.node_type in self.registered_node_types:
            logger.warning(f"Custom LangGraph node type '{node_class.node_type}' already registered. Overwriting.")
        
        self.registered_node_types[node_class.node_type] = node_class
        logger.info(f"Registered custom LangGraph node type: '{node_class.node_type}' ({node_class.node_description})")

    # Other methods would include:
    # - define_workflow(workflow_definition: Dict) -> str (workflow_id)
    # - run_workflow(workflow_id: str, initial_state: Dict) -> Dict (final_state)
    # - _instantiate_node(node_type: str, node_id: str) -> CustomLangGraphNode
    # These would involve interacting with the actual LangGraph library.

    def get_available_node_types(self) -> List[Dict[str, Any]]:
        """Lists available custom node types for workflow definition."""
        node_list = []
        for nt, nc in self.registered_node_types.items():
            node_list.append({
                "node_type": nt,
                "description": nc.node_description,
                "input_schema": [p.__dict__ for p in nc.get_input_schema()],
                "output_schema": [p.__dict__ for p in nc.get_output_schema()]
            })
        return node_list


# --- Example Usage ---

# Example Tool Implementation
class MockImageResizerTool(AbstractToolInterface):
    def __init__(self):
        super().__init__(tool_id="image_resizer_v1", name="Mock Image Resizer", version="1.0.1")

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "version": self.version,
            "description": "Resizes an image to target dimensions (mock).",
            "capabilities": ["image_manipulation", "resize"],
            "parameters": [
                {"name": "source_image_id", "type": "string", "required": True},
                {"name": "width", "type": "integer", "required": True},
                {"name": "height", "type": "integer", "required": True},
                {"name": "quality", "type": "integer", "required": False, "default": 90}
            ]
        }

    async def execute(self, parameters: Dict[str, Any], execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        source_id = parameters.get("source_image_id")
        width = parameters.get("width")
        height = parameters.get("height")
        if not all([source_id, width, height]):
            return {"error": "Missing required parameters (source_image_id, width, height).", "status": "parameter_error"}
        
        # Simulate resizing
        await asyncio.sleep(0.2)
        resized_image_id = f"resized_{source_id}_{width}x{height}"
        logger.info(f"MockImageResizerTool: Resized '{source_id}' to {width}x{height}. New ID: '{resized_image_id}'.")
        return {"status": "success", "resized_image_id": resized_image_id, "new_dimensions": [width, height]}

# Example Custom LangGraph Node
class AgentTaskDispatchNode(CustomLangGraphNode):
    node_type: str = "AgentTaskDispatchNode"
    node_description: str = "Dispatches a task to a specified agent via MCP and awaits its result."

    @classmethod
    def get_input_schema(cls) -> List[LangGraphNodeParameter]:
        return [
            LangGraphNodeParameter("target_agent_id", "string", "ID of the agent to dispatch the task to."),
            LangGraphNodeParameter("task_definition", "dict", "Full task definition payload for the agent."),
            LangGraphNodeParameter("timeout_seconds", "integer", "Timeout for awaiting task completion.", required=False)
        ]

    @classmethod
    def get_output_schema(cls) -> List[LangGraphNodeParameter]:
        return [
            LangGraphNodeParameter("task_id", "string", "The ID of the dispatched MCP task."),
            LangGraphNodeParameter("task_status", "string", "Final status of the task (e.g., completed, failed)."),
            LangGraphNodeParameter("task_result", "dict", "Result payload from the completed task.")
        ]

    async def process(self, inputs: Dict[str, Any], current_graph_state: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = inputs.get("target_agent_id")
        task_def = inputs.get("task_definition")
        # Conceptual: Use self.mcp_context to dispatch task and await result
        logger.info(f"AgentTaskDispatchNode ({self.node_id}): Conceptually dispatching task to agent '{agent_id}': {task_def}")
        # mcp_task_id = await self.mcp_context.dispatch_agent_task(agent_id, task_def)
        # task_result_payload = await self.mcp_context.await_task_completion(mcp_task_id, timeout=inputs.get("timeout_seconds", 60))
        
        # Mocking the interaction
        await asyncio.sleep(0.3)
        mock_task_id = f"mcp_task_{agent_id}_{int(time.time())}"
        mock_result = {"data": f"Mock result from agent {agent_id} for task {mock_task_id}"}
        mock_status = "completed"
        
        logger.info(f"AgentTaskDispatchNode ({self.node_id}): Mock task '{mock_task_id}' {mock_status}.")
        return {"task_id": mock_task_id, "task_status": mock_status, "task_result": mock_result}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def tool_registry_demo():
        print("\n--- Tool Registry Demo ---")
        registry = ToolRegistry()
        resizer_tool = MockImageResizerTool()
        registry.register_tool(resizer_tool)

        print("Available tools:", registry.list_tools())
        
        result = await registry.execute_tool(
            "image_resizer_v1", 
            {"source_image_id": "original_pic.png", "width": 100, "height": 100}
        )
        print("Execution result:", result)
        
        result_not_found = await registry.execute_tool("non_existent_tool", {})
        print("Execution result (not found):", result_not_found)

    async def lang_graph_manager_demo():
        print("\n--- LangGraph Workflow Manager Demo (Conceptual) ---")
        # Mock MCP context that custom nodes might use
        class MockMCPContext:
            async def dispatch_agent_task(self, agent_id, task_def): pass
            async def await_task_completion(self, task_id, timeout): pass
        
        mcp_ctx = MockMCPContext()
        lg_manager = LangGraphWorkflowManager(mcp_context=mcp_ctx)
        lg_manager.register_custom_node_type(AgentTaskDispatchNode)
        
        print("Available custom node types for LangGraph:", lg_manager.get_available_node_types())
        
        # Conceptual instantiation and execution of a node (would be part of a graph run)
        dispatch_node_instance = AgentTaskDispatchNode(node_id="node123", mcp_context=mcp_ctx)
        node_inputs = {
            "target_agent_id": "PixelForge_01",
            "task_definition": {"type": "generate_image", "prompt": "A cool dragon"}
        }
        node_output = await dispatch_node_instance.process(node_inputs, current_graph_state={})
        print("Conceptual node output:", node_output)

    async def main_demo():
        await tool_registry_demo()
        await lang_graph_manager_demo()

    asyncio.run(main_demo())