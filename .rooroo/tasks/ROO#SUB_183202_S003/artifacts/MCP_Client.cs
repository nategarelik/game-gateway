using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Rooroo.MCP
{
    /// <summary>
    /// Represents the request payload to be sent to the MCP server.
    /// </summary>
    [Serializable]
    public class MCPRequest
    {
        public string task_id;
        public string agent_id;
        public string parameters; // JSON string for agent-specific parameters

        public MCPRequest(string taskId, string agentId, string jsonParameters)
        {
            this.task_id = taskId;
            this.agent_id = agentId;
            this.parameters = jsonParameters;
        }
    }

    /// <summary>
    /// Represents the error details in an MCP response.
    /// </summary>
    [Serializable]
    public class MCPErrorDetails
    {
        public string code;
        public string message;
        // public string details; // JsonUtility struggles with deeply nested generic objects.
                               // If 'details' is a complex object, it might also need to be a JSON string.
                               // For now, assuming it's simple or not always present / critical for client.
    }

    /// <summary>
    /// Represents the response payload received from the MCP server.
    /// </summary>
    [Serializable]
    public class MCPResponse
    {
        public string task_id;
        public string status;
        public string result; // JSON string for agent-specific results
        public MCPErrorDetails error;

        public bool IsSuccess()
        {
            return status != null && status.Equals("success", StringComparison.OrdinalIgnoreCase);
        }
    }

    /// <summary>
    /// Unity MonoBehaviour client for communicating with the Python MCP server.
    /// Handles sending requests and receiving responses asynchronously.
    /// </summary>
    public class MCP_Client : MonoBehaviour
    {
        [Header("MCP Server Configuration")]
        public string serverAddress = "127.0.0.1";
        public int serverPort = 5001;
        public string apiEndpoint = "/execute_agent";

        private string GetServerUrl()
        {
            return $"http://{serverAddress}:{serverPort}{apiEndpoint}";
        }

        /// <summary>
        /// Sends a request to the MCP server asynchronously.
        /// </summary>
        /// <param name="agentId">The ID of the target agent or toolchain.</param>
        /// <param name="parameters">A JSON string representing the parameters for the agent.</param>
        /// <param name="taskId">Optional task ID. If null or empty, a new GUID will be generated.</param>
        /// <returns>A Task that resolves to an MCPResponse object.</returns>
        public async Task<MCPResponse> SendRequestAsync(string agentId, string jsonParameters, string taskId = null)
        {
            if (string.IsNullOrEmpty(taskId))
            {
                taskId = Guid.NewGuid().ToString();
            }

            MCPRequest mcpRequest = new MCPRequest(taskId, agentId, jsonParameters);
            string jsonRequestBody = JsonUtility.ToJson(mcpRequest);

            string url = GetServerUrl();
            Debug.Log($"[MCP_Client] Sending request to {url} with body: {jsonRequestBody}");

            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonRequestBody);
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                webRequest.SetRequestHeader("Content-Type", "application/json");

                var operation = webRequest.SendWebRequest();

                while (!operation.isDone)
                {
                    await Task.Yield(); // Allow Unity to continue processing other tasks
                }

                if (webRequest.result == UnityWebRequest.Result.ConnectionError ||
                    webRequest.result == UnityWebRequest.Result.ProtocolError ||
                    webRequest.result == UnityWebRequest.Result.DataProcessingError)
                {
                    Debug.LogError($"[MCP_Client] Error: {webRequest.error} - Response Code: {webRequest.responseCode}");
                    Debug.LogError($"[MCP_Client] Response Body: {webRequest.downloadHandler.text}");
                    // Construct a synthetic error response
                    return new MCPResponse
                    {
                        task_id = taskId,
                        status = "failed",
                        result = null,
                        error = new MCPErrorDetails
                        {
                            code = webRequest.result.ToString().ToUpperInvariant(),
                            message = webRequest.error + (string.IsNullOrEmpty(webRequest.downloadHandler.text) ? "" : $" | Server Response: {webRequest.downloadHandler.text}")
                        }
                    };
                }
                else
                {
                    string jsonResponse = webRequest.downloadHandler.text;
                    Debug.Log($"[MCP_Client] Received response: {jsonResponse}");
                    try
                    {
                        MCPResponse mcpResponse = JsonUtility.FromJson<MCPResponse>(jsonResponse);
                        if (mcpResponse == null) // JsonUtility returns null on failure
                        {
                             Debug.LogError($"[MCP_Client] Failed to parse JSON response: {jsonResponse}");
                             return new MCPResponse {
                                task_id = taskId, status = "failed", result = null,
                                error = new MCPErrorDetails { code = "JSON_PARSE_ERROR", message = "Failed to parse server response."}
                             };
                        }
                        return mcpResponse;
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[MCP_Client] Exception parsing JSON response: {e.Message} - JSON: {jsonResponse}");
                        return new MCPResponse
                        {
                            task_id = taskId,
                            status = "failed",
                            result = null,
                            error = new MCPErrorDetails { code = "JSON_PARSE_EXCEPTION", message = e.Message }
                        };
                    }
                }
            }
        }

        // --- Example Usage ---
        [ContextMenu("Test Send Ping Request (Level Architect)")]
        public async void TestSendPingRequest()
        {
            // Example: Sending a simple request to 'level_architect'
            // The parameters here would depend on what 'level_architect' expects.
            // For a "ping" or basic check, it might accept empty or minimal parameters.
            // We'll use a simple JSON object string.
            // For real use, you'd construct this JSON string from your actual parameter objects.
            // e.g., using Newtonsoft.Json: JsonConvert.SerializeObject(new { level_type = "test" })
            // or for JsonUtility, a serializable class: JsonUtility.ToJson(new MyLevelParams { level_type = "test" })

            string exampleParametersJson = "{\"level_type\":\"dungeon\",\"complexity\":\"low\",\"seed\":123}";
            string agentToTest = "level_architect"; // Ensure this agent is running on the server

            Debug.Log($"[MCP_Client_Test] Sending test request to agent: {agentToTest}");
            MCPResponse response = await SendRequestAsync(agentToTest, exampleParametersJson, "test_ping_001");

            if (response != null)
            {
                Debug.Log($"[MCP_Client_Test] Response Task ID: {response.task_id}");
                Debug.Log($"[MCP_Client_Test] Response Status: {response.status}");

                if (response.IsSuccess())
                {
                    Debug.Log($"[MCP_Client_Test] Response Result (JSON String): {response.result}");
                    // Here you would typically deserialize response.result into a specific C# object
                    // e.g., MyLevelData levelData = JsonUtility.FromJson<MyLevelData>(response.result);
                    // or using Newtonsoft.Json: MyLevelData levelData = JsonConvert.DeserializeObject<MyLevelData>(response.result);
                }
                else
                {
                    if (response.error != null)
                    {
                        Debug.LogError($"[MCP_Client_Test] Error Code: {response.error.code}");
                        Debug.LogError($"[MCP_Client_Test] Error Message: {response.error.message}");
                    }
                    else
                    {
                        Debug.LogError("[MCP_Client_Test] Request failed, but no error details provided in response.");
                    }
                }
            }
            else
            {
                Debug.LogError("[MCP_Client_Test] No response received or failed to parse.");
            }
        }
    }
}