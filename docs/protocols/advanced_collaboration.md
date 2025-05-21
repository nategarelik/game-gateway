# Advanced Agent Behaviors and Collaboration Protocols Documentation

This document outlines conceptual protocols for enabling advanced agent behaviors, focusing on multi-agent collaboration and real-time communication within the Autonomous AI Agent Ecosystem.

The core Python module for these conceptual protocols is located at [`src/protocols/advanced_collaboration_protocols.py`](../../src/protocols/advanced_collaboration_protocols.py).

## Purpose

The primary objectives of these protocols are:
1.  **Multi-Agent Collaboration:** To facilitate scenarios where one agent can request assistance from another agent to perform a sub-task or leverage a specific capability it lacks. This is managed conceptually through a `CollaborationManager` that would interface with the Master Control Program (MCP).
2.  **Real-Time Communication/Feedback:** To provide a mechanism (conceptually an `AgentEventBus`, likely part of the MCP) for agents to publish status updates, results, or other events, and for other interested agents or systems to subscribe and react to these events.

## Core Components and Concepts

### 1. `AgentProfile`
   *   A data class representing an agent's known profile.
   *   Attributes: `agent_id`, `capabilities` (list of strings), `current_task_id`, and `status` (e.g., "idle", "processing_task").

### 2. `TaskAssistanceRequest`
   *   A data class representing a formal request for help from one agent to another.
   *   Attributes: `request_id`, `requesting_agent_id`, `original_task_id`, `required_capability`, `task_details` (for the sub-task), `status` (e.g., "pending", "dispatched_to_mcp"), and `assigned_assisting_agent_id`.

### 3. `AgentEvent`
   *   A data class for events published by agents.
   *   Attributes: `event_id`, `source_agent_id`, `event_type` (e.g., "asset_generated", "task_progress_update"), `data` (payload of the event), and `timestamp`.

:start_line:27
-------
### 4. `CollaborationManager`
   *   **Purpose:** Manages multi-agent collaboration, focusing on task assistance. It is instantiated and managed by the `MCPServer`.
   *   **Initialization:** Takes an `mcp_interface` object (which is the `MCPServer` itself, providing methods for tasking and agent discovery). Internally maintains a dictionary of `registered_agents`.
   *   **Method: `register_agent(agent_id: str, capabilities: List[str])`**: Allows agents to make their presence and capabilities known. The `MCPServer` automatically registers its agents with the `CollaborationManager` during initialization.
   *   **Method: `update_agent_status(agent_id: str, status: str, current_task_id: Optional[str] = None)`**: Updates the recorded status of an agent.
   *   **Method: `async request_assistance(requesting_agent_id: str, original_task_id: str, required_capability: str, task_details: Dict[str, Any]) -> Optional[str]`**:
        *   An agent calls this to request help.
        *   The manager attempts to find a suitable, `idle` agent with the `required_capability`.
        *   If found, it creates a `TaskAssistanceRequest` and dispatches a new sub-task to the chosen assisting agent via the `mcp_interface` (i.e., the `MCPServer`'s `handle_api_request` method).
        *   Returns the `request_id` of the assistance request if successful, otherwise `None`.
   *   **Method: `update_assistance_request_status(request_id: str, status: str, result_data: Optional[Dict] = None)`**:
        *   Called (typically by the assisting agent or the MCP) when an assistance sub-task is completed or fails.
        *   Updates the status of the `TaskAssistanceRequest` and potentially notifies the original requesting agent.

:start_line:42
-------
### 5. `AgentEventBus`
   *   **Purpose:** A publish/subscribe system for real-time inter-agent communication. This functionality is integrated directly into the `MCPServer`.
   *   **Method: `async subscribe(event_type: str, callback: Callable)`**: Allows an agent or system to register an asynchronous `callback` function to be invoked when an event of `event_type` is published.
   *   **Method: `async unsubscribe(event_type: str, callback: Callable)`**: Removes a subscription.
   *   **Method: `async publish_event(source_agent_id: str, event_type: str, data: Dict[str, Any])`**:
        *   An agent calls this to broadcast an `AgentEvent`.
        *   The bus identifies all subscribers for that `event_type` and invokes their registered callbacks with the event data.

## Interaction Flows

### Multi-Agent Collaboration (Task Assistance):
1.  `AgentA` is working on `TaskX` and realizes it needs a capability it doesn't possess (e.g., "generate_texture").
2.  `AgentA` calls `collaboration_manager.request_assistance()`, specifying its ID, `TaskX`'s ID, the "generate_texture" capability, and details for the texture (e.g., prompt).
3.  The `CollaborationManager` queries its `registered_agents` for an `idle` agent with the "generate_texture" capability (e.g., `AgentB`).
4.  If `AgentB` is found, the `CollaborationManager` (via its `mcp_interface`) creates a new sub-task (e.g., `SubTaskY` for generating the texture) and assigns it to `AgentB`. The `TaskAssistanceRequest` is updated.
5.  `AgentB` processes `SubTaskY`.
6.  Upon completion (or failure) of `SubTaskY`, `AgentB` (or the MCP) notifies the `CollaborationManager` by calling `update_assistance_request_status()`.
7.  The `CollaborationManager` updates the status of the original `TaskAssistanceRequest` and can then notify `AgentA` that its requested assistance is complete (e.g., by posting an event or a direct message via MCP).

### Real-Time Communication (Event Bus):
1.  `AgentC` (e.g., a listener agent) subscribes to an event type, say "asset_generated", by providing a callback function to `agent_event_bus.subscribe("asset_generated", agent_c_callback)`.
2.  `AgentD` (e.g., `PixelForgeAgent`) successfully generates a new image asset.
3.  `AgentD` calls `agent_event_bus.publish_event("AgentD", "asset_generated", {"asset_id": "img_001", ...})`.
4.  The `AgentEventBus` finds `AgentC`'s subscription and asynchronously calls `agent_c_callback` with the event details.
5.  `AgentC`'s callback function processes the event (e.g., logs it, updates its internal state).

:start_line:67
-------
## Integration with MCP Server

Both the `CollaborationManager` and `AgentEventBus` are instantiated and managed by the `MCPServer`. This means agents do not directly instantiate these components but interact with them through the MCP.

### Agent Interaction with CollaborationManager (via MCP)

Agents can request assistance or update their status by calling specific methods on the `MCPServer` (which then delegates to its internal `CollaborationManager` instance). These methods are typically invoked via the `MCPServer`'s `POST /execute_agent` endpoint, targeting the `MCPServer` itself with a specific `command_type`.

*   **Registering Agent Capabilities:** During its initialization, the `MCPServer` automatically registers all instantiated agents with its `CollaborationManager` using their `agent_id` and `capabilities`.
*   **Updating Agent Status:** Agents can conceptually update their status (e.g., "idle", "processing_task", "awaiting_assistance") by sending a task to the MCP.
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"mcp_server"` (or the agent's own ID, if the MCP routes it internally)
    *   **`parameters`**:
        *   `command_type`: `"update_agent_status"`
        *   `status` (string): The new status.
        *   `current_task_id` (string, optional): The ID of the task the agent is currently processing.
*   **Requesting Assistance:** An agent requests assistance by sending a task to the MCP. The MCP then uses its `CollaborationManager` to find a suitable assisting agent and dispatches a sub-task.
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"mcp_server"`
    *   **`parameters`**:
        *   `command_type`: `"request_agent_assistance"`
        *   `requesting_agent_id` (string): The ID of the agent requesting assistance.
        *   `original_task_id` (string): The ID of the original task requiring assistance.
        *   `required_capability` (string): The capability needed from an assisting agent.
        *   `task_details` (dict): The specific sub-task details for the assisting agent.
*   **Updating Assistance Request Status:** The assisting agent (or the MCP) updates the status of an assistance request.
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"mcp_server"`
    *   **`parameters`**:
        *   `command_type`: `"update_assistance_request_status"`
        *   `request_id` (string): The ID of the assistance request.
        *   `status` (string): The new status (e.g., "completed", "failed", "rejected").
        *   `result_data` (dict, optional): Result data from the completed sub-task.

### Agent Interaction with AgentEventBus (via MCP)

Agents publish and subscribe to events through the `MCPServer`'s event handling mechanisms.

*   **Publishing Events:** Agents publish events by sending a task to the MCP.
    *   **Endpoint:** `POST /post_event` (as documented in `mcp_server/api.md`)
    *   **`event_type`**: The type of event (e.g., "asset_generated", "task_progress").
    *   **`data`**: The event-specific payload.
    *   **`source_agent_id`**: The ID of the agent publishing the event.
*   **Subscribing to Events:** Agents (or internal MCP components) subscribe to events by registering a callback with the MCP. This is typically done internally by MCP components or during agent initialization if an agent needs to react to specific events.
    *   **Endpoint:** `POST /execute_agent`
    *   **`agent_id`**: `"mcp_server"`
    *   **`parameters`**:
        *   `command_type`: `"subscribe_to_agent_event"`
        *   `event_type` (string): The type of event to subscribe to.
        *   `callback` (string/reference): A way to identify the callback function (e.g., a registered endpoint or internal method name).
    *   **Note:** Direct subscription by external agents to internal Python callbacks is not feasible via a REST API. This implies that agents would either poll for events, or the MCP would push events to registered agent endpoints. The current `subscribe` method is primarily for internal MCP components.

## Example Usage (from `if __name__ == '__main__':`)

The `advanced_collaboration_protocols.py` script includes a demonstration of the conceptual components. When integrated with the `MCPServer`, the interaction would shift to using the `POST /execute_agent` endpoint for most `CollaborationManager` and `AgentEventBus` functionalities.

```python
# In src/protocols/advanced_collaboration_protocols.py
# ... (Conceptual classes remain for internal logic) ...

# Example of how an agent might conceptually interact with the MCP for collaboration
# (This is illustrative, actual agent implementation would use MCPClient)

async def agent_behavior_example(mcp_client_instance):
    # Update own status
    await mcp_client_instance.execute_agent(
        agent_id="mcp_server",
        command_type="update_agent_status",
        parameters={"agent_id": "LevelArchitect_01", "status": "processing_task", "current_task_id": "main_level_design_task"}
    )

    # Request assistance
    assistance_req_id = await mcp_client_instance.execute_agent(
        agent_id="mcp_server",
        command_type="request_agent_assistance",
        parameters={
            "requesting_agent_id": "LevelArchitect_01",
            "original_task_id": "main_level_design_task",
            "required_capability": "generate_texture",
            "task_details": {"prompt": "a mossy stone wall texture", "resolution": "1024x1024"}
        }
    )
    if assistance_req_id and assistance_req_id.get("status") == "success":
        logger.info(f"Assistance requested: {assistance_req_id.get('result')}")
    
    # Publish an event
    await mcp_client_instance.post_event(
        event_type="task_progress",
        data={"task_id": "main_level_design_task", "progress_percent": 75, "status_message": "Finalizing prop placement."},
        source_agent_id="LevelArchitect_01"
    )

# The `if __name__ == '__main__':` block in the protocol file still uses mock components
# for standalone testing of the protocol logic itself, not the full MCP interaction.
```
This updated example illustrates how agents would conceptually interact with the MCP for collaboration and eventing, using the `POST /execute_agent` and `POST /post_event` endpoints.

## Future Enhancements

### CollaborationManager:
*   **Sophisticated Agent Matching:** Implement more advanced algorithms for finding suitable assisting agents (e.g., considering workload, proximity in a conceptual 'skill space', bidding).
*   **Task Decomposition:** Allow the manager to help break down complex assistance requests into smaller, manageable sub-tasks.
*   **Resource Management:** Integrate with resource tracking if agents have limited concurrent task capacity.
*   **Failure Handling & Retries:** More robust handling if an assisting agent fails its sub-task (e.g., re-assigning, notifying original requester with failure details).

### AgentEventBus:
*   **Persistent Event Storage:** For auditing or allowing late subscribers to catch up on recent events.
*   **Filtering & Pattern Matching:** Allow subscribers to specify more complex filters for the events they are interested in beyond just `event_type`.
*   **Guaranteed Delivery/QoS:** Implement different Quality of Service levels for event delivery if required.
*   **Security & Access Control:** Define which agents can publish or subscribe to which event types.
*   **Direct Integration with MCP:** This functionality should ideally be a core part of the MCP server itself rather than a standalone Python class in a production system.