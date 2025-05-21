# Autonomous Iteration Workflow Documentation

The Autonomous Iteration Workflow, also known as the Playtest Analysis Loop, is a system designed to simulate playtesting, analyze the results, and trigger optimization tasks to improve game levels or mechanics. This workflow aims to automate parts of the game design and balancing process.

The core Python module for this system is located at [`src/workflows/autonomous_iteration.py`](../../src/workflows/autonomous_iteration.py).

## Purpose

The primary goals of this workflow are:
1.  **Simulate Playtests:** Generate mock playtest data for specified game levels, including metrics like completion status, objectives met, and damage taken.
2.  **Analyze Metrics:** Process the collected playtest data to identify patterns, common failure points, or areas of potential improvement.
3.  **Trigger Optimizations:** Based on the analysis, suggest and (conceptually) dispatch tasks to relevant AI agents (e.g., `LevelArchitectAgent`) to make design changes or adjustments.
4.  **Iterate:** Enable a continuous loop where design changes can be re-tested and further refined.

## Core Components and Concepts

### 1. `PlaytestSession`
   *   A data class representing the outcome of a single simulated playtest.
   *   Attributes: `session_id`, `level_id`, `player_id`, `duration_seconds`, and `metrics` (a dictionary containing play-specific data like `completion_status`, `damage_taken`).

### 2. `PlaytestAnalysisReport`
   *   A data class representing the output from analyzing a batch of `PlaytestSession` objects.
   *   Attributes: `report_id`, `analyzed_level_ids`, `findings` (list of textual descriptions of issues), and `suggestions` (list of dictionaries detailing tasks for other agents).

### 3. `PlaytestSimulator`
   *   **Purpose:** Simulates playtest sessions.
   *   **Initialization:** Takes optional `level_design_data` (a dictionary conceptually describing level properties like difficulty).
   *   **Method: `async run_simulated_playtest(level_id: str, player_id: str = "sim_player_01") -> PlaytestSession`**:
        *   Simulates a playtest for the given `level_id`.
        *   Generates mock `metrics` based on randomness and conceptual `level_design_data`.
        *   Returns a `PlaytestSession` object.

### 4. `PlaytestAnalyzer`
   *   **Purpose:** Analyzes lists of `PlaytestSession` data.
   *   **Method: `async analyze_playtest_data(sessions: List[PlaytestSession]) -> PlaytestAnalysisReport`**:
        *   Processes the sessions to identify patterns (e.g., common failure points on a specific level).
        *   Generates `findings` (textual descriptions) and `suggestions` (structured task proposals for agents like `LevelArchitectAgent`).
        *   Returns a `PlaytestAnalysisReport`.

### 5. `OptimizationTrigger`
   *   **Purpose:** Processes `PlaytestAnalysisReport` objects and (conceptually) dispatches tasks to the MCP.
   *   **Initialization:** Takes an optional `mcp_task_dispatcher` (a callable function that would send tasks to the MCP).
   *   **Method: `async process_analysis_report(report: PlaytestAnalysisReport)`**:
        *   Iterates through `report.suggestions`.
        *   For each suggestion, it logs the intent to trigger a task and (if `mcp_task_dispatcher` is configured) would call it to dispatch the task. Currently, it simulates the dispatch.

### 6. `AutonomousIterationWorkflow` (Facade)
   *   **Purpose:** The main orchestrator for the entire loop.
   *   **Initialization:** Takes an optional `mcp_task_dispatcher` and `initial_level_designs`. Initializes instances of `PlaytestSimulator`, `PlaytestAnalyzer`, and `OptimizationTrigger`.
   *   **Method: `async run_iteration_cycle(level_ids_to_test: List[str], num_sessions_per_level: int = 3) -> PlaytestAnalysisReport`**:
        1.  Increments an internal iteration counter.
        2.  For each `level_id` in `level_ids_to_test`, runs `num_sessions_per_level` simulated playtests using `PlaytestSimulator`.
        3.  Collects all `PlaytestSession` objects.
        4.  Passes the collected sessions to `PlaytestAnalyzer.analyze_playtest_data()` to get a report.
        5.  Passes the `PlaytestAnalysisReport` to `OptimizationTrigger.process_analysis_report()` to (conceptually) dispatch optimization tasks.
        6.  Returns the `PlaytestAnalysisReport`.

:start_line:58
-------
## Integration with MCP Server

The `AutonomousIterationWorkflow` is instantiated and managed by the `MCPServer`. This central integration allows the MCP to orchestrate the playtest analysis loop and expose its functionalities to other agents and systems.

### Task Dispatching

The `MCPServer` provides the `AutonomousIterationWorkflow` with a concrete `mcp_task_dispatcher`. This dispatcher is an internal method of the `MCPServer` (`_dispatch_mcp_task`) that translates the workflow's suggestions into actual task requests sent to the MCP's `handle_api_request` method. This ensures that suggestions for design changes are properly routed to the target agents (e.g., `LevelArchitectAgent`, `CodeWeaverAgent`).

### Triggering Iteration Cycles

The `MCPServer` exposes a method to trigger a full iteration cycle of the Autonomous Iteration Workflow, which can be invoked via the `POST /execute_agent` API endpoint.

*   **Endpoint:** `POST /execute_agent`
*   **`agent_id`**: `"aiw"`
*   **`parameters`**:
    *   `command_type`: `"run_iteration_cycle"`
    *   `level_ids_to_test` (list of strings, required): A list of level IDs to include in the playtest simulation for this cycle.
    *   `num_sessions_per_level` (integer, optional): The number of simulated playtest sessions to run for each level. Defaults to 3.

When this command is received, the `MCPServer` calls the `autonomous_iteration_workflow.run_iteration_cycle()` method, initiating a full cycle of playtest simulation, analysis, and task dispatching.

## Interaction Flow

1.  The `AutonomousIterationWorkflow` is initialized by the `MCPServer`, receiving the `_dispatch_mcp_task` method as its task dispatcher.
2.  An external system or a high-level agent triggers `run_iteration_cycle()` via the `MCPServer`'s `POST /execute_agent` endpoint with a list of level IDs to test.
3.  **Simulation:** The `PlaytestSimulator` generates mock playtest data for these levels.
4.  **Analysis:** The `PlaytestAnalyzer` processes this data, identifying issues and formulating suggestions for redesign or tweaking.
5.  **Triggering:** The `OptimizationTrigger` takes these suggestions and dispatches them as tasks to relevant AI agents (e.g., `LevelArchitectAgent`) via the `MCPServer`'s `_dispatch_mcp_task` method.
6.  (Outside this specific module) The `LevelArchitectAgent` (or other relevant agents) would receive these tasks, make modifications to the level designs.
7.  The loop can then be re-run on the modified (or new) levels to assess the impact of the changes.

## Example Usage (from `if __name__ == '__main__':`)

The `autonomous_iteration.py` script includes a self-contained demo:

```python
# In src/workflows/autonomous_iteration.py

# Mock MCP task dispatcher
async def mock_mcp_dispatch(task_spec: dict) -> str:
    dispatch_id = f"mcp_task_{int(time.time())}_{random.randint(100,999)}"
    logger.info(f"[MockMCP] Received task to dispatch: {task_spec}. Assigned ID: {dispatch_id}")
    return dispatch_id

# Conceptual initial level designs
level_designs = {
    "level_01_intro": {"difficulty_score": 0.9, ...},
    "level_02_puzzle_arena": {"difficulty_score": 0.4, ...},
    # ...
}

workflow = AutonomousIterationWorkflow(mcp_task_dispatcher=mock_mcp_dispatch, initial_level_designs=level_designs)

async def demo_run():
    levels_to_test_round1 = ["level_01_intro", "level_02_puzzle_arena"]
    report1 = await workflow.run_iteration_cycle(level_ids_to_test=levels_to_test_round1, num_sessions_per_level=5)
    
    if report1:
        print("\nReport 1 Findings:", report1.findings)
        # ...
    
    # ... (potentially run more cycles) ...

asyncio.run(demo_run())
```
This example demonstrates running a couple of iteration cycles, showing how playtests are simulated, analysis reports are generated, and mock tasks are "dispatched."

## Future Enhancements

*   **Real Playtest Integration:** Interface with an actual game environment or a more sophisticated simulation framework to gather genuine playtest metrics.
*   **Advanced Analytics:** Implement more complex data analysis techniques (e.g., statistical analysis, machine learning models) to derive deeper insights from playtest data.
*   **Sophisticated Task Generation:** Improve the logic for generating task suggestions, making them more specific and actionable for the target agents.
*   **MCP Integration:** Fully implement the `mcp_task_dispatcher` to allow the workflow to create and manage tasks within the MCP server.
*   **Feedback Loop Closure:** Develop mechanisms for agents to report back on the success/failure of optimization tasks, allowing the workflow to track the effectiveness of changes.
*   **Configurable Parameters:** Allow simulation parameters, analysis thresholds, and target agent aliases to be configured externally.
*   **Metrics Standardization:** Define a clear, extensible schema for playtest metrics.