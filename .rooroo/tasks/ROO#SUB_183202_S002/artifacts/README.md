# MCP Server (ROO#SUB_183202_S002 Modification)

This document describes how to run the modified MCP server (`mcp_server_core.py`) and its dependencies. The server now includes a Flask-based REST API to interact with various AI agents and toolchains.

## Dependencies

The primary new dependency is **Flask**. Ensure it is installed in your Python environment:

```bash
pip install Flask
```

The server also depends on the agent and toolchain modules being correctly located. The script attempts to dynamically add their directories to `sys.path`. The expected locations are:
*   Level Architect Agent: `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py`
*   Pixel Forge Agent: `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py`
*   Documentation Sentinel Agent: `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py`
*   Muse Integration: `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py`
*   Retro Diffusion Integration: `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py`

Ensure these files exist at the specified paths relative to the workspace root.

## Running the Server

To run the MCP server, navigate to the directory containing `mcp_server_core.py` (which is `.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/`) and execute it using Python:

```bash
# Assuming your current directory is the workspace root c:/Users/Nate2/UnityAgent
cd .rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/
python mcp_server_core.py
```

By default, the server will start on `http://127.0.0.1:5001`.
You can configure the host and port using environment variables:
*   `MCP_SERVER_HOST` (defaults to `127.0.0.1`)
*   `MCP_SERVER_PORT` (defaults to `5001`)

Example:
```bash
set MCP_SERVER_PORT=5005 
# or on Linux/macOS: export MCP_SERVER_PORT=5005
python mcp_server_core.py
```

## API Endpoint

The server exposes the following API endpoint:

*   **`POST /execute_agent`**
    *   **Request Body (JSON):**
        ```json
        {
          "task_id": "string", // Unique identifier for this request instance
          "agent_id": "string", // Identifier of the target agent or toolchain (e.g., "level_architect", "pixel_forge", "muse", "retro_diffusion")
          "parameters": {      // JSON object containing parameters specific to the agent/task
            // ... agent-specific parameters ...
          }
        }
        ```
    *   **Response Body (JSON):**
        ```json
        {
          "task_id": "string",
          "status": "string",  // "success" or "failed"
          "result": { /* agent-specific results */ }, // if success
          "error": { /* error details */ } // if failed
        }
        ```

Refer to the `communication_architecture_design.md` from task `ROO#SUB_183202_S001` for detailed message structures and error codes.

## Agent/Toolchain Interaction Notes

*   **Agents** (e.g., `level_architect`): The server expects these agent classes to have a method `handle_direct_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]`. This method receives the `parameters` from the API request and should return a dictionary that will be placed in the `result` field of the API response.
*   **Toolchains** (`muse`, `retro_diffusion`):
    *   For `muse`: `parameters` should include `command_type` and `command_text`.
    *   For `retro_diffusion`: `parameters` should include `prompt` and optionally `options`.

If an agent or toolchain is not found, or if its required methods/parameters are missing, the API will return an appropriate error. Check the server console output for detailed logs and warnings regarding module imports and request processing.