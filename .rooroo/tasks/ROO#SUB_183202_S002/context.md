# Sub-Task Context: ROO#SUB_183202_S002
## Parent Task ID: ROO#NAV_PLAN_20250518-183202
## Depends on: ROO#SUB_183202_S001
## Goal for rooroo-developer:
Modify the existing Python MCP server ([`mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)) to expose API endpoints as defined by the communication architecture from task `ROO#SUB_183202_S001`.

**Specifics to Implement:**
1.  **API Endpoints:** Implement the server-side API endpoints (e.g., using Flask, FastAPI, or Python's built-in `http.server` if simple enough) according to the design from `ROO#SUB_183202_S001`.
2.  **Request Handling:** Parse incoming requests from Unity.
3.  **Agent Invocation:** Based on the request, call the appropriate Python agent:
    *   Level Architect: [`level_architect_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py)
    *   Pixel Forge: [`pixel_forge_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py)
    *   Documentation Sentinel: [`documentation_sentinel_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py)
4.  **Toolchain Invocation:** Implement logic to call toolchain integrations:
    *   Muse Integration: [`muse_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py)
    *   Retro Diffusion Integration: [`retro_diffusion_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py)
5.  **Response Generation:** Format and send responses back to Unity as per the defined protocol.
6.  **Server Execution:** Ensure the MCP server can be run (e.g., `python mcp_server_core.py`) and is accessible locally.

**Key Input References:**
*   Communication Architecture Design: Artifact from `ROO#SUB_183202_S001` (e.g., `.rooroo/tasks/ROO#SUB_183202_S001/artifacts/communication_architecture_design.md`)
*   Existing MCP Server: [`mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)
*   Agent Scripts (paths listed above)
*   Toolchain Scripts (paths listed above)

**Expected Output Artifact:**
*   Modified [`mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py) file with the implemented API endpoints and logic.
*   (Optional) A brief `README.md` in this task's artifact directory explaining how to run the modified server and any new dependencies.