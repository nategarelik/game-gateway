# Documentation Sentinel Agent Documentation

**Agent ID:** Typically `doc_sentinel_agent` (or similar, e.g., `doc_sentinel_001`)

**Inherits From:** [`BaseAgent`](../../src/agents/base_agent.py)

## Overview

The Documentation Sentinel Agent is a proactive component of the Autonomous AI Agent Ecosystem. Its primary role is to monitor specified documentation sources (local file paths, directories, and potentially URLs in future versions) for any changes, such as modifications, creations, or deletions. Upon detecting a change, it processes the update and can notify the Master Control Program (MCP) or other relevant systems (like a Knowledge Management system) about the change. This helps keep the ecosystem's understanding of its own documentation and codebase up-to-date.

:start_line:11
-------
## Capabilities
 
*   `documentation_monitoring`: Can actively monitor specified file paths and directories for changes.
*   `change_detection`: Can identify when files have been modified, created (implicitly by appearing in a watched directory), or deleted (implicitly by disappearing).
*   `script_documentation_generation`: Can generate API-like documentation for C# scripts.

:start_line:17
-------
## Core Functionality

### Script Documentation Generation (`generate_script_documentation`)

This method is responsible for generating API-like documentation for C# scripts. Currently, it provides a mock documentation string based on the script name and content. In a full implementation, this would involve parsing the C# code to extract method signatures, comments, and other relevant information to produce structured documentation.

### Task Processing (`process_task`)

The agent can respond to specific tasks from the MCP. It now supports the following task types:

*   **`CHECK_SOURCE_UPDATES`**: Checks a specified documentation source for updates.
    *   **Parameters**:
        *   `source_uri` (string, required): The URI of the source to check (e.g., "docs/some_document.md").
    *   **Workflow**: Simulates checking for updates and posts a `doc_source_updated` event if an update is "found".
*   **`PROCESS_DOCUMENT_CHUNK`**: Processes a chunk of document content.
    *   **Parameters**:
        *   `document_uri` (string, required): The URI of the parent document.
        *   `chunk_content` (string, required): The content of the document chunk.
        *   `metadata` (dict, optional): Additional metadata about the chunk (e.g., section headers).
    *   **Workflow**: Simulates processing/vectorizing the chunk and posts a `doc_chunk_processed` event. This is intended for integration with a Knowledge Management System.
*   **`GENERATE_SCRIPT_DOCS`**: Generates documentation for a given C# script.
    *   **Parameters**:
        *   `script_name` (string, required): The name of the script (e.g., "PlayerController").
        *   `script_content` (string, required): The full C# code content for which to generate documentation.
    *   **Workflow**: Calls `generate_script_documentation` and posts a `script_documentation_generated` event with the generated documentation.

### Monitoring Loop (Conceptual)

While the agent's core functionality is now task-driven, the concept of a continuous monitoring loop remains. This would involve periodically dispatching `CHECK_SOURCE_UPDATES` tasks for configured sources.

## MCP Interaction

:start_line:75
-------
*   **Registration:** Registers with the MCP upon initialization.
*   **Event Posting:**
    *   `doc_sentinel_progress`: Sent during various stages of task processing (e.g., "started", "completed").
    *   `doc_source_updated`: Sent when a monitored document source is detected as having updates.
    *   `doc_chunk_processed`: Sent when a document chunk has been processed (e.g., vectorized).
    *   `script_documentation_generated`: **NEW**. Sent when API documentation for a script has been generated.
        *   Payload includes `task_id`, `script_name`, and `documentation` content.
    *   `doc_sentinel_error`: Sent if an error occurs during task processing.

## Integration with Other Systems

*   **MCP Server:** For tasking, eventing, and overall orchestration.
*   **Knowledge Management System:** (Conceptual) The sentinel is designed to feed updated document information (e.g., file content, chunks) to a central knowledge system for embedding, indexing, and retrieval by other agents.
*   **File System:** Directly interacts with the local file system to monitor file modification times and read content.

## Configuration

*   `agent_id`: Unique identifier for the agent instance.
*   `mcp_server_url`: URL of the MCP server.
*   `watch_paths`: List of directory or file paths to monitor (e.g., `["docs/", "src/core_logic.py"]`).
*   `interval_seconds` (for `monitoring_loop`): How often to check for file changes.

## Future Enhancements

*   Full integration with a Knowledge Management system (e.g., sending processed chunks for vectorization).
*   Support for monitoring remote sources (e.g., Git repositories, web URLs).
*   More sophisticated file type filtering and content parsing.
*   Handling of file creation and deletion events more explicitly.
*   Throttling or debouncing of updates for very frequently changing files.
*   Ability to configure watch paths and file types dynamically via MCP tasks.

## Example `if __name__ == '__main__':` Usage

The agent includes an `if __name__ == '__main__':` block that demonstrates:
1.  Instantiating the agent with example `watch_paths`.
2.  Running an initial `scan_documentation_sources` task.
3.  Starting the `monitoring_loop` with a short interval for demonstration.

This allows for basic standalone testing of its monitoring capabilities.
```python
# src/agents/documentation_sentinel.py
# ... (class definition) ...

if __name__ == '__main__':
    async def main_loop():
        mcp_url = "http://localhost:8000/mcp" # Example MCP URL
        agent = DocumentationSentinelAgent(
            agent_id="doc_sentinel_001", 
            mcp_server_url=mcp_url,
            watch_paths=["./docs", "./src"] # Watch project's docs and src for demo
        )
        
        try:
            example_task = {"task_id": "ds_task_scan_01", "type": "scan_documentation_sources"}
            await agent.process_task(example_task)
            await agent.monitoring_loop(interval_seconds=10)
        except KeyboardInterrupt:
            print("DocumentationSentinel demo interrupted by user.")
        finally:
            await agent.shutdown()

    asyncio.run(main_loop())