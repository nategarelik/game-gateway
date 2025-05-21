# Task: Develop LevelArchitectAgent Prompts & Behavior Mechanisms

**Task ID:** ROO#SUB_20250520-024601_S004
**Parent Plan Task ID:** ROO#PLAN_LEVEL_ARCHITECT_20250520-024601
**Depends on:**
*   ROO#SUB_20250520-024601_S002 (LevelArchitectAgent Core Logic)
*   MCP Server PromptRegistry implementation (ROO#SUB_20250520-020934_S004)
**Overall Project Plan:** `.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`
**Agent File:** [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0)
**MCP PromptRegistry File:** [`src/mcp_server/core/prompt_registry.py`](src/mcp_server/core/prompt_registry.py:0)
**Relevant Design Documents:**
*   `docs/agents/level_architect.md` (if exists)
*   `.rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md`
*   `.rooroo/tasks/ROO#SUB_PLAN_S003/mcp_prompt_orchestration_system.md`

**Goal for rooroo-developer:**
Develop and refine the initial set of prompt templates for the `LevelArchitectAgent` and integrate their use within the agent's logic. Implement basic behavior enforcement mechanisms related to prompt usage.

**Key Implementation Steps:**
1.  **Define Initial Prompt Templates:**
    *   Based on the design documents, create 2-3 core prompt templates for the Level Architect. Examples:
        *   `level_generation_initial`: "Design a [level_type] level for a [genre] game with a [theme] theme. Key features should include [features_list]. The desired difficulty is [difficulty]."
        *   `level_style_adaptation`: "Adapt the following level data: [level_data_json] to a [new_style] style, focusing on [style_elements]."
        *   `level_constraint_check`: "Review the following level design: [level_data_json]. Ensure it meets these constraints: [constraints_list]. Report any violations."
    *   Store these templates. For now, they can be hardcoded as strings within the `LevelArchitectAgent` or a related configuration area. (Later, they will be managed by the MCP's `PromptRegistry`).
2.  **Integrate Prompts into Agent Logic:**
    *   In [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0):
        *   Modify the `_interpret_design_prompt` helper method (or create new ones) to select an appropriate prompt template based on the `task_details`.
        *   Populate the necessary variables for the chosen template from `task_details`.
        *   Format the prompt template with the variables.
        *   **Simulate LLM Call:** For this task, instead of an actual LLM call, the method that would use the prompt (e.g., `_interpret_design_prompt` or `_generate_initial_level_structure`) should log the fully resolved prompt and return a *mocked/predefined structured output* that an LLM might produce.
            *   Example: If using `level_generation_initial`, the mock output could be `{"level_type": "dungeon", "size": "medium", ...}`.
3.  **Behavior Enforcement (Basic):**
    *   Within the agent's logic, add simple checks:
        *   Before attempting to resolve a prompt, verify that all its declared required variables (if you define them alongside the templates) are available in the `task_details` or agent's current context.
        *   If critical information for a prompt is missing, the agent should log this and potentially report an error status back to the MCP (e.g., "insufficient_data_for_prompt").
4.  **Interaction with MCP `PromptRegistry` (Conceptual/Placeholder):**
    *   While full integration with the MCP's `PromptRegistry` (loading prompts from it, etc.) might be a larger step, the `LevelArchitectAgent` can be structured to *conceptually* fetch prompts by name.
    *   For instance, instead of hardcoding the template string directly in the logic, have a method like `_get_prompt_template_for_task(task_type)` which currently returns a hardcoded string but is designed to later query the `PromptRegistry`.
5.  **Update `__init__` for Prompt Configuration:**
    *   The `LevelArchitectAgent.__init__` could be updated to pre-load its initial set of (currently hardcoded) prompt templates into an internal dictionary (e.g., `self.prompt_templates`).
6.  **Unit Tests:**
    *   Expand tests in `tests/agents/test_level_architect_agent.py` (or create new ones if more organized) to cover:
        *   Correct selection of prompt templates based on task type (mocked).
        *   Successful formatting of prompts with variables.
        *   Handling of missing variables for a prompt.
        *   Verification that the agent's `process_task` uses the (mocked) output of prompt processing in its subsequent logic.

**Key Considerations:**
*   **No Actual LLM Calls:** This task focuses on the agent's internal mechanics of selecting, formatting, and *preparing* to use prompts. The "LLM call" is simulated.
*   **Template Management:** Keep templates simple for now. The goal is the flow, not perfect prompt engineering at this stage.
*   The `PromptRegistry` on the MCP server side is assumed to be functional from previous tasks for storing/retrieving prompts, but this agent task focuses on *using* prompts, even if sourced internally for now.

**Output Artifacts:**
*   Modified [`src/agents/level_architect_agent.py`](src/agents/level_architect_agent.py:0) with prompt handling logic.
*   Updated `tests/agents/test_level_architect_agent.py`.
*   A brief report in `.rooroo/tasks/ROO#SUB_20250520-024601_S004/artifacts/level_architect_prompts_report.md`.