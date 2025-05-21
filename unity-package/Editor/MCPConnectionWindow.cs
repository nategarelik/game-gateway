using UnityEngine;
using UnityEditor;
using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace UnityAgentMCP.Editor
{
    public class MCPConnectionWindow : EditorWindow
    {
        private string serverUrl = "http://localhost:5001";
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
                    HttpResponseMessage response = await client.GetAsync(serverUrl);
                    
                    if (response.IsSuccessStatusCode)
                    {
                        connectionStatus = "Connected successfully";
                        isConnected = true;
                    }
                    else
                    {
                        connectionStatus = $"Connection failed: {response.StatusCode}";
                        isConnected = false;
                    }
                }
            }
            catch (Exception ex)
            {
                connectionStatus = $"Connection error: {ex.Message}";
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