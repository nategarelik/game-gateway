# MCP Server Documentation

## Overview

The Multi-Agent Communication Protocol (MCP) Server acts as the central orchestration hub for the Autonomous AI Agent Ecosystem. Its primary roles include:

*   **Agent Management:** Providing a standardized interface for agents to interact with the ecosystem.
*   **Workflow Execution:** Managing multi-step processes involving different agents and toolchains, potentially using a `StateGraph` mechanism.
*   **Toolchain Integration:** Acting as a bridge to external toolchains like Muse and Retro Diffusion.

Agents and external clients communicate with the MCP Server via a defined API, allowing them to request actions, submit results, and participate in workflows.

## Server Core (`src/mcp_server/server_core.py`)

The MCP Server is implemented using the Flask web framework. It provides the core logic for handling incoming requests, routing them to appropriate agents or toolchains, and managing the overall state or workflow.

### Key Functionalities

*   Initializes the Flask application and the core `MCPServer` instance.
*   Loads available agents and toolchain bridges based on imports.
*   Provides an API endpoint for external interaction.
*   Manages a `StateGraph` for defining and executing multi-step workflows (though the current implementation primarily focuses on direct API calls).
*   Includes a `PromptRegistry` for managing agent prompt templates (though not directly used by the current API endpoint).

### API Endpoints

The primary endpoint for interacting with the MCP Server is `/execute_agent`.

#### `POST /execute_agent`

This endpoint is used to request an agent or toolchain to perform a specific action.

*   **Method:** `POST`
*   **Content Type:** `application/json`

*   **Request Payload:**

    ```json
    {
      "task_id": "string", // A unique identifier for the task or request
      "agent_id": "string", // The ID of the target agent or toolchain (e.g., "level_architect", "muse", "retro_diffusion")
      "parameters": {      // A dictionary containing parameters specific to the agent/toolchain and action
        // ... agent/toolchain specific parameters ...
      }
    }
    ```

    **`parameters` Details:**
    *   If `agent_id` refers to an agent (e.g., "level_architect"), the `parameters` dictionary is passed directly to the agent's `handle_direct_request` method. The required keys and value types depend entirely on the specific agent's implementation.
    *   If `agent_id` is `"muse"`, the `parameters` should include:
        *   `"command_type": "string"` (e.g., "send_message", "execute_script")
        *   `"command_text": "string"` (The command or message content)
        *   Optional additional parameters for the Muse toolchain.
    *   If `agent_id` is `"retro_diffusion"`, the `parameters` should include:
        *   `"prompt": "string"` (The text prompt for asset generation)
        *   Optional `"options": { ... }` dictionary for generation parameters.

*   **Response Format:**

    ```json
    {
      "task_id": "string", // The task_id from the request
      "status": "string",  // "success" or "failed"
      "result": "object" | null, // The result data from the agent/toolchain on success, or null on failure
      "error": {           // Error details on failure, or null on success
        "code": "string",  // A code representing the error type (e.g., "INVALID_REQUEST", "AGENT_NOT_FOUND", "EXECUTION_ERROR")
        "message": "string" // A human-readable error message
      } | null
    }
    ```

*   **HTTP Status Codes:**
    *   `200 OK`: Request processed successfully. Check the `status` field in the response body for the outcome of the agent/toolchain execution.
    *   `400 Bad Request`: Invalid request format, missing required fields (`task_id`, `agent_id`), or invalid parameters for the target agent/toolchain.
    *   `404 Not Found`: The requested `agent_id` does not correspond to a registered agent or available toolchain.
    *   `500 Internal Server Error`: An unexpected error occurred during server processing, toolchain connection issues, or agent implementation errors.

### State Management (`StateGraph`)

The `StateGraph` class in [`server_core.py`](src/mcp_server/server_core.py:0) is intended to manage multi-step workflows. It defines nodes (representing actions, typically performed by agents) and edges (transitions between nodes).

*   **Nodes:** Added using `add_node(name, action)`, where `action` is a callable (like an agent's `execute` method).
*   **Edges:** Added using `add_edge(start_node, end_node, condition=None)`, defining transitions.
*   **Execution:** The `run(initial_state, start_node_name)` method executes the workflow starting from a specified node, passing a `GameDevState` object between nodes.

While the `StateGraph` structure exists, the current `/execute_agent` API endpoint primarily facilitates direct calls to individual agent/toolchain handlers (`handle_direct_request`, `send_muse_command`, `generate_retro_asset`) rather than executing a predefined workflow graph. The `StateGraph` is initialized but not actively used by the API route handler.

### Configuration Options

The server's host and port can be configured using environment variables:

*   `MCP_SERVER_HOST`: Specifies the host address (default: `127.0.0.1`).
*   `MCP_SERVER_PORT`: Specifies the port number (default: `5001`).

## Client Library (`src/mcp_server/client.py`)

The [`MCPClient`](src/mcp_server/client.py:4) class provides a basic Python interface for agents or other components to interact with the MCP Server.

### Purpose

To abstract the details of making HTTP requests to the MCP Server's API, providing a simpler method-based interface for communication.

### Instantiation and Usage

An `MCPClient` instance is created by providing the server URL and the ID of the agent using the client.

```python
from src.mcp_server.client import MCPClient

# Assuming the server is running locally on port 5001
server_url = "http://127.0.0.1:5001"
agent_id = "my_custom_agent"

client = MCPClient(server_url, agent_id)
```

### Key Methods

*   `connect()`: Simulates establishing a connection to the server. Returns `True` on success.
*   `disconnect()`: Simulates disconnecting from the server.
*   `post_event(event_type: str, payload: Dict[str, Any]) -> bool`: Simulates sending an event to the server. In a real implementation, this would likely map to an API call (though the current `server_core.py` doesn't have a dedicated `/event` endpoint; this method's usage might evolve or be intended for a different endpoint). The `payload` is a dictionary containing event-specific data. Returns `True` on simulated success, `False` if not connected.

### Example Usage Snippets

```python
from src.mcp_server.client import MCPClient

server_url = "http://127.0.0.1:5001"
agent_id = "example_agent"

client = MCPClient(server_url, agent_id)

if client.connect():
    print("Client connected.")
    
    # Example of posting a simulated event
    event_payload = {
        "status": "processing",
        "details": "Started generating assets"
    }
    client.post_event("asset_generation_status", event_payload)

    client.disconnect()
    print("Client disconnected.")
else:
    print("Failed to connect to MCP Server.")

# Note: The current MCPClient.post_event is simulated.
# A real implementation would use a library like 'requests'
# to make HTTP calls to the server's API, potentially to the /execute_agent
# endpoint with a specific agent_id for event handling, or a dedicated /event endpoint.
```

## Deployment/Running

To run the MCP Server, ensure you have Flask installed (`pip install Flask`).

Navigate to the project's root directory in your terminal and execute the [`server_core.py`](src/mcp_server/server_core.py:0) file directly:

```bash
python src/mcp_server/server_core.py
```

The server will start and listen on the configured host and port (defaulting to `http://127.0.0.1:5001`). For production environments, a more robust WSGI server like Gunicorn or Waitress should be used.