# Sub-Task: Relocate MCP Server and Client Files

**Parent Task ID:** ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251
**Sub-Task ID:** ROO#SUB_182251_S002
**Depends On:** ROO#SUB_182251_S001

**Goal:**
Relocate the existing MCP server core and client library Python files to the newly created project structure. Update their internal import statements to reflect the new package structure. Create a `requirements.txt` file.

**Files to Move:**
1.  **MCP Server Core:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)
    *   **New Path:** [`src/mcp_server/server_core.py`](src/mcp_server/server_core.py)
2.  **MCP Client Library:**
    *   **Original Path:** [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_client.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_client.py)
    *   **New Path:** [`src/mcp_server/client.py`](src/mcp_server/client.py)

**Instructions:**
1.  Ensure the target directory [`src/mcp_server/`](src/mcp_server/) exists (created in ROO#SUB_182251_S001).
2.  Move the specified files to their new locations.
3.  Review and update any import statements within `server_core.py` and `client.py` to use relative imports appropriate for the `src.mcp_server` package (e.g., `from . import some_module` or `from ..agents import some_agent_if_needed_later`). For now, focus on internal consistency within `src.mcp_server`.
4.  Create a `requirements.txt` file in the project root (`c:/Users/Nate2/UnityAgent/requirements.txt`) and add initial dependencies. Suggestion:
    ```
    fastapi
    uvicorn[standard]
    # Add other known dependencies if any
    ```

**Reference Parent Context:**
For overall project goals and existing file locations, see [`.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md`](.rooroo/tasks/ROO#NAV_PROJECT_SETUP_PLAN_20250519-182251/context.md).