# Unity Integration Setup Guide: Python AI Agent Ecosystem

This guide details the setup process for the Python AI agent ecosystem and its integration with a Unity project for testing. It covers setting up the Python environment, integrating the Unity C# client, and basic test cases.

**Task ID:** ROO#SUB_183202_S004

## 1. Python Environment Setup

The AI agent ecosystem and the MCP server are Python-based.

### 1.1. Dependencies

The primary dependency for the modified MCP server is **Flask**. Ensure you have Python installed (version 3.7+ recommended) and install Flask using pip:

```bash
pip install Flask
```

The MCP server also dynamically imports agent and toolchain modules. Ensure the following files exist at the specified paths relative to the workspace root (`c:/Users/Nate2/UnityAgent`):

*   Level Architect Agent: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py)
*   Pixel Forge Agent: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py)
*   Documentation Sentinel Agent: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py)
*   Muse Integration: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py)
*   Retro Diffusion Integration: [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/retro_diffusion_integration.py)

### 1.2. Running the MCP Server

The modified MCP server is located at [`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py).

To run the server, open a terminal, navigate to the directory containing the script, and execute it using Python:

```bash
# Assuming your current directory is the workspace root c:/Users/Nate2/UnityAgent
cd .rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/
python mcp_server_core.py
```

By default, the server will start on `http://127.0.0.1:5001`.

You can configure the host and port using environment variables before running the script:

*   `MCP_SERVER_HOST` (defaults to `127.0.0.1`)
*   `MCP_SERVER_PORT` (defaults to `5001`)

Example (Windows):

```bash
set MCP_SERVER_PORT=5005
python mcp_server_core.py
```

Example (Linux/macOS):

```bash
export MCP_SERVER_PORT=5005
python mcp_server_core.py
```

The server exposes a REST API endpoint `POST /execute_agent` for interacting with agents. Refer to the [Communication Architecture Design document](.rooroo/tasks/ROO#SUB_183202_S001/artifacts/communication_architecture_design.md) for details on the request and response JSON structures.

## 2. Unity Project Setup

To integrate the AI agent ecosystem with your Unity project, you need to add and configure the C# MCP client script.

### 2.1. Integrating the C# Client

1.  **Copy Script:** Obtain the `MCP_Client.cs` file (from task `ROO#SUB_183202_S003`). Place this file into your Unity project's `Assets` folder (e.g., `Assets/Scripts/Rooroo/MCP/`).
2.  **Create GameObject:** In your Unity scene, create an empty GameObject. A descriptive name like "MCPClientManager" is recommended.
3.  **Attach Script:** Drag and drop the `MCP_Client.cs` script onto the newly created GameObject in the Hierarchy or Inspector.

### 2.2. Configuring the C# Client

Select the GameObject with the `MCP_Client` script attached. In the Inspector panel, configure the following fields:

*   **Server Address:** Enter the IP address or hostname where your Python MCP server is running (e.g., `127.0.0.1` for localhost).
*   **Server Port:** Enter the port number the MCP server is listening on (e.g., `5001`).
*   **API Endpoint:** This should match the agent execution endpoint configured on the server. The default is `/execute_agent`.

Adjust these settings to match your MCP server's configuration.

### 2.3. Using the Client in Scripts

In your other Unity C# scripts, you can get a reference to the `MCP_Client` instance and use its `SendRequestAsync` method to communicate with the server.

```csharp
using UnityEngine;
using Rooroo.MCP; // Assuming MCP_Client.cs is in a Rooroo.MCP namespace
using System.Threading.Tasks; // Required for async/await
using System; // Required for Guid

public class AgentInteractionExample : MonoBehaviour
{
    public MCP_Client mcpClient; // Assign this in the Inspector

    async void Start()
    {
        if (mcpClient == null)
        {
            mcpClient = FindObjectOfType<MCP_Client>();
            if (mcpClient == null)
            {
                Debug.LogError("MCP_Client instance not found in the scene!");
                return;
            }
        }

        // Example: Call a basic agent on start
        await CallDocumentationSentinel();
    }

    public async Task CallDocumentationSentinel()
    {
        // 1. Prepare parameters as a JSON string
        // The Documentation Sentinel agent might expect parameters like {"text": "...", "format": "..."}
        string agentParamsJson = "{\"text\": \"Document this code snippet:\nvoid Start() { Debug.Log(\"Hello\"); }\", \"format\": \"markdown\"}";

        string agentIdToCall = "documentation_sentinel"; // The agent_id for the Documentation Sentinel

        Debug.Log($"Attempting to call agent: {agentIdToCall}");

        // Generate a unique task ID for this request
        string taskId = Guid.NewGuid().ToString();

        MCPResponse response = await mcpClient.SendRequestAsync(agentIdToCall, agentParamsJson, taskId);

        if (response != null)
        {
            Debug.Log($"Response Status: {response.status}");
            if (response.IsSuccess())
            {
                Debug.Log($"Agent Result (JSON): {response.result}");
                // 2. Deserialize response.result if needed
                // The result for Documentation Sentinel might be {"documentation": "..."}
                // You would need a C# class to deserialize this, e.g.,
                // [System.Serializable]
                // public class DocSentinelResult { public string documentation; }
                // DocSentinelResult resultData = JsonUtility.FromJson<DocSentinelResult>(response.result);
                // Debug.Log($"Generated Documentation: {resultData.documentation}");
            }
            else
            {
                if (response.error != null)
                {
                    Debug.LogError($"Agent Error Code: {response.error.code}, Message: {response.error.message}");
                }
                else
                {
                    Debug.LogError("Agent request failed with no specific error details.");
                }
            }
        }
        else
        {
            Debug.LogError("No response received from MCP_Client or request failed catastrophically.");
        }
    }
}
```

Remember to handle JSON serialization and deserialization for agent parameters and results. Unity's built-in `JsonUtility` can be used for simple objects, but for more complex structures, consider using a library like Newtonsoft.Json.

## 3. Basic Test Cases

These test cases can be implemented within your Unity scripts to verify communication with the MCP server and basic agent functionality.

### 3.1. Test Case 1: MCP Server Ping/Status Check

While the current MCP server implementation doesn't have a dedicated `/ping` or `/status` endpoint, you can perform a basic connectivity check by attempting to call a known agent with minimal parameters and observing the response status. A simple call to an agent like "documentation_sentinel" with empty or minimal parameters should result in either a "success" (if the agent handles it) or a specific "failed" status like `INVALID_PARAMETERS` or `EXECUTION_ERROR`, indicating the server was reached and processed the request. A connection error would indicate the server is not reachable.

You can use the `MCP_Client.TestSendPingRequest()` method (accessible via the Context Menu in the Unity Inspector when the script is selected) as a starting point. This method currently attempts to call the "level_architect" agent. You could modify this method or create a new one to target "documentation_sentinel" with a minimal valid request.

**Expected Outcome:** The Unity Console should show logs indicating a response was received from the server, with a status of "success" or a specific "failed" status related to parameter validation or agent execution, but *not* a connection error.

### 3.2. Test Case 2: Basic Agent Invocation

This test case involves making a call from Unity to invoke one of the simpler agents via the MCP server and processing its response. The Documentation Sentinel agent is a good candidate for this.

**Steps:**

1.  Ensure the Python MCP server is running and the Documentation Sentinel agent ([`.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S004/artifacts/documentation_sentinel_agent.py)) is accessible to the server.
2.  In a Unity script (like the `AgentInteractionExample` above), get a reference to the `MCP_Client`.
3.  Prepare a JSON string for the parameters expected by the Documentation Sentinel agent (e.g., `{"text": "...", "format": "..."}`).
4.  Call `mcpClient.SendRequestAsync("documentation_sentinel", agentParamsJson)`.
5.  Handle the `MCPResponse`. Check if `response.IsSuccess()` is true.
6.  If successful, deserialize the `response.result` JSON string into a C# object to access the generated documentation.
7.  Log the result or display it in the Unity UI.

**Expected Outcome:** The Unity Console should show a "Response Status: success" log, followed by the JSON result containing the generated documentation from the agent.

## 4. Troubleshooting

*   **Connection Errors:**
    *   Verify the Python MCP server is running and accessible from the machine running Unity.
    *   Check that the `Server Address` and `Server Port` configured in the `MCP_Client` component in Unity match the server's host and port.
    *   Ensure no firewall is blocking communication between Unity and the server.
*   **"AGENT_NOT_FOUND" errors:**
    *   Confirm that the `agent_id` string used in `SendRequestAsync` exactly matches an agent ID registered on the MCP server (e.g., "documentation_sentinel", "level_architect"). Check the server's startup logs for registered agents.
*   **"INVALID_PARAMETERS" errors:**
    *   Double-check that the JSON string you are passing as `jsonParameters` to `SendRequestAsync` is valid JSON and contains all the required parameters in the correct format expected by the target agent. Refer to the specific agent's documentation or code for expected parameters.
*   **JSON Parsing Errors (Client-Side in Unity):**
    *   If you encounter errors when using `JsonUtility.FromJson` or Newtonsoft.Json to deserialize `response.result`, inspect the raw `response.result` string in the Unity Console logs. Compare its structure to the C# class you are trying to deserialize it into. Ensure the JSON structure matches the C# class fields (including case sensitivity, depending on the deserializer).
    *   If the server is sending non-JSON data or an unexpected format, check the server logs for errors during response generation.
*   **Server-Side Errors (Check Python Console):**
    *   If requests fail with generic `EXECUTION_ERROR` or `INTERNAL_SERVER_ERROR`, check the console output of the running Python MCP server for detailed traceback information. This will help pinpoint issues within the agent execution or server logic.