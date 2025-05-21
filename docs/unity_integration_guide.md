# Unity Integration Guide

This guide explains how to integrate the Unity Agent MCP system with any Unity project, allowing you to use AI-driven game development tools for programming, scripting, scene creation, and world mapping.

## Prerequisites

- Unity 2022.3 LTS or newer
- Python 3.8+
- Git (optional, for cloning the repository)

## Installation

### Step 1: Set Up the MCP Server

1. Clone or download the Unity Agent MCP repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/unity-agent-mcp.git
   cd unity-agent-mcp
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the MCP server:
   ```bash
   python -m src.mcp_server.main
   ```

   The server will start on http://localhost:5001 by default.

### Step 2: Import the Unity Package

There are two ways to import the Unity package into your project:

#### Option 1: Using the Unity Package Manager (Recommended)

1. In Unity, open Window > Package Manager
2. Click the "+" button in the top-left corner
3. Select "Add package from disk..."
4. Navigate to the `unity-package/com.unity-agent-mcp.tgz` file in the repository
5. Click "Open" to import the package

#### Option 2: Manual Import

1. Copy the contents of the `unity-package` directory to your Unity project's `Packages/com.unity-agent-mcp` directory
2. Restart Unity or refresh the Package Manager

## Configuration

1. In Unity, open Window > Unity Agent MCP > Settings
2. Enter the MCP server URL (default: http://localhost:5001)
3. Click "Test Connection" to verify the connection
4. Click "Save Settings" to save the configuration

## Using the Agents

### Level Architect Agent

The Level Architect Agent helps you create and modify Unity scenes based on descriptions.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Level Architect" from the dropdown
3. Enter a prompt describing the scene you want to create or modify, for example:
   ```
   Create a medieval village with a central square, surrounded by 5-7 houses, a blacksmith shop, and a tavern. Include a small river running through the eastern side of the village.
   ```
4. Click "Send to Agent"
5. The agent will process your request and generate or modify the scene accordingly

### Code Weaver Agent

The Code Weaver Agent helps you generate and implement C# scripts for game logic.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Code Weaver" from the dropdown
3. Enter a prompt describing the script you want to create, for example:
   ```
   Create a player controller script that allows WASD movement, jumping with spacebar, and a dash ability with shift. Include adjustable parameters for movement speed, jump height, and dash distance.
   ```
4. Click "Send to Agent"
5. The agent will generate the script and place it in your project

### Documentation Sentinel Agent

The Documentation Sentinel Agent helps you manage documentation for your code and assets.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Documentation Sentinel" from the dropdown
3. Enter a prompt describing the documentation you need, for example:
   ```
   Generate documentation for the PlayerController script, including a description of each public method and parameter.
   ```
4. Click "Send to Agent"
5. The agent will generate the documentation and place it in your project

### Pixel Forge Agent

The Pixel Forge Agent helps you place and organize assets in your scenes.

1. Open Window > Unity Agent MCP > Agent Interface
2. Select "Pixel Forge" from the dropdown
3. Enter a prompt describing the asset placement you want, for example:
   ```
   Place trees around the perimeter of the current scene, with higher density on the north and east sides. Add some rocks and bushes scattered throughout.
   ```
4. Click "Send to Agent"
5. The agent will place the assets in your scene according to your description

## Advanced Usage

### Combining Agent Capabilities

You can combine the capabilities of multiple agents to create complex game elements. For example:

1. Use the Level Architect to create a basic scene structure
2. Use the Pixel Forge to populate the scene with assets
3. Use the Code Weaver to create scripts for interactive elements
4. Use the Documentation Sentinel to document the created elements

### Using with Existing Projects

The Unity Agent MCP system can be integrated with existing Unity projects of any size:

1. Import the Unity package as described above
2. Configure the MCP server connection
3. Use the agents to enhance specific parts of your project without disrupting existing work

### Remote Server Setup

For team environments, you can set up the MCP server on a remote machine:

1. Configure the server to listen on a specific IP address:
   ```bash
   export MCP_SERVER_HOST=0.0.0.0
   python -m src.mcp_server.main
   ```

2. In Unity, configure the MCP server URL to point to the remote server:
   ```
   http://your-server-ip:5001
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

## Best Practices

1. **Start Small**: Begin with simple prompts and gradually increase complexity as you become familiar with the system
2. **Be Specific**: Provide detailed descriptions in your prompts for better results
3. **Iterate**: Use the agents iteratively, refining their output with additional prompts
4. **Combine Agents**: Use different agents in sequence to create complex game elements
5. **Version Control**: Keep your project under version control to easily revert changes if needed

## Extending the System

The Unity Agent MCP system is designed to be extensible. You can:

1. Add new agents for specific tasks
2. Enhance existing agents with new capabilities
3. Integrate with additional Unity packages and tools
4. Create custom workflows combining multiple agents

For more information on extending the system, see the [Developer Guide](developer_guide.md).