# Task: Plan Core MCP Server Infrastructure Setup

**Task ID:** ROO#PLAN_MCP_SETUP_20250520-020934
**Parent Project Plan:** `.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`

**Goal for rooroo-planner:**
Based on the overall project plan ([`.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`](.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md:0)), the next major phase is "Setting up the core MCP server infrastructure". Your task is to create a detailed, actionable sub-plan for this phase.

**Key Objectives for this Planning Phase:**
1.  Identify all necessary components and sub-tasks required to establish the core MCP server infrastructure.
2.  Consider dependencies between these sub-tasks.
3.  For each sub-task, define a clear goal, suggest an appropriate Rooroo expert (e.g., `rooroo-developer`, `rooroo-documenter`), and estimate complexity if possible.
4.  The output should be a list of tasks in JSONL format suitable for adding to the `.rooroo/queue.jsonl` file.
5.  Refer to the "MCP Server Core Structure" section (lines 8-12) and the artifact [`.rooroo/tasks/ROO#SUB_PLAN_S001/mcp_server_core_structure.md`](.rooroo/tasks/ROO#SUB_PLAN_S001/mcp_server_core_structure.md:0) from the main plan for detailed specifications.

**Main Plan Summary (for context):**
```markdown
# Autonomous AI Agent Ecosystem for Game Development: Implementation Plan Summary
# Project Overview
This project has successfully developed a comprehensive implementation plan for an Autonomous AI Agent Ecosystem for Game Development. The system employs a distributed network of specialized AI agents coordinated through a central MCP server, utilizing LangGraph workflows for state management and dedicated toolchains.

## Completed Components

### 1. MCP Server Core Structure
- Defined core architecture for the central Model Context Protocol server
- Outlined LangGraph integration for state management
- Designed PromptRegistry for dynamic prompt handling

(Further sections of the main plan omitted for brevity in this context, but planner should assume access to the full file if needed via its own tools)
...
## Next Steps
The implementation plans are now ready for development. The next phase would involve:

1. Setting up the core MCP server infrastructure
2. Implementing the specialized agents one by one
3. Integrating the external toolchains
4. Testing the system with increasingly complex game development tasks
```

**Expected Output from Planner:**
*   A JSON object in the `result` field of the `attempt_completion` call, containing:
    *   `status`: "Done" or "Failed"
    *   `message`: Concise summary.
    *   `queue_tasks_json_lines` (string): A string containing multiple JSON objects, each on a new line, representing tasks for the queue. Each JSON object should include `taskId`, `parentTaskId` (set to `ROO#PLAN_MCP_SETUP_20250520-020934`), `suggested_mode`, `context_file_path` (for a new context file you'll specify for that sub-task), and `goal_for_expert`.
    *   `output_artifact_paths`: Path to a markdown file summarizing the plan (e.g., `.rooroo/plans/ROO#PLAN_MCP_SETUP_20250520-020934_summary.md`).

Please create a robust plan to get the MCP server infrastructure up and running.