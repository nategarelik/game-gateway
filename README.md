# Unity Agent MCP

An Autonomous AI Agent Ecosystem for Unity Game Development, focusing on programming, scripting, scene creation, and world mapping.

## Overview

This project provides a Model Context Protocol (MCP) server and agent framework for Unity game development. It enables AI-driven game development with specialized agents for:

- Level architecture and scene creation
- Code generation and scripting
- Documentation management
- Asset placement and organization

## Quick Start

### Prerequisites

- Python 3.8+
- Unity 2022.3 LTS or newer
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/unity-agent-mcp.git
   cd unity-agent-mcp
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Import the Unity package:
   - In Unity, go to Window > Package Manager
   - Click '+' > Add package from disk
   - Select the `unity-package/com.unity-agent-mcp.tgz` file

### Running the MCP Server

```bash
python -m src.mcp_server.main
```

### Configuring Unity Integration

1. In Unity, open Window > Unity Agent MCP > Settings
2. Enter your MCP server details (default: http://localhost:5001)
3. Click "Test Connection"

## Features

- **Level Architect Agent**: Creates and modifies Unity scenes based on descriptions
- **Code Weaver Agent**: Generates and implements C# scripts for game logic
- **Documentation Sentinel**: Manages documentation for code and assets
- **Pixel Forge Agent**: Places and organizes assets in scenes

## Project Structure

- `src/`: Core source code
- `docs/`: Documentation
- `tests/`: Test files
- `unity-package/`: Unity integration package
- `scripts/`: Utility scripts

## Publishing to GitHub

To make this project available from any device:

1. Create a new GitHub repository:
   - Go to https://github.com/new
   - Name it "unity-agent-mcp" (or your preferred name)
   - Set it to Public or Private as desired
   - Do not initialize with README, .gitignore, or license

2. Push the local repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/unity-agent-mcp.git
   git push -u origin main
   ```

3. Set up GitHub Actions for CI/CD:
   - The `.github/workflows/build.yml` file is already configured
   - It will automatically run tests and build the Unity package

## License

MIT