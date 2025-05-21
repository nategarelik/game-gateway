# Task: Implement LevelArchitectAgent Core Logic

**Task ID:** ROO#SUB_20250520-024601_S002
**Parent Plan Task ID:** ROO#PLAN_LEVEL_ARCHITECT_20250520-024601
**Depends on:** ROO#SUB_20250520-024601_S001 (LevelArchitectAgent Class Structure)
**Overall Project Plan:** `.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`
**Agent File:** [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0)
**Relevant Design Document:** `docs/agents/level_architect.md` (if exists) and `.rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md`

**Goal for rooroo-developer:**
Implement the core logic within the `LevelArchitectAgent` class ([`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0)) for processing level design tasks. This involves fleshing out the `process_task` method and any helper methods required for its operation.

**Key Implementation Steps:**
1.  **Refine `process_task` Method:**
    *   Update the `process_task` method in [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0).
    *   This method should be able to:
        *   Receive `task_details` (a dictionary, likely including a `prompt`, `task_id`, `theme`, `constraints`, etc.).
        *   Interpret the core request from the `task_details`.
        *   Call internal helper methods (defined below) to generate or modify level data.
        *   Post progress events to the MCP server using `self.post_event_to_mcp()`.
        *   Return a dictionary with the `status` ("success" or "failure"), a `message`, and the `output` (e.g., the generated level data or a reference to it).
2.  **Implement Helper Methods for Level Design Logic:**
    *   **`_interpret_design_prompt(prompt: str, context: dict) -> dict`:**
        *   (Placeholder for now) This method would eventually use an LLM or complex parsing to understand the design prompt. For this task, it can perform simple keyword extraction or rule-based interpretation of the `prompt` string from `task_details`.
        *   Return a structured representation of the design goals (e.g., `{"level_type": "dungeon", "size": "medium", "key_features": ["traps", "secret_room"]}`).
    *   **`_generate_initial_level_structure(design_goals: dict) -> dict`:**
        *   Based on the `design_goals`, create a basic data structure representing the level. This could be a 2D array, a graph of rooms, or a list of components.
        *   (Placeholder for now) For this task, it can return a predefined simple structure or generate one based on simple rules.
        *   Example output: `{"rooms": [{"id": "room1", "type": "start"}, {"id": "room2", "type": "corridor"}], "connections": [("room1", "room2")]}`.
    *   **`_apply_theme_and_constraints(level_structure: dict, theme: str, constraints: list) -> dict`:**
        *   (Placeholder for now) Modify the `level_structure` based on `theme` and `constraints`. This might involve adding specific types of rooms, items, or adjusting parameters.
        *   Return the modified `level_structure`.
    *   **`_interact_with_external_tool(tool_name: str, tool_input: dict) -> dict`:**
        *   (Placeholder for now) This method will eventually call external tools (e.g., Unity Muse, Retro Diffusion via MCP or direct API). For this task, it can log the intended call and return a mock success response.
        *   The `self.level_design_tool_config` from `__init__` might be used here.
3.  **Update `__init__` (if needed):**
    *   If the `LevelArchitectAgent` needs to initialize any specific clients or configurations for its core logic (beyond what's in `BaseAgent`), add them to the `__init__` method.
4.  **Error Handling:**
    *   Implement basic error handling within `process_task` and helper methods. If a step fails, the agent should attempt to post an error event to the MCP and return an appropriate failure response from `process_task`.

**Key Considerations:**
*   The focus is on the internal logic flow of the agent and its placeholder interactions. Full LLM integration or actual external tool calls are for later tasks.
*   The data structures for level design can be simple for now, as long as the flow is clear.
*   Ensure the `process_task` method in [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0) is updated from the very basic version provided in the S001 context.

**Output Artifacts:**
*   Modified [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0) with implemented core logic.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-024601_S002/artifacts/level_architect_core_logic_report.md` detailing the implemented logic and any significant decisions.