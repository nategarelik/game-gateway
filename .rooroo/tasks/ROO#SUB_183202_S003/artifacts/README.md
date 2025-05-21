# Unity MCP Client (MCP_Client.cs)

Task ID: `ROO#SUB_183202_S003`

This document provides instructions on how to integrate and use the `MCP_Client.cs` script in your Unity project to communicate with the Python MCP (Multi-Agent Control Plane) server.

## 1. Overview

`MCP_Client.cs` is a Unity MonoBehaviour script that facilitates communication with the MCP server using HTTP RESTful API calls. It allows Unity to send requests to specific AI agents or toolchains managed by the MCP server and receive their responses asynchronously.

The communication protocol uses JSON for data exchange.

## 2. Integration into Unity

1.  **Copy Script:** Place the `MCP_Client.cs` file into your Unity project's `Assets` folder (or a subfolder like `Assets/Scripts`).
2.  **Create GameObject:**
    *   In your Unity scene, create an empty GameObject (e.g., name it "MCPClientManager").
    *   Attach the `MCP_Client.cs` script to this GameObject.
3.  **Configure Client:**
    *   Select the "MCPClientManager" GameObject in the Hierarchy.
    *   In the Inspector panel, you will see the `MCP_Client` component with the following configurable fields:
        *   **Server Address:** The IP address or hostname of the MCP server (default: `127.0.0.1`).
        *   **Server Port:** The port number the MCP server is listening on (default: `5001`).
        *   **API Endpoint:** The specific path for the agent execution endpoint on the server (default: `/execute_agent`).
    *   Adjust these settings if your MCP server is running on a different address or port.

## 3. Script Structure

The `MCP_Client.cs` script defines the following key classes:

*   **`MCPRequest`**: Represents the JSON payload sent to the server.
    *   `task_id` (string): A unique identifier for the request.
    *   `agent_id` (string): The ID of the target agent or toolchain.
    *   `parameters` (string): A JSON string containing agent-specific parameters.
*   **`MCPErrorDetails`**: Represents error information if a request fails.
    *   `code` (string): An error code.
    *   `message` (string): A human-readable error message.
*   **`MCPResponse`**: Represents the JSON payload received from the server.
    *   `task_id` (string): The ID from the corresponding request.
    *   `status` (string): "success" or "failed".
    *   `result` (string): A JSON string containing agent-specific results (if successful).
    *   `error` (`MCPErrorDetails`): Error details (if failed).
*   **`MCP_Client` (MonoBehaviour)**: The main client class.
    *   `SendRequestAsync(string agentId, string jsonParameters, string taskId = null)`: Asynchronously sends a request to the server.
        *   `agentId`: The ID of the agent/toolchain to call.
        *   `jsonParameters`: The parameters for the agent, formatted as a JSON string.
            *   **Note on `jsonParameters` and `result`:** Due to limitations with Unity's built-in `JsonUtility` (especially with dictionaries and complex nested objects), the `parameters` field in `MCPRequest` and the `result` field in `MCPResponse` are handled as raw JSON strings. You are responsible for serializing your C# parameter objects into a JSON string before calling `SendRequestAsync`, and deserializing the `result` JSON string back into appropriate C# objects upon receiving a successful response. For more complex JSON, consider using a library like Newtonsoft.Json (available via UPM or .dll).
        *   `taskId`: Optional. If not provided, a new GUID is generated.
    *   `TestSendPingRequest()`: An example method (accessible via Context Menu in Inspector) that demonstrates sending a request to the "level_architect" agent.

## 4. How to Use

1.  **Get a Reference:** In your other Unity scripts, get a reference to the `MCP_Client` instance.
    ```csharp
    // In your other script
    using UnityEngine;
    using Rooroo.MCP; // Assuming MCP_Client.cs is in a Rooroo.MCP namespace
    using System.Threading.Tasks; // For async/await

    public class MyGameController : MonoBehaviour
    {
        public MCP_Client mcpClient; // Assign in Inspector or find via code

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
            // Example: Call an agent on start
            await CallMyAgent();
        }

        public async Task CallMyAgent()
        {
            // 1. Prepare parameters as a JSON string
            // Example: If your agent expects {"settingA": "value1", "settingB": 100}
            // Using a simple manual string for this example:
            string agentParamsJson = "{\"settingA\": \"value1\", \"settingB\": 100}";

            // For more complex objects, serialize them:
            // MyAgentParams myParams = new MyAgentParams { settingA = "value1", settingB = 100 };
            // string agentParamsJson = JsonUtility.ToJson(myParams); // If MyAgentParams is [Serializable]
            // Or using Newtonsoft.Json:
            // string agentParamsJson = Newtonsoft.Json.JsonConvert.SerializeObject(myParams);

            string agentIdToCall = "level_architect"; // Or any other agent_id configured on your MCP server

            Debug.Log($"Attempting to call agent: {agentIdToCall}");
            MCPResponse response = await mcpClient.SendRequestAsync(agentIdToCall, agentParamsJson);

            if (response != null)
            {
                Debug.Log($"Response Status: {response.status}");
                if (response.IsSuccess())
                {
                    Debug.Log($"Agent Result (JSON): {response.result}");
                    // 2. Deserialize response.result if needed
                    // Example: MyAgentResult resultData = JsonUtility.FromJson<MyAgentResult>(response.result);
                    // Or using Newtonsoft.Json:
                    // MyAgentResult resultData = Newtonsoft.Json.JsonConvert.DeserializeObject<MyAgentResult>(response.result);
                    // Process resultData...
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

2.  **Call `SendRequestAsync`:**
    *   Use the `await` keyword to call `mcpClient.SendRequestAsync(...)` from an `async` method.
    *   Provide the `agentId` and the `jsonParameters` string.
    *   Handle the returned `MCPResponse` object. Check `response.status` and `response.IsSuccess()`.
    *   If successful, `response.result` will contain the JSON string from the agent. Deserialize it as needed.
    *   If failed, `response.error` will contain details about the error.

## 5. Example Test

The `MCP_Client.cs` script includes a `TestSendPingRequest()` method.
1.  Ensure your MCP server is running and accessible.
2.  Ensure an agent with ID "level_architect" is registered and can handle a request with parameters like `{"level_type":"dungeon","complexity":"low","seed":123}` (or modify the test parameters).
3.  Select the GameObject with the `MCP_Client` script in the Unity Editor.
4.  In the Inspector, right-click on the `MCP_Client` component's title bar (or the three dots menu) and select "Test Send Ping Request (Level Architect)".
5.  Check the Unity Console for log messages indicating the request and response.

## 6. Dependencies

*   Unity Engine (tested with Unity 2021.3 LTS, but should be compatible with newer versions supporting `UnityWebRequest` and `async/await`).
*   No external C# libraries are strictly required by `MCP_Client.cs` itself for its core functionality (it uses `JsonUtility`). However, for more robust JSON serialization/deserialization of complex `parameters` and `result` objects, you might consider adding a library like **Newtonsoft.Json**.

## 7. Troubleshooting

*   **Connection Errors:**
    *   Verify the MCP server is running.
    *   Check that `Server Address` and `Server Port` in the `MCP_Client` component match the server's configuration.
    *   Ensure no firewall is blocking communication between Unity and the server.
*   **"AGENT_NOT_FOUND" errors:**
    *   Confirm the `agent_id` you are trying to call exists and is correctly registered on the MCP server.
*   **"INVALID_PARAMETERS" errors:**
    *   Double-check that the `jsonParameters` string you are sending is valid JSON and matches the format expected by the target agent.
*   **JSON Parsing Errors (Client-Side):**
    *   If `JsonUtility.FromJson<MCPResponse>(...)` fails, the server might be sending an invalid JSON structure or non-JSON data. Check server logs.
    *   If deserializing `response.result` fails, ensure your C# target class structure matches the JSON structure in `response.result`.
*   **Unity Editor Freezing (should not happen):**
    *   The client uses `async/await` and `UnityWebRequest.SendWebRequest()` which is non-blocking. If freezes occur, it might indicate an issue elsewhere or an extremely long-running synchronous operation on the server blocking the response.