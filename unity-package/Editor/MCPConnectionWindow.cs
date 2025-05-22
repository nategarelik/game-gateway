using UnityEngine;
using UnityEditor;
using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace UnityAgentMCP.Editor
{
    public class MCPConnectionWindow : EditorWindow
    {
        private string serverUrl = "http://127.0.0.1:8000/api/v1";
        private string connectionStatus = "Not connected";
        private bool isConnected = false;

        [MenuItem("Window/Unity Agent MCP/Settings")]
        public static void ShowWindow()
        {
            GetWindow<MCPConnectionWindow>("MCP Settings");
        }

        void OnGUI()
        {
            GUILayout.Label("MCP Server Connection", EditorStyles.boldLabel);

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.PrefixLabel("Server URL");
            serverUrl = EditorGUILayout.TextField(serverUrl);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space();

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.PrefixLabel("Status");
            EditorGUILayout.LabelField(connectionStatus);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space();

            if (GUILayout.Button("Test Connection"))
            {
                TestConnection();
            }

            EditorGUILayout.Space();

            GUI.enabled = isConnected;
            if (GUILayout.Button("Save Settings"))
            {
                SaveSettings();
            }
            GUI.enabled = true;
        }

        private async void TestConnection()
        {
            connectionStatus = "Testing connection...";
            Repaint();

            try
            {
                using (HttpClient client = new HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(5);
                    
                    // First test if server is reachable
                    HttpResponseMessage pingResponse = await client.GetAsync(serverUrl.TrimEnd('/') + "/");
                    
                    if (!pingResponse.IsSuccessStatusCode)
                    {
                        string errorContent = await pingResponse.Content.ReadAsStringAsync();
                        connectionStatus = $"Server error: {pingResponse.StatusCode} - {errorContent}";
                        isConnected = false;
                        Repaint();
                        return;
                    }
                    
                    // Test the API endpoint specifically
                    HttpResponseMessage apiResponse = await client.GetAsync(serverUrl.TrimEnd('/'));
                    
                    if (apiResponse.IsSuccessStatusCode)
                    {
                        string content = await apiResponse.Content.ReadAsStringAsync();
                        connectionStatus = "Connected successfully";
                        isConnected = true;
                    }
                    else
                    {
                        string errorContent = await apiResponse.Content.ReadAsStringAsync();
                        connectionStatus = $"API error: {apiResponse.StatusCode} - {errorContent}";
                        isConnected = false;
                    }
                }
            }
            catch (HttpRequestException httpEx)
            {
                connectionStatus = $"Network error: {httpEx.Message}";
                if (httpEx.InnerException != null)
                {
                    connectionStatus += $" (Inner: {httpEx.InnerException.Message})";
                }
                isConnected = false;
            }
            catch (TaskCanceledException)
            {
                connectionStatus = "Connection timed out. Check if the MCP server is running.";
                isConnected = false;
            }
            catch (Exception ex)
            {
                connectionStatus = $"Error: {ex.GetType().Name} - {ex.Message}";
                isConnected = false;
            }

            Repaint();
        }

        private void SaveSettings()
        {
            EditorPrefs.SetString("MCPServerURL", serverUrl);
            Debug.Log("MCP settings saved");
        }
    }
}