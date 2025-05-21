# Knowledge Management System Documentation

The Knowledge Management System (KMS) is responsible for monitoring documentation sources, processing document content into manageable chunks, performing (placeholder) vectorization of these chunks, and storing them in a conceptual knowledge base. This system aims to provide an up-to-date repository of information that can be queried by AI agents or other components of the ecosystem.

The core Python module for this system is located at [`src/systems/knowledge_management_system.py`](../../src/systems/knowledge_management_system.py).

## Purpose

The primary goal of the KMS is to:
1.  **Monitor Sources:** Keep track of specified documentation sources (e.g., local directories of markdown files, potentially web pages or code repositories in the future) for new or updated content.
2.  **Process Content:** When changes are detected, read the document content and divide it into smaller, semantically relevant chunks.
3.  **Vectorize Chunks (Conceptual):** Convert these chunks into numerical vector representations (embeddings) that capture their meaning. This step is currently a placeholder.
4.  **Store in Knowledge Base:** Store these chunks and their vectors in a knowledge base (currently an in-memory placeholder, but designed to interface with a vector database) for efficient retrieval.
5.  **Propagate Updates:** Notify other systems (e.g., via MCP events) about updates to the knowledge base. This is also conceptual at present.

## Core Components and Concepts

### 1. `DocumentSource`
   *   Represents a source of documentation (e.g., a local directory).
   *   Attributes: `source_id`, `path_or_url`, `source_type` (e.g., "local_markdown_dir"), `last_scanned_timestamp`, `monitored_files` (dictionary of `filepath: mtime` for local directories).

### 2. `DocumentChunk`
   *   Represents a processed piece of a document.
   *   Attributes: `chunk_id`, `document_id` (ID of parent document), `source_uri`, `content`, `metadata` (e.g., sequence number), `vector` (placeholder for embedding), `last_updated`.

### 3. `DocumentMonitor`
   *   **Purpose:** Monitors registered `DocumentSource` instances for changes.
   *   **Method: `add_source(source: DocumentSource)`**: Adds a new source to monitor.
   *   **Method: `async scan_source(source: DocumentSource) -> List[Tuple[str, str]]`**:
        *   Scans a given source. For `local_markdown_dir`, it walks the directory, checks file modification times against stored states, and identifies "created", "updated", or "deleted" files.
        *   Updates `source.monitored_files` with current states.
        *   Web page monitoring is conceptual.
        *   Returns a list of `(filepath, event_type)` tuples.

### 4. `DocumentProcessor`
   *   **Purpose:** Handles chunking of document content and (placeholder) vectorization.
   *   **Initialization:** Takes `chunk_size` (in characters) and `chunk_overlap`.
   *   **Method: `chunk_document_content(document_id: str, source_uri: str, full_content: str) -> List[DocumentChunk]`**:
        *   Splits `full_content` into `DocumentChunk` objects based on `chunk_size` and `chunk_overlap`.
        *   Generates a `chunk_id` for each chunk.
   *   **Method: `async vectorize_chunk(chunk: DocumentChunk) -> List[float]`**:
        *   Placeholder method that simulates vectorization.
        *   Returns a dummy numerical vector. In a real system, this would call an embedding model.

### 5. `KnowledgeBaseClient`
   *   **Purpose:** A conceptual client for interacting with a knowledge base (e.g., vector store).
   *   **Initialization:** Takes an optional `kb_endpoint`. Currently uses an in-memory dictionary (`self.vector_store`) as a placeholder.
   *   **Method: `async upsert_chunk(chunk: DocumentChunk)`**: Adds or updates a (vectorized) chunk in the `vector_store`.
   *   **Method: `async remove_document_chunks(document_id: str)`**: Removes all chunks associated with a given `document_id` from the `vector_store`.

### 6. `KnowledgeManagementSystem` (Facade)
   *   **Purpose:** The main entry point and orchestrator for the KMS.
   *   **Initialization:** Takes an optional `mcp_server_url` (for conceptual event posting). Initializes `DocumentMonitor`, `DocumentProcessor`, and `KnowledgeBaseClient`.
   *   **Method: `add_document_source(path_or_url: str, source_type: str = "local_markdown_dir", source_id: Optional[str] = None)`**: Creates and adds a `DocumentSource` to the monitor.
   *   **Method: `async run_update_cycle()`**:
        1.  Iterates through all registered `DocumentSource`s.
        2.  Calls `monitor.scan_source()` for each.
        3.  For each detected change (`filepath`, `event_type`):
            *   If "deleted": Calls `kb_client.remove_document_chunks()`.
            *   If "created" or "updated":
                *   Reads the file content.
                *   Calls `processor.chunk_document_content()`.
                *   For each chunk, calls `processor.vectorize_chunk()`.
                *   Calls `kb_client.upsert_chunk()` for the vectorized chunk.
        4.  Logs the outcome of the cycle.
        5.  (Conceptual) Posts events to MCP about knowledge base updates.

:start_line:68
-------
## Integration with MCP Server

The `KnowledgeManagementSystem` is instantiated and managed by the `MCPServer`. This central integration allows the MCP to orchestrate knowledge updates and expose KMS functionalities to other agents and systems.

### Source Configuration

During its initialization, the `MCPServer` configures the `KnowledgeManagementSystem` with predefined document sources. These sources represent key areas of knowledge for the game development ecosystem:

*   `docs/game_design_principles.md`
*   `docs/unity_api_best_practices.md`
*   `docs/scripting_best_practices.md`
*   `docs/existing_assets_placeholders.md`

These sources are added to the KMS using the `add_document_source` method, ensuring that the system continuously monitors these critical knowledge areas.

### Triggering Knowledge Updates

The `MCPServer` exposes a method to trigger the KMS's update cycle, which can be invoked via the `POST /execute_agent` API endpoint.

*   **Endpoint:** `POST /execute_agent`
*   **`agent_id`**: `"kms"`
*   **`parameters`**:
    *   `command_type`: `"trigger_update_cycle"`
    *   No additional parameters are currently required for this command.

When this command is received, the `MCPServer` calls the `kms.run_update_cycle()` method, initiating a scan of all configured document sources, processing any changes, and updating the knowledge base.

## Interaction Flow

1.  `DocumentSource`s are configured with the `KnowledgeManagementSystem` by the `MCPServer`.
2.  The `MCPServer` (or an agent via the API) triggers `kms.run_update_cycle()`.
3.  The `DocumentMonitor` scans sources for changes.
4.  Changed documents are read by the `KnowledgeManagementSystem`.
5.  The `DocumentProcessor` splits content into chunks.
6.  The `DocumentProcessor` (conceptually) vectorizes each chunk.
7.  The `KnowledgeBaseClient` upserts these chunks (with their vectors) into the knowledge base.
8.  If documents are deleted, their corresponding chunks are removed from the knowledge base.

## Example Usage (from `if __name__ == '__main__':`)

The `knowledge_management_system.py` script includes a self-contained demo in its `if __name__ == '__main__':` block:

```python
# In src/systems/knowledge_management_system.py

# ... (setup of TEST_DOCS_PATH with doc1.md, doc2.md) ...

kms = KnowledgeManagementSystem(mcp_server_url="http://localhost:8000/mcp_mock")
kms.add_document_source(path_or_url=TEST_DOCS_PATH, source_type="local_markdown_dir", source_id="test_docs")

async def demo():
    print("\n--- First update cycle (initial processing) ---")
    await kms.run_update_cycle() # Processes doc1.md, doc2.md

    # Simulate a change to doc1.md and addition of doc3.md
    # ... (file modifications) ...

    print("\n--- Second update cycle (processing changes) ---")
    await kms.run_update_cycle() # Processes updated doc1.md, new doc3.md

    # Simulate deletion of doc2.md
    # ... (os.remove(doc2.md)) ...
    
    print("\n--- Third update cycle (processing deletion) ---")
    await kms.run_update_cycle() # Processes deletion of doc2.md
    
    # ... (cleanup TEST_DOCS_PATH) ...

asyncio.run(demo())
```
This example demonstrates the system's ability to detect new files, file updates, and file deletions, and to (conceptually) process and store their content.

## Future Enhancements

*   **Real Vectorization:** Integrate with actual sentence transformer models or other embedding services (e.g., OpenAI, Cohere) for `vectorize_chunk`.
*   **Vector Database Integration:** Replace the in-memory `vector_store` in `KnowledgeBaseClient` with a client for a proper vector database (e.g., Pinecone, Weaviate, FAISS).
*   **Advanced Chunking:** Implement more sophisticated chunking strategies (e.g., based on semantic boundaries, markdown sections, code structures).
*   **Broader Source Support:** Implement monitoring for other `source_type`s like Git repositories or web URLs.
*   **MCP Eventing:** Fully implement the posting of events to the MCP server when the knowledge base is updated, allowing other agents (like `DocumentationSentinelAgent` or query agents) to react.
*   **Error Handling and Resilience:** Add more robust error handling, retries for network operations, etc.
*   **Query Interface:** Add methods to the `KnowledgeBaseClient` and `KnowledgeManagementSystem` to allow querying the knowledge base (e.g., semantic search using query vectors).