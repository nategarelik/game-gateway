# Sub-Task: Relocate Agent Files and Update Imports

**Parent Task ID:** ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251
**Sub-Task ID:** ROO#SUB_182251_S003
**Depends On:** ROO#SUB_182251_S001, ROO#SUB_182251_S002

**Goal:**
Relocate the existing agent Python files to the `src/agents/` directory. Update their internal import statements and any imports of MCP components to reflect the new project structure. Optionally, create a `base_agent.py`.

**Files to Move:**
1.  **Documentation Sentinel Agent:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py)
    *   **New Path:** [`src/agents/documentation_sentinel.py`](src/agents/documentation_sentinel.py)
2.  **Level Architect Agent:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py)
    *   **New Path:** [`src/agents/level_architect.py`](src/agents/level_architect.py)
3.  **Pixel Forge Agent:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py)
    *   **New Path:** [`src/agents/pixel_forge.py`](src/agents/pixel_forge.py)

**Instructions:**
1.  Ensure the target directory [`src/agents/`](src/agents/) exists (created in ROO#SUB_182251_S001).
2.  Move the specified agent files to their new locations.
3.  Review and update import statements within each agent file:
    *   For imports of other agents (if any): `from . import another_agent`
    *   For imports from MCP server (e.g., client): `from ..mcp_server.client import MCPClient` (adjust as per actual client class name and usage)
    *   For imports from toolchains (once they are moved): `from ..toolchains import some_bridge`
4.  Consider if a `src/agents/base_agent.py` would be beneficial for shared agent logic (e.g., common initialization, MCP interaction). If so, create it and refactor common elements. For now, this is optional but good to consider.

**Reference Parent Context:**
For overall project goals and existing file locations, see [`.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md`](.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md).