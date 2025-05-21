# Development Setup Guide

This guide provides instructions for setting up a development environment for the Unity Agent MCP project.

## Prerequisites

- Python 3.8+
- Unity 2022.3 LTS or newer
- Git
- npm (for packaging the Unity package)

## Setting Up the Python Environment

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/unity-agent-mcp.git
cd unity-agent-mcp
```

### 2. Create a Virtual Environment

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

## Setting Up Unity

### 1. Install Unity

If you don't already have Unity installed, download and install Unity Hub from the [Unity website](https://unity.com/download), then install Unity 2022.3 LTS or newer.

### 2. Create a Test Unity Project

1. Open Unity Hub
2. Click "New Project"
3. Select "3D" template
4. Name the project "UnityAgentMCP-Test"
5. Click "Create Project"

### 3. Import the Unity Package

#### Option 1: Using the Unity Package Manager

1. In Unity, open Window > Package Manager
2. Click the "+" button in the top-left corner
3. Select "Add package from disk..."
4. Navigate to the `unity-package/com.unity-agent-mcp.tgz` file in the repository
5. Click "Open" to import the package

#### Option 2: Manual Import

1. Copy the contents of the `unity-package` directory to your Unity project's `Packages/com.unity-agent-mcp` directory
2. Restart Unity or refresh the Package Manager

## Running the MCP Server

### 1. Start the MCP Server

```bash
python -m src.mcp_server.main
```

The server will start on http://localhost:5001 by default.

### 2. Configure the Unity Connection

1. In Unity, open Window > Unity Agent MCP > Settings
2. Enter the MCP server URL (default: http://localhost:5001)
3. Click "Test Connection" to verify the connection
4. Click "Save Settings" to save the configuration

## Development Workflow

### Python Development

1. Make changes to the Python code in the `src` directory
2. Run tests to ensure your changes don't break existing functionality:
   ```bash
   python -m pytest tests/
   ```
3. Run the MCP server to test your changes:
   ```bash
   python -m src.mcp_server.main
   ```

### Unity Development

1. Make changes to the Unity code in the `unity-package` directory
2. Test your changes in the Unity Editor
3. Package the Unity package for distribution:
   ```bash
   python scripts/package_unity_integration.py
   ```

## Code Structure

### Python Code

- `src/agents/`: Agent implementations
  - `base_agent.py`: Base class for all agents
  - `level_architect_agent.py`: Level Architect agent implementation
  - `code_weaver_agent.py`: Code Weaver agent implementation
  - `documentation_sentinel_agent.py`: Documentation Sentinel agent implementation
  - `pixel_forge_agent.py`: Pixel Forge agent implementation
- `src/mcp_server/`: MCP server implementation
  - `server_core.py`: Core server implementation
  - `main.py`: Server entry point
  - `core/`: Core server components
    - `prompt_registry.py`: Prompt template registry
    - `state_manager.py`: State management
    - `server.py`: Server implementation
  - `api/`: API endpoints
    - `routes.py`: API route definitions
  - `models/`: Data models
    - `api_models.py`: API data models
    - `game_dev_state.py`: Game development state model
    - `managed_task_state.py`: Task state model
- `src/protocols/`: Communication protocols
  - `advanced_collaboration_protocols.py`: Multi-agent collaboration protocols
  - `emergent_behavior_protocols.py`: Emergent behavior protocols
- `src/systems/`: System components
  - `extensibility_integration.py`: Extensibility and integration system
  - `knowledge_management_system.py`: Knowledge management system
  - `style_enforcement_system.py`: Style enforcement system
- `src/toolchains/`: Toolchain integrations
  - `base_toolchain_bridge.py`: Base class for toolchain bridges
  - `muse_bridge.py`: Unity Muse integration
  - `retro_diffusion_bridge.py`: Retro Diffusion integration
  - `unity_bridge.py`: Unity Editor integration
- `src/workflows/`: Workflow definitions
  - `autonomous_iteration.py`: Autonomous iteration workflow

### Unity Code

- `unity-package/Editor/`: Unity Editor scripts
  - `MCPConnectionWindow.cs`: MCP connection configuration window
  - `AgentInterfaceWindow.cs`: Agent interface window
- `unity-package/Runtime/`: Unity runtime scripts
  - `MCPClient.cs`: MCP client for runtime communication

## Testing

### Running Python Tests

```bash
python -m pytest tests/
```

### Running Unity Tests

1. In Unity, open Window > General > Test Runner
2. Select "EditMode" or "PlayMode" tab
3. Click "Run All" to run all tests

## Debugging

### Debugging the MCP Server

1. Add print statements or use a debugger to debug the MCP server
2. Check the server logs for error messages
3. Use the `--debug` flag to enable debug logging:
   ```bash
   python -m src.mcp_server.main --debug
   ```

### Debugging Unity Integration

1. Use Unity's Debug.Log to log messages
2. Check the Unity Console for error messages
3. Use the Unity Debugger to debug C# code

## Common Issues

### MCP Server Won't Start

- Check that the port is not in use by another application
- Ensure all dependencies are installed
- Check for syntax errors in the code

### Unity Can't Connect to MCP Server

- Ensure the MCP server is running
- Check that the URL in the Unity settings is correct
- Verify that there are no firewall issues blocking the connection

### Agent Not Responding

- Check that the agent is properly registered with the MCP server
- Ensure the prompt templates are correctly defined
- Verify that the agent's process_task method is properly implemented

## Contributing

See the [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines on contributing to the project.

## Next Steps

Now that you have set up your development environment, you can:

1. Explore the codebase to understand how the system works
2. Run the example scripts to see the system in action
3. Create a new agent to extend the system
4. Contribute to the project by fixing bugs or adding features

Happy coding!