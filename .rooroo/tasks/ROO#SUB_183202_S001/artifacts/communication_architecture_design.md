# Communication Architecture Design: Unity (C#) and Python AI Agent Ecosystem

**Task ID:** ROO#SUB_183202_S001
**Goal:** Design the communication architecture and protocol for interaction between a Unity (C#) project and the existing Python-based AI agent ecosystem via the MCP server.

## 1. Protocol Selection

**Chosen Protocol:** REST API over HTTP

**Justification:**
*   **Simplicity:** HTTP is a widely understood and easily implemented protocol in both C# (Unity) and Python.
*   **Request-Response Model:** The interaction pattern of Unity requesting an action from an agent and receiving a result fits well with the synchronous request-response nature of REST.
*   **Statelessness:** Each request from Unity is independent, simplifying server-side logic and scalability.
*   **Tooling and Libraries:** Extensive libraries and built-in support exist in both Unity (C#) and Python for making and handling HTTP requests.

While WebSockets could be considered for real-time streaming or long-running tasks, the primary use case of invoking agents and receiving outputs is adequately served by a simpler REST approach for the initial design. gRPC offers performance benefits but introduces more complexity in setup and code generation compared to REST/JSON.

## 2. Data Exchange Format

**Chosen Format:** JSON (JavaScript Object Notation)

**Justification:**
*   **Interoperability:** JSON is a language-agnostic format, making it ideal for exchanging data between C# and Python.
*   **Readability:** JSON is human-readable, which aids in debugging and development.
*   **Ease of Parsing:** Both C# and Python have robust built-in or widely available libraries for serializing and deserializing JSON data.
*   **Flexibility:** JSON's hierarchical structure can easily represent complex data structures required for agent parameters and results.

## 3. Message Structure

All messages will be JSON objects.

### 3.1. Unity Request to MCP

This structure is used by the Unity client to request an action from a specific agent or toolchain via the MCP server.

```json
{
  "task_id": "string", // Unique identifier for this request instance
  "agent_id": "string", // Identifier of the target agent or toolchain (e.g., "level_architect", "pixel_forge", "muse")
  "parameters": {      // JSON object containing parameters specific to the agent/task
    // ... agent-specific parameters ...
  }
}
```

**Example Request (Invoking Level Architect):**

```json
{
  "task_id": "unity_req_12345",
  "agent_id": "level_architect",
  "parameters": {
    "level_type": "dungeon",
    "complexity": "medium",
    "seed": 42
  }
}
```

### 3.2. MCP Response to Unity

This structure is used by the MCP server to return the result or status of a request back to the Unity client.

```json
{
  "task_id": "string", // Identifier from the corresponding request
  "status": "string",  // Status of the request ("success", "failed", "processing")
  "result": {          // JSON object containing output data (present if status is "success")
    // ... agent-specific results ...
  },
  "error": {           // JSON object containing error details (present if status is "failed")
    "code": "string",    // Specific error code
    "message": "string", // Human-readable error description
    "details": {}        // Optional additional details
  }
}
```

**Example Success Response (from Level Architect):**

```json
{
  "task_id": "unity_req_12345",
  "status": "success",
  "result": {
    "level_data": {
      "layout": [[0, 1], [1, 0]],
      "entities": [{"type": "player", "pos": [0,0]}]
    },
    "generation_time_ms": 550
  },
  "error": null
}
```

**Example Failure Response (Agent Not Found):**

```json
{
  "task_id": "unity_req_67890",
  "status": "failed",
  "result": null,
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID 'non_existent_agent' not found.",
    "details": {}
  }
}
```

## 4. MCP Interaction Flow

1.  **Unity Initiates Request:** The Unity application constructs a JSON request object based on the desired agent/toolchain and parameters.
2.  **Unity Sends HTTP Request:** Unity sends an HTTP POST request containing the JSON payload to a predefined endpoint on the Python MCP server (e.g., `http://mcp_server_address:port/execute_agent`).
3.  **MCP Receives and Parses:** The Python MCP server receives the HTTP request, extracts the JSON payload, and parses it into a Python dictionary or object.
4.  **MCP Routes Request:** The MCP server examines the `agent_id` in the request. It uses an internal mapping or routing mechanism to identify the appropriate agent handler or toolchain integration responsible for that ID.
5.  **MCP Forwards to Agent/Toolchain:** The MCP server passes the `parameters` to the designated agent handler or toolchain integration function/method.
6.  **Agent/Toolchain Executes:** The agent or toolchain performs the requested task.
7.  **Agent/Toolchain Returns Result/Error:** Upon completion, the agent or toolchain returns either the result data or an error object back to the MCP server.
8.  **MCP Constructs Response:** The MCP server constructs a JSON response object, including the original `task_id`, the `status` ("success" or "failed"), and either the `result` or `error` data.
9.  **MCP Sends HTTP Response:** The MCP server sends the JSON response back to the Unity client as the body of the HTTP response.
10. **Unity Receives and Processes:** The Unity application receives the HTTP response, parses the JSON payload, and processes the `status`, `result`, or `error` accordingly.

## 5. Error Handling

Errors are handled by returning a "failed" status in the MCP Response structure, along with a detailed `error` object. This allows Unity to programmatically identify the type of error and display appropriate feedback to the user or handle it internally.

**Common Error Codes:**
*   `AGENT_NOT_FOUND`: The requested `agent_id` does not correspond to a known agent or toolchain.
*   `INVALID_PARAMETERS`: The provided `parameters` are missing, malformed, or invalid for the target agent/task.
*   `EXECUTION_ERROR`: An error occurred during the execution of the agent or toolchain task.
*   `INTERNAL_SERVER_ERROR`: An unexpected error occurred within the MCP server itself.

Unity should be designed to check the `status` field in the response. If it is "failed", it should examine the `error` object to understand the cause and react appropriately.