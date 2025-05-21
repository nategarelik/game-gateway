# Sub-Task Context: ROO#SUB_183202_S001
## Parent Task ID: ROO#NAV_PLAN_20250518-183202
## Goal for rooroo-analyzer:
Design the communication architecture and protocol for interaction between a Unity (C#) project and the existing Python-based AI agent ecosystem.

**Specifics to Address:**
1.  **Protocol Selection:** Choose and justify a suitable communication protocol (e.g., REST API over HTTP, WebSockets, gRPC) for Unity-Python inter-process communication.
2.  **Data Exchange Format:** Specify the data format for messages (e.g., JSON).
3.  **Message Structure:** Define basic message structures for requests from Unity (e.g., to invoke an agent, query status) and responses from the Python MCP server.
4.  **MCP Interaction Flow:** Outline how Unity will send requests to the Python MCP server ([`mcp_server_core.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S001/mcp_server_core.py)) and how the MCP will route these to appropriate agents (e.g., [`level_architect_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S002/level_architect_agent.py), [`pixel_forge_agent.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S003/pixel_forge_agent.py)) or toolchain integrations (e.g., [`muse_integration.py`](.rooroo/tasks/ROO#SUB_PLAN_20250518-170411_S005/muse_integration.py)).
5.  **Error Handling:** Briefly consider how errors might be communicated back to Unity.

**Key Input Reference:**
*   Overall project context and existing artifacts: [`.rooroo/tasks/ROO#NAV_PLAN_20250518-183202/context.md`](.rooroo/tasks/ROO#NAV_PLAN_20250518-183202/context.md)

**Expected Output Artifact:**
*   A design document (e.g., `communication_architecture_design.md`) in this task's artifact directory, detailing the chosen protocol, data formats, message structures, and interaction flow.