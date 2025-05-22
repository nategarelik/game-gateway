# Unity Agent MCP Documentation

Welcome to the Unity Agent MCP documentation. This documentation provides comprehensive information about the Autonomous AI Agent Ecosystem for Unity Game Development.

## Getting Started

- [development_setup](development_setup.md) - Setting up a development environment
- [unity_integration_guide](unity_integration_guide.md) - Integrating with Unity projects
- [github_setup](github_setup.md) - Setting up and publishing the project on GitHub

## Architecture

- [architecture_overview](architecture_overview.md) - High-level overview of the system architecture
- [unity_package_structure](unity_package_structure.md) - Structure and content of the Unity package

## MCP Server

- [mcp_server](mcp_server.md) - Overview of the MCP server
- [api](mcp_server/api.md) - API documentation
- [prompt_registry](mcp_server/prompt_registry.md) - Prompt template management
- [state_management](mcp_server/state_management.md) - State management using LangGraph

## Agents

- [level_architect](agents/level_architect.md) - Level Architect agent documentation
- [code_weaver](agents/code_weaver.md) - Code Weaver agent documentation
- [documentation_sentinel](agents/documentation_sentinel.md) - Documentation Sentinel agent documentation
- [pixel_forge](agents/pixel_forge_agent.md) - Pixel Forge agent documentation
- [creating_new_agents](creating_new_agents.md) - Guide to creating new agents

## Protocols

- [advanced_collaboration](protocols/advanced_collaboration.md) - Multi-agent collaboration protocols
- [emergent_behaviors](protocols/emergent_behaviors.md) - Emergent behavior protocols

## Systems

- [extensibility](systems/extensibility.md) - Extensibility and integration system
- [knowledge_management](systems/knowledge_management.md) - Knowledge management system
- [style_enforcement](systems/style_enforcement.md) - Style enforcement system

## Toolchains

- [muse](toolchains/muse.md) - Unity Muse integration
- [retro_diffusion](toolchains/retro_diffusion.md) - Retro Diffusion integration

## Workflows

- [autonomous_iteration](workflows/autonomous_iteration.md) - Autonomous iteration workflow

## Tests

- [e2e_scenario_01](tests/e2e_scenario_01.md) - End-to-end test scenario

## Contributing

- [CONTRIBUTING](/CONTRIBUTING.md) - Guidelines for contributing to the project

## Directory Structure

```
docs/
├── README.md                        # This file
├── architecture_overview.md         # High-level architecture overview
├── creating_new_agents.md           # Guide to creating new agents
├── development_setup.md             # Development environment setup
├── github_setup.md                  # GitHub repository setup
├── unity_integration_guide.md       # Unity integration guide
├── unity_package_structure.md       # Unity package structure
├── agents/
│   ├── code_weaver.md               # Code Weaver agent documentation
│   ├── documentation_sentinel.md    # Documentation Sentinel agent documentation
│   ├── level_architect.md           # Level Architect agent documentation
│   └── pixel_forge_agent.md         # Pixel Forge agent documentation
├── mcp_server/
│   ├── api.md                       # API documentation
│   ├── prompt_registry.md           # Prompt registry documentation
│   └── state_management.md          # State management documentation
├── protocols/
│   ├── advanced_collaboration.md    # Advanced collaboration protocols
│   └── emergent_behaviors.md        # Emergent behavior protocols
├── systems/
│   ├── extensibility.md             # Extensibility system documentation
│   ├── knowledge_management.md      # Knowledge management system documentation
│   └── style_enforcement.md         # Style enforcement system documentation
├── tests/
│   └── e2e_scenario_01.md           # End-to-end test scenario
├── toolchains/
│   ├── muse.md                      # Muse toolchain documentation
│   └── retro_diffusion.md           # Retro Diffusion toolchain documentation
└── workflows/
    └── autonomous_iteration.md      # Autonomous iteration workflow documentation
```

## Document Conventions

Throughout the documentation, we use the following conventions:

- Code blocks are used for code examples, command-line instructions, and file contents
- Inline code formatting is used for code elements, file names, and paths
- Blockquotes are used for important notes and warnings
- Headings are used to organize content hierarchically
- Lists are used for sequential steps, options, and collections of items

## Updating Documentation

When updating the documentation, please follow these guidelines:

1. Use clear, concise language
2. Include examples where appropriate
3. Keep documentation up to date with code changes
4. Use proper Markdown formatting
5. Add new documents to this index

## Getting Help

If you need help with the Unity Agent MCP system, you can:

- Check the documentation for relevant information
- Look for examples in the `scripts` directory
- Create an issue on GitHub for bugs or feature requests
- Reach out to the project maintainers

Thank you for using Unity Agent MCP!