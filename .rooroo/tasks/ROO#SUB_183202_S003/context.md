# Sub-Task Context: ROO#SUB_183202_S003
## Parent Task ID: ROO#NAV_PLAN_20250518-183202
## Depends on: ROO#SUB_183202_S001, ROO#SUB_183202_S002
## Goal for rooroo-developer:
Develop a C# client module/script for a Unity project to communicate with the Python MCP server. This client must adhere to the communication architecture from `ROO#SUB_183202_S001` and interact with the server API implemented in `ROO#SUB_183202_S002`.

**Specifics to Implement:**
1.  **Unity Setup:** Assume a new or existing Unity project. The C# script should be easily integrable.
2.  **Request Sending:** Implement C# functions to send requests to the MCP server's API endpoints (e.g., using `UnityWebRequest` for HTTP).
3.  **Response Handling:** Implement C# logic to receive and parse responses from the MCP server (e.g., deserialize JSON).
4.  **Asynchronous Operations:** Ensure communication is handled asynchronously to prevent freezing the Unity editor or game.
5.  **Configuration:** Allow for easy configuration of the MCP server address and port.
6.  **Example Usage:** Provide a simple example within the C# script or a separate test script demonstrating how to send a request to the MCP server (e.g., to ping the server or request a list of available agents).

**Key Input References:**
*   Communication Architecture Design: Artifact from `ROO#SUB_183202_S001` (e.g., `.rooroo/tasks/ROO#SUB_183202_S001/artifacts/communication_architecture_design.md`)
*   MCP Server API details: Based on the implementation in `ROO#SUB_183202_S002` (refer to its context and the modified [`mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)).

**Expected Output Artifact:**
*   A C# script file (e.g., `MCP_Client.cs`) containing the client logic.
*   (Optional) A simple Unity scene or prefab demonstrating the client's usage.
*   A brief `README.md` in this task's artifact directory explaining how to integrate and use the C# client in a Unity project.