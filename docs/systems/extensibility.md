# Extensibility and Integration Documentation

This document outlines conceptual mechanisms for extending the Autonomous AI Agent Ecosystem, focusing on Plug-and-Play Tool Support and the integration of Custom Workflow Nodes (e.g., for LangGraph) within the Master Control Program (MCP) or its associated services.

The core Python module for these conceptual systems is located at [`src/systems/extensibility_integration.py`](../../src/systems/extensibility_integration.py).

## Purpose

The primary objectives for these extensibility features are:
1.  **Plug-and-Play Tool Support:** To allow new tools or capabilities to be easily integrated into the ecosystem without requiring significant modifications to core agent or MCP logic. This is achieved through a `ToolRegistry` and a common `AbstractToolInterface`.
2.  **Custom Workflow Nodes:** To enable the definition and use of custom, reusable processing nodes within more complex workflows, such as those managed by a graph-based execution framework like LangGraph (conceptually managed by the MCP's `StateManager` or a `LangGraphWorkflowManager`).

## Core Components and Concepts

### Plug-and-Play Tool Support

#### 1. `AbstractToolInterface` (ABC)
   *   **Purpose:** Defines a standard contract for all pluggable tools.
   *   **Key Methods:**
        *   `__init__(self, tool_id: str, name: str, version: str = "1.0.0")`
        *   `get_metadata(self) -> Dict[str, Any]` (abstract): Returns a dictionary describing the tool (ID, name, version, description, capabilities, parameters schema).
        *   `async execute(self, parameters: Dict[str, Any], execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]` (abstract): Executes the tool's logic with given parameters and returns a result dictionary.

#### 2. `ToolRegistry`
   *   **Purpose:** Manages the lifecycle of pluggable tools.
   *   **Methods:**
        *   `register_tool(self, tool_instance: AbstractToolInterface) -> bool`: Adds a tool instance to the registry.
        *   `unregister_tool(self, tool_id: str) -> bool`: Removes a tool.
        *   `get_tool(self, tool_id: str) -> Optional[AbstractToolInterface]`: Retrieves a tool by its ID.
        *   `list_tools(self) -> List[Dict[str, Any]]`: Returns metadata for all registered tools.
        *   `async execute_tool(self, tool_id: str, parameters: Dict[str, Any], ...) -> Optional[Dict[str, Any]]`: Finds and executes a registered tool.

   **Example Tool (`MockImageResizerTool`):**
   The module provides an example `MockImageResizerTool` that inherits from `AbstractToolInterface` and implements `get_metadata` and `execute` for a conceptual image resizing operation.

### Custom Workflow Nodes (Conceptual for LangGraph)

This part is highly conceptual and outlines how custom nodes might be defined for integration with a framework like LangGraph, potentially managed by the MCP.

#### 1. `LangGraphNodeParameter`
   *   A simple data class to describe an input or output parameter for a custom node (name, type, description, required).

#### 2. `CustomLangGraphNode` (ABC)
   *   **Purpose:** Abstract base class for custom nodes in a LangGraph workflow.
   *   **Class Attributes:**
        *   `node_type: str`: A unique string identifier for the node type.
        *   `node_description: str`: A human-readable description.
   *   **Initialization:** `__init__(self, node_id: str, mcp_context: Any)`: Takes a unique instance ID and a conceptual `mcp_context` (for accessing MCP services like agent tasking).
   *   **Class Methods (for schema definition):**
        *   `get_input_schema(cls) -> List[LangGraphNodeParameter]`
        *   `get_output_schema(cls) -> List[LangGraphNodeParameter]`
   *   **Abstract Method:**
        *   `async process(self, inputs: Dict[str, Any], current_graph_state: Dict[str, Any]) -> Dict[str, Any]`: Contains the core logic of the node. It receives inputs, can access the current graph state, and returns outputs that will update the graph state.

#### 3. `LangGraphWorkflowManager` (Conceptual)
   *   **Purpose:** A placeholder for a component (likely within the MCP's `StateManager`) that would manage the definition, registration, and execution of LangGraph workflows incorporating custom nodes.
   *   **Methods (Conceptual):**
        *   `register_custom_node_type(self, node_class: Type[CustomLangGraphNode])`: Adds a new custom node class to the manager's known types.
        *   `get_available_node_types(self) -> List[Dict[str, Any]]`: Lists all registered custom node types with their schemas.
        *   Other methods would handle workflow definition (e.g., from a JSON/YAML spec) and execution, interacting with the LangGraph library.

   **Example Node (`AgentTaskDispatchNode`):**
   The module provides an example `AgentTaskDispatchNode` that inherits from `CustomLangGraphNode`. Its `process` method conceptually dispatches a task to an agent via the `mcp_context` and awaits its result, mocking the interaction.

:start_line:65
-------
## Integration with MCP Server

The `Extensibility and Integration` components, particularly the `ToolRegistry`, are integrated directly into the `MCPServer`. This allows for centralized management and exposure of pluggable tools.

### Tool Registry Management by MCP

The `MCPServer` instantiates a `ToolRegistry` and registers example external tools (like `MockImageResizerTool`) during its initialization. It also exposes methods to interact with this registry via its API.

*   **Registering External Tools:**
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"tool_registry"`
    *   **`parameters`**:
        *   `command_type`: `"register_external_tool"`
        *   `tool_instance` (object): An instance of a class implementing `AbstractToolInterface`. (Note: In a real API, this would likely be a serialized representation of the tool's metadata and a reference to its implementation, or a dynamic loading mechanism).
*   **Unregistering External Tools:**
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"tool_registry"`
    *   **`parameters`**:
        *   `command_type`: `"unregister_external_tool"`
        *   `tool_id` (string): The ID of the tool to unregister.
*   **Listing External Tools:**
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"tool_registry"`
    *   **`parameters`**:
        *   `command_type`: `"list_external_tools"`
*   **Executing External Tools:**
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"tool_registry"`
    *   **`parameters`**:
        *   `command_type`: `"execute_external_tool"`
        *   `tool_id` (string): The ID of the tool to execute.
        *   `parameters` (dict): Parameters to pass to the tool's `execute` method.
        *   `execution_context` (dict, optional): Additional context for execution.

### Custom Workflow Nodes and MCP's StateGraph

The `CustomLangGraphNode` and `LangGraphWorkflowManager` concepts are placeholders for how the `MCPServer`'s `StateGraph` could be extended to support more complex, dynamically defined workflows. The `StateGraph` already allows adding nodes and edges, providing a foundation for custom workflow definitions. Future enhancements would involve formalizing how these custom nodes are registered and integrated into the `StateGraph`'s execution logic, potentially allowing agents to define and run their own sub-workflows.

## Interaction Flows

### Tool Registry:
1.  During system startup or dynamically, `AbstractToolInterface` implementations (tools) are instantiated.
2.  These instances are registered with the `MCPServer`'s internal `ToolRegistry` via the `register_external_tool` command.
3.  Agents or other systems can query the `ToolRegistry` via the `list_external_tools` command to discover available tools.
4.  To use a tool, an agent sends an `execute_external_tool` command to the `MCPServer`, which then delegates to the `ToolRegistry` to find and execute the tool.

### Custom LangGraph Nodes:
1.  Developers create new node classes by inheriting from `CustomLangGraphNode`, defining their `node_type`, `node_description`, input/output schemas, and implementing the `process` logic.
2.  These custom node classes are registered with the `LangGraphWorkflowManager` (conceptually, this would be integrated with the `MCPServer`'s `StateGraph`).
3.  Workflow designers can then define LangGraph workflows that incorporate instances of these registered custom node types.
4.  When a workflow is executed by the `LangGraphWorkflowManager`:
    *   It instantiates the custom nodes as needed, providing them with their `node_id` and `mcp_context`.
    *   As the graph traversal reaches a custom node, its `process` method is called with the appropriate inputs derived from the current graph state.
    *   The outputs from the `process` method are used to update the graph state, influencing the subsequent flow of the workflow.

## Example Usage (from `if __name__ == '__main__':`)

The `extensibility_integration.py` script includes demonstrations for both concepts:

*   **Tool Registry Demo:** Shows registration of `MockImageResizerTool`, listing tools, and executing a tool by ID.
*   **LangGraph Workflow Manager Demo:** Shows registration of `AgentTaskDispatchNode`, listing available node types, and conceptually invoking a node's `process` method.

```python
# In src/systems/extensibility_integration.py

async def tool_registry_demo():
    registry = ToolRegistry()
    resizer_tool = MockImageResizerTool()
    registry.register_tool(resizer_tool)
    # ... execute tool ...

async def lang_graph_manager_demo():
    # ... (MockMCPContext setup) ...
    lg_manager = LangGraphWorkflowManager(mcp_context=mcp_ctx)
    lg_manager.register_custom_node_type(AgentTaskDispatchNode)
    # ... conceptual node execution ...

asyncio.run(main_demo()) # Runs both demos
```

## Future Enhancements

### Tool Registry:
*   **Dynamic Loading:** Load tool plugins from external directories or packages.
*   **Dependency Management:** Handle dependencies between tools.
*   **Versioning:** More sophisticated handling of tool versions.
*   **Security:** Permissions and sandboxing for executing third-party tools.

### Custom LangGraph Nodes & Manager:
*   **Full LangGraph Integration:** Actual integration with the LangGraph library for defining, compiling, and running graphs.
*   **State Persistence:** Saving and loading the state of running or completed LangGraph workflows.
*   **Visual Workflow Editor:** A UI for composing workflows using registered custom nodes.
*   **Error Handling in Graphs:** Robust error handling, retry mechanisms, and conditional branching within workflows.
*   **Monitoring & Debugging:** Tools for monitoring the execution of LangGraph workflows and debugging custom nodes.