# Emergent Behavior Protocols Documentation

Emergent Behavior Protocols are designed to manage and guide complex interactions between AI agents, particularly when dealing with creative conflicts or requiring sequences of tool usage to achieve a goal. These protocols aim to foster more sophisticated and adaptive agent behaviors.

The core Python module for these conceptual protocols is located at [`src/protocols/emergent_behavior_protocols.py`](../../src/protocols/emergent_behavior_protocols.py).

## Purpose

The primary objectives of these protocols are:
1.  **Creative Conflict Resolution:** To provide mechanisms for resolving situations where multiple agents propose differing solutions or designs for the same game element or task.
2.  **Dynamic Tool Composition:** To enable agents (or a dedicated composing system) to dynamically select and sequence a series of tools or capabilities to achieve a more complex goal than a single tool could accomplish. This is a placeholder for a more advanced planning system.

## Core Components and Concepts

### 1. `DesignProposal`
   *   A data class representing a design idea or solution proposed by an agent.
   *   Attributes: `proposal_id`, `agent_id`, `target_element_id` (what is being designed), `proposed_design` (dictionary of design specifics), `confidence` (agent's confidence in the proposal), and `priority`.

### 2. `Tool`
   *   A conceptual data class representing an available tool or capability.
   *   Attributes: `tool_id`, `name`, `capabilities` (list of strings describing what the tool does), `parameters` (describing tool inputs).
   *   Method: `async execute(execution_params: Dict[str, Any], agent_context: Optional[Dict] = None) -> Dict[str, Any]`: A placeholder for tool execution, returning a mock result.

:start_line:45
-------
### 3. `CreativeConflictResolver`
   *   **Purpose:** To mediate and resolve conflicts arising from multiple `DesignProposal`s for the same `target_element_id`.
   *   **Initialization:** Takes an `mcp_event_notifier` (a callable function, typically provided by the MCP Server, to send notifications if a conflict cannot be automatically resolved or requires human review).
   *   **Method: `async resolve_conflicting_proposals(proposals: List[DesignProposal], target_element_id: str) -> Optional[DesignProposal]`**:
        *   If only one proposal exists, it's returned.
        *   **Current Logic:** Sorts proposals first by `priority` (descending) and then by `confidence` (descending). The top proposal is selected as the winner.
        *   If there's a "close call" (e.g., top two proposals have same priority and very similar confidence), it logs a warning and uses the `mcp_event_notifier` to flag the conflict for review.
        *   Returns the winning `DesignProposal` or `None` if no proposals were provided.

### 4. `DynamicToolComposer`
   *   **Purpose:** A conceptual component to dynamically select and sequence a series of `Tool` executions to achieve a given `task_goal`. This is a highly simplified placeholder for what would typically be a complex AI planning system.
   *   **Initialization:** Takes a list of `available_tools`.
   *   **Method: `async compose_and_execute_tool_sequence(task_goal: str, initial_state: Dict[str, Any]) -> List[Dict[str, Any]]`**:
        *   **Current Placeholder Logic:** Contains hardcoded example logic. For a `task_goal` like "generate_detailed_forest_texture", it attempts to:
            1.  Find and use a "concept_generation" tool to get keywords.
            2.  Find and use a "generate_texture" tool with these keywords.
            3.  Find and use an "enhance_detail" tool on the generated texture.
        *   It simulates the execution of these tools and accumulates their mock results.
        *   If required tools are not found, it logs warnings or errors.
        *   Returns a list of mock results from the executed tool sequence.

## Interaction Flow

### Creative Conflict Resolution:
1.  Multiple agents submit `DesignProposal` objects for the same game element (e.g., a puzzle design, a character appearance) to a central system or to each other.
2.  These proposals are collected and passed to the `CreativeConflictResolver`.
3.  The resolver applies its logic (e.g., priority/confidence sorting) to select a winning proposal.
4.  If the conflict is too close or meets certain criteria for ambiguity, the resolver can notify the MCP or a human supervisor for a final decision.
5.  The winning design is then used for implementation.

### Dynamic Tool Composition:
1.  An agent (or the MCP) identifies a high-level `task_goal` that requires multiple steps or capabilities.
2.  The `task_goal` and relevant `initial_state` information are passed to the `DynamicToolComposer`.
3.  The composer (conceptually) plans a sequence of available tools.
4.  It then (conceptually) executes these tools in order, potentially passing the output of one tool as input to the next.
5.  The final result or a summary of the sequence execution is returned.

## Example Usage (from `if __name__ == '__main__':`)

The `emergent_behavior_protocols.py` script includes a demonstration:

```python
# In src/protocols/emergent_behavior_protocols.py

async def mock_mcp_notify(event_type: str, data: dict):
    logger.info(f"[MockMCPNotifier] Event: {event_type}, Data: {data}")

# Creative Conflict Resolution Example
resolver = CreativeConflictResolver(mcp_event_notifier=mock_mcp_notify)
proposals = [
    DesignProposal("propA1", "AgentAlpha", "puzzle_01", {...}, priority=1, confidence=0.9),
    DesignProposal("propB1", "AgentBeta", "puzzle_01", {...}, priority=2, confidence=0.85),
    # ...
]
# winning = await resolver.resolve_conflicting_proposals(proposals, "puzzle_01")

# Dynamic Tool Composition Example
mock_tools = [
    Tool("tool_concept", "Concept Generator", ["concept_generation"], {...}),
    # ... other tools ...
]
composer = DynamicToolComposer(available_tools=mock_tools)
# tool_results = await composer.compose_and_execute_tool_sequence("generate_detailed_forest_texture", {})
```
This example illustrates how to instantiate and use the `CreativeConflictResolver` with sample proposals and the `DynamicToolComposer` with mock tools to achieve a conceptual multi-step goal.

:start_line:90
-------
## Integration with MCP Server

Both the `CreativeConflictResolver` and `DynamicToolComposer` are instantiated and managed by the `MCPServer`. This allows the MCP to act as the central orchestrator for these emergent behaviors.

### Triggering Conflict Resolution

Agents or other systems can request conflict resolution via the `MCPServer`'s `POST /execute_agent` endpoint by specifying `agent_id: "conflict_resolver"`.

*   **Endpoint:** `POST /execute_agent`
*   **`agent_id`**: `"conflict_resolver"`
*   **`parameters`**:
    *   `command_type`: `"resolve_design_conflict"`
    *   `proposals` (list of dicts): A list of design proposals, each conforming to the `DesignProposal` structure.
    *   `target_element_id` (string): The ID of the element for which conflicts are being resolved.

### Triggering Dynamic Tool Composition

Agents or other systems can request dynamic tool composition via the `MCPServer`'s `POST /execute_agent` endpoint by specifying `agent_id: "tool_composer"`.

*   **Endpoint:** `POST /execute_agent`
*   **`agent_id`**: `"tool_composer"`
*   **`parameters`**:
    *   `command_type`: `"compose_and_execute_tools"`
    *   `task_goal` (string): A description of the overall goal for tool composition (e.g., "generate_detailed_forest_texture").
    *   `initial_state` (dict): The current state relevant to the task, which the composer can use for planning.

### Tool Execution within DynamicToolComposer

When the `DynamicToolComposer` executes a `Tool` (as defined in `emergent_behavior_protocols.py`), it does so by calling back to the `MCPServer`'s internal `handle_api_request` method. This means that the conceptual `Tool.execute` method in `emergent_behavior_protocols.py` is effectively a proxy for calling actual agents or toolchains registered with the MCP.

## Future Enhancements

### Creative Conflict Resolver:
*   **Advanced Resolution Strategies:** Implement more sophisticated methods like weighted voting, merging compatible parts of proposals, or negotiation protocols between agents.
*   **Learning/Adaptation:** Allow the resolver to learn from past conflict resolutions or human feedback.
*   **Configurable Policies:** Define different resolution policies for different types of conflicts or elements.

### Dynamic Tool Composer:
*   **AI Planning Integration:** Replace placeholder logic with a robust AI planning system (e.g., PDDL-based, HTN, or LLM-based planning) that can dynamically generate tool sequences based on tool capabilities, preconditions, and effects.
*   **State Management:** Implement proper state representation and tracking as tools are executed.
*   **Error Handling & Replanning:** Allow the composer to handle tool execution failures and potentially re-plan the sequence.
*   **Tool Discovery:** Integrate with a service that allows dynamic discovery of available tools and their capabilities.
*   **Cost/Benefit Analysis:** Incorporate a notion of cost or utility for different tools and sequences.