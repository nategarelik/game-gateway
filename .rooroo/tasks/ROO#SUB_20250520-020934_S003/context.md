# Task: Integrate LangGraph for MCP State Management

**Task ID:** ROO#SUB_20250520-020934_S003
**Parent Plan Task ID:** ROO#PLAN_MCP_SETUP_20250520-020934
**Depends on:** ROO#SUB_20250520-020934_S001 (Initialize MCP Server Project Structure & Dependencies), ROO#SUB_20250520-020934_S002 (Implement Core MCP Server API Endpoints)
**Overall Project Plan:** `../../plans/ROO#20250517-041757-PLAN_final_summary.md`
**MCP Server Core Structure Document:** `../../ROO#SUB_PLAN_S001/mcp_server_core_structure.md` (relative path, actual: `.rooroo/tasks/ROO#SUB_PLAN_S001/mcp_server_core_structure.md`)

**Goal for rooroo-developer:**
Integrate LangGraph into the MCP server for managing the state of ongoing tasks and agent interactions. This involves setting up a basic LangGraph workflow that can be triggered and updated via API calls.

**Key Implementation Steps:**
1.  **Define Core State Model:**
    *   In `src/mcp_server/models/`, define a Pydantic model for the core state that LangGraph will manage (e.g., `ManagedTaskState`). This state should include at least:
        *   `task_id`: Unique identifier for the task/workflow.
        *   `current_step`: Name of the current step in the workflow.
        *   `status`: (e.g., "pending", "in_progress", "waiting_for_agent", "completed", "failed").
        *   `history`: A list of events or steps taken.
        *   `agent_responses`: A dictionary to store responses from agents.
        *   `error_info`: Details if an error occurs.
2.  **Create State Manager Class:**
    *   In `src/mcp_server/core/state_manager.py`, create a `StateManager` class.
    *   This class will encapsulate the LangGraph `StatefulGraph`.
    *   It should have methods to:
        *   Initialize a new graph instance for a new task.
        *   Add nodes and edges to the graph (initially, a very simple graph with a start and end node, and perhaps one intermediate "processing" node).
        *   Invoke the graph with an initial input (e.g., when a new task is posted via `/request_action`).
        *   Update the graph's state based on external events (e.g., an agent completing a sub-task and posting results back).
        *   Retrieve the current state of a graph instance.
3.  **Basic LangGraph Setup:**
    *   Define a simple LangGraph:
        *   Start node: Initializes the task state.
        *   An example "process_request" node: Simulates some processing, perhaps logs the input and transitions.
        *   End node: Marks the task as completed (for this initial setup).
    *   Compile this graph within the `StateManager`.
4.  **Integrate with API (Placeholder):**
    *   Modify the `/request_action` endpoint in `src/mcp_server/api/routes.py` (or `main.py`):
        *   When a new action is requested, it should (conceptually) trigger the `StateManager` to create and invoke a new LangGraph instance for that task.
        *   For now, this can be a placeholder call; full asynchronous handling and callbacks will be in later tasks.
    *   The `/status` endpoint could be enhanced to (conceptually) query the `StateManager` for active graph instances, though this is optional for this initial task.
5.  **Unit Tests:**
    *   Add basic unit tests in `tests/mcp_server/test_state_manager.py` to:
        *   Verify the `StateManager` can initialize a graph.
        *   Verify a simple graph can be invoked and transitions state.

**Key Considerations:**
*   This is an *initial* integration. The LangGraph workflow will be very simple at this stage.
*   Focus on the mechanics of creating, invoking, and (conceptually) updating a LangGraph instance managed by the `StateManager`.
*   Persistence of graph states (e.g., using `langgraph-checkpoint`) is **out of scope** for this sub-task but should be kept in mind for future tasks. For now, states can be in-memory.

**Output Artifacts:**
*   Modified `src/mcp_server/models/` (with new state models).
*   New/modified `src/mcp_server/core/state_manager.py`.
*   Modified `src/mcp_server/api/routes.py` (or `main.py`) showing placeholder integration points.
*   New `tests/mcp_server/test_state_manager.py`.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-020934_S003/artifacts/langgraph_integration_report.md`.