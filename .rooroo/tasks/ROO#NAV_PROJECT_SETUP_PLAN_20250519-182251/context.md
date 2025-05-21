# Planning Request: Full Project Implementation and Organization

**Task ID:** ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251
**User Request:** "Great, proceed with the full plan but start to move everything into an organized project folder with proper documentation. Don't ask for approval, proceed with it."

**Overall Goal:**
Refactor the existing AI agent ecosystem into a well-organized project structure, implement the full functionality of each specialized agent as per their design documents, integrate toolchains, and generate comprehensive documentation for all components and the overall system. The Navigator will manage the execution of planned tasks from the queue without requiring per-step user approval.

**Reference Plan:**
The overall project scope is outlined in [`.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md`](.rooroo/plans/ROO#20250517-041757-PLAN_final_summary.md).

**Current System State:**
1.  **MCP Server:** Operational.
    *   Core: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)
    *   Client Lib: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_client.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_client.py)
    *   Handles direct API calls to `/execute_agent`.
2.  **Agents:** Basic shells exist, `__init__` and `handle_direct_request` methods are present. Core logic for `handle_direct_request` and `execute` (workflow) methods needs full implementation.
    *   `DocumentationSentinelAgent`: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py)
    *   `LevelArchitectAgent`: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py)
    *   `PixelForgeAgent`: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py)
3.  **Toolchain Bridges:** Basic shells exist. Core logic needs full implementation.
    *   `MuseToolchainBridge`: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py)
    *   `RetroDiffusionToolchainBridge`: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py)
4.  **File Structure:** Currently, components are located within various `.rooroo/tasks/` subdirectories from previous development stages.

**Key Requirements for the Plan:**
1.  **Project Restructuring:**
    *   Define a clean, organized project directory structure within the workspace root (e.g., `src/`, `docs/`, `tests/`).
    *   Plan tasks to move existing Python files (`mcp_server_core.py`, `mcp_client.py`, agent files, toolchain bridge files) into this new structure.
    *   Ensure all Python import statements are updated to reflect the new structure.
    *   Establish `requirements.txt` for dependencies.
2.  **Agent Implementation (Full Functionality):**
    *   For each agent (`DocumentationSentinelAgent`, `LevelArchitectAgent`, `PixelForgeAgent`):
        *   Detail tasks for `rooroo-developer` to implement the core logic of its `handle_direct_request` method based on its specific design document (e.g., for `LevelArchitectAgent`, this is specified in [`.rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md`](.rooroo/tasks/ROO#SUB_PLAN_S002/specialized_agent_roles_and_prompt_systems.md)).
        *   Detail tasks to implement the `execute(self, state: GameDevState)` method for participation in stateful, multi-step workflows managed by the MCP server's `StateGraph`.
3.  **Toolchain Bridge Implementation:**
    *   For each toolchain bridge (`MuseToolchainBridge`, `RetroDiffusionToolchainBridge`):
        *   Detail tasks for `rooroo-developer` to implement its methods to interact with the (potentially mocked for now) external tool or API.
4.  **Documentation:**
    *   Detail tasks for `rooroo-documenter` to:
        *   Create an overall project `README.md` in the new project root.
        *   Create detailed markdown documentation for the MCP server, each agent, and each toolchain bridge, to be placed in the `docs/` directory.
5.  **Testing Strategy (High-Level):**
    *   Briefly outline how the implemented components will be tested (e.g., suggestions for unit tests, API endpoint tests for agents). Planner can suggest tasks for `rooroo-developer` to create basic test scripts or manual test procedures.

**Expected Output from Planner:**
A JSON array (as a string, with each object on a new line) of task objects suitable for adding to the Rooroo Navigator's task queue. Each task object should specify `taskId`, `parentTaskId` (can be this planning task ID: `ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251`), `suggested_mode`, `goal_for_expert`, `context_file_path` (if any, for sub-tasks), and `dependencies`.

**Example Desired Project Structure (Planner to refine and use for task generation):**
```
/ (workspace root: c:/Users/Nate2/UnityAgent)
├── src/
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server_core.py
│   │   └── client.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Consider if a more functional base is needed
│   │   ├── documentation_sentinel.py
│   │   ├── level_architect.py
│   │   └── pixel_forge.py
│   ├── toolchains/
│   │   ├── __init__.py
│   │   ├── base_toolchain_bridge.py # Consider if useful
│   │   ├── muse_bridge.py
│   │   └── retro_diffusion_bridge.py
│   └── utils/
│       └── __init__.py
├── docs/
│   ├── README.md
│   ├── mcp_server.md
│   ├── agents/
│   │   ├── documentation_sentinel.md
│   │   ├── level_architect.md
│   │   └── pixel_forge.md
│   └── toolchains/
│       ├── muse.md
│       └── retro_diffusion.md
├── tests/
│   ├── test_mcp_server.py
│   └── agents/
│       └── test_documentation_sentinel.py 
├── requirements.txt
└── .rooroo/ # Navigator's internal files, remains as is