# MCP Server State Management

The MCP Server utilizes a `StateManager` class to manage the lifecycle and state of complex, potentially long-running tasks. This is primarily achieved through integration with LangGraph.

## Core Component: `StateManager`

-   **Location:** `src.mcp_server.core.state_manager.StateManager`
-   **Purpose:**
    -   To define and compile task workflows as LangGraph graphs.
    -   To initialize new instances of these graphs when a task is requested (e.g., via the `/request_action` API).
    -   To manage the state persistence and retrieval for each active task graph using a checkpointer (currently an in-memory `MemorySaver`).
    -   To provide methods for invoking updates/events on a task graph and retrieving its current state.

## Key Functionalities

1.  **Graph Definition (`_create_new_graph_definition`):**
    -   Defines the nodes (steps) and edges (transitions) of a task workflow.
    -   The current implementation uses a simple linear graph: `start_task` -> `process_request` -> `custom_end_node`.
    -   Nodes are methods within the `StateManager` that update the `ManagedTaskState` part of the overall `GraphState`.

2.  **Task Initialization (`initialize_task_graph`):**
    -   Called when a new task needs to be started (e.g., by an API endpoint).
    -   Takes a `task_id` (can be auto-generated) and `initial_input` for the task.
    -   Compiles the graph definition using a `MemorySaver` checkpointer.
    -   Stores the compiled graph instance.
    -   Returns a `ManagedTaskState` object representing the pristine, "pending" state of the task before any execution.

3.  **Task Invocation/Update (`invoke_graph_update`):**
    -   Takes a `task_id` and optional `event_input`.
    -   Retrieves the compiled graph for the `task_id`.
    -   Determines the appropriate input for the LangGraph `stream()` method:
        -   If it's the first run for the task (no checkpoint exists), it constructs an initial `GraphState` using a fresh `ManagedTaskState` and the `event_input`.
        -   If resuming from a checkpoint, it constructs a `GraphState` based on the checkpointed values and the new `event_input`.
    -   Invokes the graph's `stream()` method, allowing the graph to run (or continue running). For the current simple graph, this typically runs it to completion.
    -   Returns the `ManagedTaskState` after the stream processing, reflecting the updated status, step, and history.

4.  **State Retrieval (`get_graph_state`):**
    -   Takes a `task_id`.
    -   Retrieves the latest state snapshot for the task's graph using `compiled_graph.get_state(config)`.
    -   Extracts and returns the `ManagedTaskState` from the snapshot. Returns `None` if the task or its state is not found.

## State Objects

-   **`GraphState` (TypedDict):** The overall state object managed by LangGraph for each task. It contains:
    -   `task_state`: An instance of `ManagedTaskState`.
    -   `input_data`: Optional dictionary for initial or step-specific inputs to the task.
-   **`ManagedTaskState` (Pydantic Model):**
    -   Location: `src.mcp_server.models.managed_task_state.ManagedTaskState`
    -   Contains detailed information about a task, including:
        -   `task_id`
        -   `status` (e.g., "pending", "in_progress", "completed", "error")
        -   `current_step` (name of the current node in the graph)
        -   `history` (list of steps taken and messages)
        -   `results` (dictionary to store outcomes)
        -   `errors` (list of error details)
        -   `agent_responses` (dictionary for agent-specific data)

## Current Workflow Example

The default graph defined in `StateManager` is a simple linear flow:
1.  **`start_task`**: Sets task status to "in_progress", logs initiation.
2.  **`process_request`**: Simulates processing, logs action data, updates `agent_responses`.
3.  **`custom_end_node`**: Sets task status to "completed", logs completion.

This provides a basic framework for more complex, stateful agent interactions and task orchestrations.