# MCP Server API Documentation

This document provides a basic overview of the Master Control Program (MCP) Server API endpoints.

## General Information

-   **Base URL:** `/api/v1`
-   **Authentication:** (Currently none, to be defined)
-   **Response Format:** JSON

:start_line:11
-------
## Core Endpoints

The MCP Server exposes a set of RESTful API endpoints for interaction with agents, toolchains, and internal systems.

### 1. Server Status

-   **Endpoint:** `GET /status`
-   **Description:** Returns the current operational status of the MCP server.
-   **Response Body:**
    ```json
    {
        "status": "running",
        "message": "MCP Server is operational."
    }
    ```

### 2. Agent and Toolchain Listing

-   **Endpoint:** `GET /agents`
    -   **Description:** Returns a list of all currently registered agents and their advertised capabilities.
    -   **Response Body:**
        ```json
        {
            "agents": {
                "level_architect": ["level_design", "procedural_generation_guidance", "scene_creation", "world_mapping"],
                "code_weaver": ["script_generation", "game_logic_implementation", "ui_scripting"],
                "pixel_forge": ["asset_generation_2d", "asset_generation_3d_placeholder", "asset_placement"],
                "documentation_sentinel": ["documentation_monitoring", "knowledge_update_trigger", "script_documentation_generation"]
            }
        }
        ```
-   **Endpoint:** `GET /toolchains`
    -   **Description:** Returns a list of all available toolchain bridges and their availability status.
    -   **Response Body:**
        ```json
        {
            "toolchains": {
                "muse": {"available": true},
                "retro_diffusion": {"available": true},
                "unity": {"available": true}
            }
        }
        ```

### 3. Agent Task Execution and System Interaction

-   **Endpoint:** `POST /execute_agent`
    -   **Description:** This is the primary endpoint for assigning tasks to specific agents or triggering actions within the MCP's internal systems (Knowledge Management, Autonomous Iteration, Emergent Behaviors, Extensibility). The `agent_id` in the request payload determines the target.
    -   **Request Body:**
        ```json
        {
            "task_id": "unique_task_identifier_from_client",
            "agent_id": "target_agent_or_system_id", // e.g., "level_architect", "code_weaver", "unity", "kms", "aiw", "conflict_resolver", "tool_composer", "tool_registry"
            "parameters": {
                // Task-specific parameters. Refer to agent/system documentation for details.
            }
        }
        ```
    -   **Response Body:**
        ```json
        {
            "task_id": "unique_task_identifier_from_client",
            "status": "success" | "failed",
            "result": { /* Task-specific result data */ },
            "error": { /* Error details if status is 'failed' */ }
        }
        ```
    -   **Supported `agent_id` values and their conceptual `parameters`:**
        *   **Agents (e.g., `level_architect`, `code_weaver`, `pixel_forge`, `documentation_sentinel`)**:
            *   `parameters` should contain the `task_details` expected by the agent's `process_task` method.
            *   Example for `code_weaver`: `{"command_type": "generate_script", "script_name": "MyScript", "script_content": "..."}`
        *   **Toolchains (e.g., `unity`, `muse`, `retro_diffusion`)**:
            *   `parameters` should contain `command_type` (for Unity/Muse) or `prompt` (for Retro Diffusion) and other tool-specific arguments.
            *   Example for `unity`: `{"command_type": "manipulate_scene", "arguments": {"operation": "create_object", "target_object": "Cube"}}`
        *   **Knowledge Management System (`kms`)**:
            *   `command_type`: `"trigger_update_cycle"`
            *   `parameters`: `{}` (no additional parameters for now)
        *   **Autonomous Iteration Workflow (`aiw`)**:
            *   `command_type`: `"run_iteration_cycle"`
            *   `parameters`: `{"level_ids_to_test": ["level_01"], "num_sessions_per_level": 5}`
        *   **Creative Conflict Resolver (`conflict_resolver`)**:
            *   `command_type`: `"resolve_design_conflict"`
            *   `parameters`: `{"proposals": [...], "target_element_id": "..."}` (list of `DesignProposal` dicts)
        *   **Dynamic Tool Composer (`tool_composer`)**:
            *   `command_type`: `"compose_and_execute_tools"`
            *   `parameters`: `{"task_goal": "...", "initial_state": {...}}`
        *   **Tool Registry (`tool_registry`)**:
            *   `command_type`: `"register_external_tool"`, `"unregister_external_tool"`, `"list_external_tools"`, `"execute_external_tool"`
            *   `parameters`: Varies based on `command_type`. For `register_external_tool`, it would be the tool's metadata. For `execute_external_tool`, it would be `{"tool_id": "...", "parameters": {...}}`.

### 4. Event Posting

-   **Endpoint:** `POST /post_event`
    -   **Description:** Allows agents or other systems to post arbitrary events to the MCP server. These events are then routed to relevant subscribers via the `AgentEventBus`.
    -   **Request Body:**
        ```json
        {
            "event_type": "type_of_event", // e.g., "level_design_progress", "asset_generated", "creative_conflict_review_needed"
            "data": { /* Event-specific payload */ },
            "source_agent_id": "agent_that_posted_event" // Optional, but recommended
        }
        ```
    -   **Response:** `PostEventResponse` (confirmation message and `event_id`).
    -   **Note:** Events are a primary mechanism for asynchronous feedback and inter-agent communication.

---
*Note: This documentation reflects the current API structure and is subject to expansion as the system evolves.*

---
*Note: This is initial documentation and subject to expansion.*