# Unity Agent MCP Package

This package provides Unity integration for the Autonomous AI Agent Ecosystem, allowing you to use AI-driven game development tools for programming, scripting, scene creation, and world mapping.

## Installation

### Option 1: Package Manager (Recommended)

1. In Unity, open Window > Package Manager
2. Click '+' > Add package from disk
3. Select the `com.unity-agent-mcp.tgz` file

### Option 2: Manual Installation

1. Copy the contents of this directory to your Unity project's `Packages/com.unity-agent-mcp` directory

## Prerequisites

- Unity 2022.3 LTS or newer
- Running MCP server (see the main repository README for setup instructions)

## Features

- **MCP Connection**: Configure and test the connection to the MCP server
- **Agent Interface**: Interact with specialized AI agents
- **Runtime Integration**: Use the MCP system at runtime in your games

## Getting Started

1. After installing the package, open Window > Unity Agent MCP > Settings
2. Enter the MCP server URL (default: http://localhost:5001)
3. Click "Test Connection" to verify the connection
4. Click "Save Settings" to save the configuration

## Using the Agents

### Level Architect Agent

The Level Architect Agent helps you create and modify Unity scenes based on descriptions.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Level Architect" from the dropdown
3. Enter a prompt describing the scene you want to create or modify
4. Click "Send to Agent"

Example prompt:
```
Create a medieval village with a central square, surrounded by 5-7 houses, a blacksmith shop, and a tavern. Include a small river running through the eastern side of the village.
```

### Code Weaver Agent

The Code Weaver Agent helps you generate and implement C# scripts for game logic.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Code Weaver" from the dropdown
3. Enter a prompt describing the script you want to create
4. Click "Send to Agent"

Example prompt:
```
Create a player controller script that allows WASD movement, jumping with spacebar, and a dash ability with shift. Include adjustable parameters for movement speed, jump height, and dash distance.
```

### Documentation Sentinel Agent

The Documentation Sentinel Agent helps you manage documentation for your code and assets.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Documentation Sentinel" from the dropdown
3. Enter a prompt describing the documentation you need
4. Click "Send to Agent"

Example prompt:
```
Generate documentation for the PlayerController script, including a description of each public method and parameter.
```

### Pixel Forge Agent

The Pixel Forge Agent helps you place and organize assets in your scenes.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Pixel Forge" from the dropdown
3. Enter a prompt describing the asset placement you want
4. Click "Send to Agent"

Example prompt:
```
Place trees around the perimeter of the current scene, with higher density on the north and east sides. Add some rocks and bushes scattered throughout.
```

## Runtime Integration

To use the MCP system at runtime in your games:

1. Add the `MCPClient` component to a GameObject in your scene
2. Use the `MCPClient.Instance.SendRequest` method to send requests to the MCP server

Example:
```csharp
using UnityEngine;
using System.Collections.Generic;
using UnityAgentMCP;

public class ExampleScript : MonoBehaviour
{
    public async void GenerateLevel()
    {
        var parameters = new Dictionary<string, object>
        {
            { "prompt", "Generate a small dungeon with 5-7 rooms, including a treasure room and a boss room." },
            { "scene_name", UnityEngine.SceneManagement.SceneManager.GetActiveScene().name }
        };

        string response = await MCPClient.Instance.SendRequest("level_architect", parameters);
        Debug.Log("Response: " + response);
    }
}
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the MCP server:

1. Ensure the server is running
2. Check that the URL in the Unity settings is correct
3. Verify that there are no firewall issues blocking the connection
4. Check the server logs for any error messages

### Agent Response Issues

If an agent is not responding as expected:

1. Check that your prompt is clear and specific
2. Ensure that the necessary assets or scripts are available in your project
3. Check the Unity console for any error messages
4. Restart the MCP server and try again

## API Reference

### MCPClient

The `MCPClient` class provides methods for communicating with the MCP server.

#### Properties

- `Instance`: Gets the singleton instance of the MCPClient.

#### Methods

- `SendRequest(string agentId, Dictionary<string, object> parameters)`: Sends a request to the specified agent with the given parameters.

### Editor Windows

#### MCPConnectionWindow

The `MCPConnectionWindow` class provides a Unity Editor window for configuring the connection to the MCP server.

- Menu Item: Window > Unity Agent MCP > Settings

#### AgentInterfaceWindow

The `AgentInterfaceWindow` class provides a Unity Editor window for interacting with the AI agents.

- Menu Item: Window > Unity Agent MCP > Agent Interface

## License

This package is licensed under the MIT License. See the LICENSE file in the main repository for details.