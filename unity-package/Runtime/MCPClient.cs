using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

namespace UnityAgentMCP
{
    public class MCPClient : MonoBehaviour
    {
        private static MCPClient _instance;
        private HttpClient httpClient;

        public static MCPClient Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("MCPClient");
                    _instance = go.AddComponent<MCPClient>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);
            httpClient = new HttpClient();
        }

        public async Task<string> SendRequest(string agentId, Dictionary<string, object> parameters)
        {
            string serverUrl = GetServerUrl();
            if (string.IsNullOrEmpty(serverUrl))
            {
                Debug.LogError("MCP Server URL not configured");
                return "Error: MCP Server URL not configured";
            }

            try
            {
                var requestData = new Dictionary<string, object>
                {
                    { "task_id", Guid.NewGuid().ToString() },
                    { "agent_id", agentId },
                    { "parameters", parameters }
                };

                string json = JsonUtility.ToJson(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{serverUrl}/execute_agent", content);
                string responseContent = await response.Content.ReadAsStringAsync();
                
                if (response.IsSuccessStatusCode)
                {
                    return responseContent;
                }
                else
                {
                    Debug.LogError($"MCP request failed: {response.StatusCode}\n{responseContent}");
                    return $"Error: {response.StatusCode}\n{responseContent}";
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"MCP request exception: {ex.Message}");
                return $"Error: {ex.Message}";
            }
        }

        private string GetServerUrl()
        {
            #if UNITY_EDITOR
            return UnityEditor.EditorPrefs.GetString("MCPServerURL", "http://localhost:5001");
            #else
            return PlayerPrefs.GetString("MCPServerURL", "http://localhost:5001");
            #endif
        }
    }
}