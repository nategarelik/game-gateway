# Unity Package Structure

This document outlines the structure and contents of the Unity package for the Autonomous AI Agent Ecosystem. The package allows Unity developers to integrate with the MCP server and utilize the AI agents for game development tasks.

## Directory Structure

```
unity-package/
├── Editor/
│   ├── MCPConnectionWindow.cs
│   ├── AgentInterfaceWindow.cs
│   └── UnityAgentMCP.Editor.asmdef
├── Runtime/
│   ├── MCPClient.cs
│   └── UnityAgentMCP.Runtime.asmdef
├── package.json
└── README.md
```

## File Contents

### package.json

```json
{
  "name": "com.unity-agent-mcp",
  "version": "1.0.0",
  "displayName": "Unity Agent MCP",
  "description": "Integration package for the Autonomous AI Agent Ecosystem for Unity Game Development",
  "unity": "2022.3",
  "dependencies": {},
  "keywords": [
    "ai",
    "agent",
    "mcp",
    "game development"
  ],
  "author": {
    "name": "Unity Agent MCP Team",
    "email": "example@example.com",
    "url": "https://github.com/YOUR_USERNAME/unity-agent-mcp"
  }
}
```

### Editor/MCPConnectionWindow.cs

This file implements a Unity Editor window for configuring the connection to the MCP server. Key features:

- Server URL configuration
- Connection testing
- Settings persistence using EditorPrefs

```csharp
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
            // UI implementation for server configuration
            // Connection testing functionality
            // Settings persistence
        }
    }
}
```

### Editor/AgentInterfaceWindow.cs

This file implements a Unity Editor window for interacting with the AI agents. Key features:

- Agent selection (Level Architect, Code Weaver, Documentation Sentinel, Pixel Forge)
- Prompt input
- Response display

```csharp
using UnityEngine;
using UnityEditor;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace UnityAgentMCP.Editor
{
    public class AgentInterfaceWindow : EditorWindow
    {
        private string[] agentTypes = new string[] { "Level Architect", "Code Weaver", "Documentation Sentinel", "Pixel Forge" };
        private int selectedAgentIndex = 0;
        private string prompt = "";
        private string response = "";

        [MenuItem("Window/Unity Agent MCP/Agent Interface")]
        public static void ShowWindow()
        {
            GetWindow<AgentInterfaceWindow>("MCP Agents");
        }

        void OnGUI()
        {
            // UI implementation for agent interaction
            // Communication with MCP server
        }
    }
}
```

### Runtime/MCPClient.cs

This file implements a runtime client for communicating with the MCP server from Unity games. Key features:

- Singleton pattern for easy access
- Asynchronous communication with MCP server
- Request/response handling

```csharp
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
                // Singleton implementation
            }
        }

        public async Task<string> SendRequest(string agentId, Dictionary<string, object> parameters)
        {
            // Implementation for sending requests to MCP server
        }
    }
}
```

### Assembly Definition Files

#### Editor/UnityAgentMCP.Editor.asmdef

```json
{
    "name": "UnityAgentMCP.Editor",
    "rootNamespace": "UnityAgentMCP.Editor",
    "references": [
        "UnityAgentMCP.Runtime"
    ],
    "includePlatforms": [
        "Editor"
    ],
    "excludePlatforms": [],
    "allowUnsafeCode": false,
    "overrideReferences": false,
    "precompiledReferences": [],
    "autoReferenced": true,
    "defineConstraints": [],
    "versionDefines": [],
    "noEngineReferences": false
}
```

#### Runtime/UnityAgentMCP.Runtime.asmdef

```json
{
    "name": "UnityAgentMCP.Runtime",
    "rootNamespace": "UnityAgentMCP",
    "references": [],
    "includePlatforms": [],
    "excludePlatforms": [],
    "allowUnsafeCode": false,
    "overrideReferences": false,
    "precompiledReferences": [],
    "autoReferenced": true,
    "defineConstraints": [],
    "versionDefines": [],
    "noEngineReferences": false
}
```

## Integration Steps

1. Create the directory structure as outlined above
2. Create each file with the specified content
3. Package the Unity package:
   - In Unity, select Assets > Export Package
   - Select all files in the unity-package directory
   - Export as `com.unity-agent-mcp.unitypackage`
4. Alternatively, use the Unity Package Manager format:
   - Compress the unity-package directory as a tarball (tgz)
   - Rename to `com.unity-agent-mcp.tgz`

## Usage in Unity Projects

To use this package in a Unity project:

1. In Unity, go to Window > Package Manager
2. Click '+' > Add package from disk
3. Select the `com.unity-agent-mcp.tgz` file
4. Access the tools via Window > Unity Agent MCP