using UnityEngine;
using UnityEditor;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace UnityAgentMCP.Editor
{
    public class AgentInterfaceWindow : EditorWindow
    {
        private string[] agentTypes = new string[] { "Level Architect", "Code Weaver", "Documentation Sentinel", "Pixel Forge", "Orchestrator" };
        private int selectedAgentIndex = 0;
        private string prompt = "";
        private string response = "";
        private bool isProcessing = false;

        [MenuItem("Window/Unity Agent MCP/Agent Interface")]
        public static void ShowWindow()
        {
            GetWindow<AgentInterfaceWindow>("MCP Agents");
        }

        void OnGUI()
        {
            GUILayout.Label("Unity Agent MCP Interface", EditorStyles.boldLabel);

            EditorGUILayout.Space();

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.PrefixLabel("Agent Type");
            selectedAgentIndex = EditorGUILayout.Popup(selectedAgentIndex, agentTypes);
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.Space();

            EditorGUILayout.LabelField("Prompt");
            prompt = EditorGUILayout.TextArea(prompt, GUILayout.Height(100));

            EditorGUILayout.Space();

            GUI.enabled = !isProcessing && !string.IsNullOrEmpty(prompt);
            if (GUILayout.Button("Send to Agent"))
            {
                SendPromptToAgent();
            }
            GUI.enabled = true;

            EditorGUILayout.Space();

            EditorGUILayout.LabelField("Response");
            EditorGUILayout.TextArea(response, GUILayout.Height(200));
        }

        private async void SendPromptToAgent()
        {
            if (string.IsNullOrEmpty(EditorPrefs.GetString("MCPServerURL")))
            {
                response = "Error: MCP Server URL not configured. Please set it in Window > Unity Agent MCP > Settings";
                return;
            }

            string serverUrl = EditorPrefs.GetString("MCPServerURL");
            string agentId = GetAgentId();

            isProcessing = true;
            response = "Processing request...";
            Repaint();

            try
            {
                using (HttpClient client = new HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(30);
                    
                    var requestData = new Dictionary<string, object>
                    {
                        { "task_id", Guid.NewGuid().ToString() },
                        { "agent_id", agentId },
                        { "parameters", new Dictionary<string, object>
                            {
                                { "prompt", prompt },
                                { "scene_name", UnityEngine.SceneManagement.SceneManager.GetActiveScene().name }
                            }
                        }
                    };

                    string json = JsonUtility.ToJson(requestData);
                    var content = new StringContent(json, Encoding.UTF8, "application/json");

                    HttpResponseMessage httpResponse = await client.PostAsync($"{serverUrl}/execute_agent", content);
                    string responseContent = await httpResponse.Content.ReadAsStringAsync();
                    
                    if (httpResponse.IsSuccessStatusCode)
                    {
                        response = responseContent;
                    }
                    else
                    {
                        response = $"Error: {httpResponse.StatusCode}\n{responseContent}";
                    }
                }
            }
            catch (Exception ex)
            {
                response = $"Error: {ex.Message}";
            }

            isProcessing = false;
            Repaint();
        }

        private string GetAgentId()
        {
            switch (selectedAgentIndex)
            {
                case 0: return "level_architect";
                case 1: return "code_weaver";
                case 2: return "documentation_sentinel";
                case 3: return "pixel_forge";
                case 4: return "orchestrator";
                default: return "orchestrator"; // Fallback
            }
        }
    }
}
