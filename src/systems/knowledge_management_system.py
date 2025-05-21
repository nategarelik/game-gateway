# src/systems/knowledge_management_system.py
import asyncio
import os
import time
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# --- Conceptual Data Structures ---

class DocumentSource:
    """Represents a source of documentation to be monitored."""
    def __init__(self, source_id: str, path_or_url: str, source_type: str = "local_markdown_dir"):
        self.source_id = source_id
        self.path_or_url = path_or_url # Could be a local directory, file, or a URL
        self.source_type = source_type # e.g., "local_markdown_dir", "git_repository", "web_page"
        self.last_scanned_timestamp: Optional[float] = None
        self.monitored_files: Dict[str, float] = {} # For local dirs: {filepath: mtime}

class DocumentChunk:
    """Represents a chunk of a document, potentially ready for vectorization."""
    def __init__(self, chunk_id: str, document_id: str, source_uri: str, content: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id # e.g., hash of content or sequential ID
        self.document_id = document_id # ID of the parent document
        self.source_uri = source_uri # Original path or URL of the document
        self.content = content
        self.metadata = metadata # e.g., section headers, page number
        self.vector: Optional[List[float]] = None # Placeholder for embedding vector
        self.last_updated: float = time.time()

    def __repr__(self):
        return f"<DocumentChunk id='{self.chunk_id}' source='{self.source_uri}' len='{len(self.content)}'>"

# --- Core System Components (Conceptual Implementations) ---

class DocumentMonitor:
    """Monitors specified document sources for changes."""
    def __init__(self):
        self.sources_to_monitor: List[DocumentSource] = []
        logger.info("DocumentMonitor initialized.")

    def add_source(self, source: DocumentSource):
        self.sources_to_monitor.append(source)
        logger.info(f"Added document source: {source.source_id} ({source.path_or_url})")

    async def scan_source(self, source: DocumentSource) -> List[Tuple[str, str]]: # Returns (filepath, 'event_type')
        """
        Scans a single source for new or updated documents.
        'event_type' can be 'created', 'updated', 'deleted'.
        This is a simplified placeholder.
        """
        changed_items = []
        if source.source_type == "local_markdown_dir":
            if not os.path.isdir(source.path_or_url):
                logger.warning(f"Source path for {source.source_id} is not a directory: {source.path_or_url}")
                return []
            
            current_files = {}
            for root, _, files in os.walk(source.path_or_url):
                for file in files:
                    if file.endswith(".md"): # Focus on markdown for this example
                        filepath = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(filepath)
                            current_files[filepath] = mtime
                            
                            if filepath not in source.monitored_files:
                                changed_items.append((filepath, "created"))
                                logger.info(f"Detected new file in {source.source_id}: {filepath}")
                            elif source.monitored_files[filepath] < mtime:
                                changed_items.append((filepath, "updated"))
                                logger.info(f"Detected update in {source.source_id}: {filepath}")
                        except FileNotFoundError:
                            continue # File might have been deleted during scan
            
            # Check for deleted files
            deleted_files = [fp for fp in source.monitored_files if fp not in current_files]
            for fp in deleted_files:
                changed_items.append((fp, "deleted"))
                logger.info(f"Detected deleted file in {source.source_id}: {fp}")

            source.monitored_files = current_files # Update the state
            
        elif source.source_type == "web_page":
            logger.info(f"Web page monitoring for {source.path_or_url} is conceptual and not implemented.")
            # Placeholder: fetch content, compare hash with previous, etc.
            # For now, simulate an update occasionally if it's the first scan
            if source.last_scanned_timestamp is None:
                 changed_items.append((source.path_or_url, "updated")) # Simulate initial fetch as an update
        
        source.last_scanned_timestamp = time.time()
        return changed_items


class DocumentProcessor:
    """Processes document content, including chunking and placeholder vectorization."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size # Characters
        self.chunk_overlap = chunk_overlap
        logger.info(f"DocumentProcessor initialized. Chunk size: {chunk_size}, Overlap: {chunk_overlap}")

    def _generate_chunk_id(self, document_id: str, content_part: str) -> str:
        return hashlib.md5(f"{document_id}:{content_part}".encode()).hexdigest()

    def chunk_document_content(self, document_id: str, source_uri: str, full_content: str) -> List[DocumentChunk]:
        """Splits document content into manageable chunks."""
        chunks = []
        content_len = len(full_content)
        start_index = 0
        chunk_seq = 0
        while start_index < content_len:
            end_index = min(start_index + self.chunk_size, content_len)
            content_part = full_content[start_index:end_index]
            
            chunk_id = self._generate_chunk_id(document_id, content_part[:50] + str(chunk_seq)) # Use part of content and sequence for ID
            chunk_metadata = {"sequence": chunk_seq, "source_char_start": start_index, "source_char_end": end_index}
            
            doc_chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                source_uri=source_uri,
                content=content_part,
                metadata=chunk_metadata
            )
            chunks.append(doc_chunk)
            
            chunk_seq += 1
            start_index += (self.chunk_size - self.chunk_overlap)
            if start_index >= end_index and end_index < content_len : # Ensure progress if overlap is large or chunk small
                start_index = end_index 
        return chunks

    async def vectorize_chunk(self, chunk: DocumentChunk) -> List[float]:
        """
        Placeholder for vectorizing a document chunk using an embedding model.
        Returns a dummy vector.
        """
        logger.debug(f"Simulating vectorization for chunk: {chunk.chunk_id} from {chunk.source_uri}")
        await asyncio.sleep(0.05) # Simulate I/O or computation
        # Create a dummy vector based on content length and first char
        dummy_vector = [len(chunk.content) * 0.001, ord(chunk.content[0]) * 0.01 if chunk.content else 0.0] + [0.0] * 8 # Example 10-dim vector
        return dummy_vector[:10] # Ensure fixed size

class KnowledgeBaseClient:
    """
    A conceptual client for interacting with a knowledge base (e.g., a vector store).
    This would handle storing, updating, and retrieving document chunks/vectors.
    """
    def __init__(self, kb_endpoint: Optional[str] = None):
        self.kb_endpoint = kb_endpoint # e.g., URL to a vector database API
        self.vector_store: Dict[str, DocumentChunk] = {} # In-memory placeholder
        logger.info(f"KnowledgeBaseClient initialized. Endpoint: {self.kb_endpoint or 'In-memory'}")

    async def upsert_chunk(self, chunk: DocumentChunk):
        """Adds or updates a chunk in the knowledge base."""
        if chunk.vector is None:
            logger.warning(f"Attempted to upsert chunk {chunk.chunk_id} without a vector. Skipping.")
            return
        
        logger.info(f"Upserting chunk {chunk.chunk_id} (source: {chunk.source_uri}) into KB.")
        self.vector_store[chunk.chunk_id] = chunk
        # In a real system:
        # await http_client.post(f"{self.kb_endpoint}/upsert", json=chunk.to_dict_for_kb())
        await asyncio.sleep(0.02) # Simulate KB interaction

    async def remove_document_chunks(self, document_id: str):
        """Removes all chunks associated with a document_id from the KB."""
        chunks_to_remove = [cid for cid, chunk in self.vector_store.items() if chunk.document_id == document_id]
        for cid in chunks_to_remove:
            del self.vector_store[cid]
        logger.info(f"Removed {len(chunks_to_remove)} chunks for document_id {document_id} from KB.")
        # In a real system:
        # await http_client.post(f"{self.kb_endpoint}/delete_by_doc_id", json={"document_id": document_id})
        await asyncio.sleep(0.01 * len(chunks_to_remove))


class KnowledgeManagementSystem:
    """
    Main facade for the Knowledge Management System.
    Orchestrates monitoring, processing, and storing document information.
    """
    def __init__(self, mcp_server_url: Optional[str] = None): # mcp_server_url for event posting
        self.monitor = DocumentMonitor()
        self.processor = DocumentProcessor()
        self.kb_client = KnowledgeBaseClient() # Could be configured with a real endpoint
        self.mcp_server_url = mcp_server_url # For posting events about KB updates
        self._processing_lock = asyncio.Lock() # Ensure one processing cycle at a time
        logger.info("KnowledgeManagementSystem initialized.")

    def add_document_source(self, path_or_url: str, source_type: str = "local_markdown_dir", source_id: Optional[str] = None):
        if source_id is None:
            source_id = hashlib.md5(path_or_url.encode()).hexdigest()[:10]
        source = DocumentSource(source_id=source_id, path_or_url=path_or_url, source_type=source_type)
        self.monitor.add_source(source)

    async def _process_file_change(self, filepath: str, event_type: str, source_id: str):
        document_id = hashlib.md5(filepath.encode()).hexdigest() # Simple ID based on path

        if event_type == "deleted":
            await self.kb_client.remove_document_chunks(document_id)
            logger.info(f"Processed deletion of document: {filepath} (ID: {document_id})")
            # Post event to MCP
            if self.mcp_server_url: pass # Placeholder for actual event posting logic
            return

        try:
            # For 'created' or 'updated', read, chunk, vectorize, and upsert
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = self.processor.chunk_document_content(document_id, filepath, content)
            logger.info(f"Generated {len(chunks)} chunks for {filepath}")

            for chunk in chunks:
                chunk.vector = await self.processor.vectorize_chunk(chunk)
                await self.kb_client.upsert_chunk(chunk)
            
            logger.info(f"Successfully processed and stored document: {filepath} (ID: {document_id})")
            # Post event to MCP
            if self.mcp_server_url: pass # Placeholder for actual event posting logic

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}", exc_info=True)


    async def run_update_cycle(self):
        """Scans all sources, processes changes, and updates the knowledge base."""
        async with self._processing_lock:
            logger.info("Starting Knowledge Management update cycle...")
            all_changes_count = 0
            for source in self.monitor.sources_to_monitor:
                logger.info(f"Scanning source: {source.source_id} ({source.path_or_url})...")
                changed_files_events = await self.monitor.scan_source(source)
                all_changes_count += len(changed_files_events)
                for filepath, event_type in changed_files_events:
                    await self._process_file_change(filepath, event_type, source.source_id)
            
            logger.info(f"Knowledge Management update cycle finished. Processed {all_changes_count} changes across all sources.")
            logger.info(f"Current KB size (in-memory chunks): {len(self.kb_client.vector_store)}")


# --- Example Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a dummy docs directory for testing
    TEST_DOCS_PATH = "temp_km_docs"
    os.makedirs(TEST_DOCS_PATH, exist_ok=True)
    with open(os.path.join(TEST_DOCS_PATH, "doc1.md"), "w") as f:
        f.write("# Document 1\nThis is the first test document with some initial content.")
    with open(os.path.join(TEST_DOCS_PATH, "doc2.md"), "w") as f:
        f.write("# Document 2\nContent for the second document. It is a bit longer to test chunking effectively. " * 50)

    kms = KnowledgeManagementSystem(mcp_server_url="http://localhost:8000/mcp_mock") # MCP URL is for conceptual event posting
    kms.add_document_source(path_or_url=TEST_DOCS_PATH, source_type="local_markdown_dir", source_id="test_docs")

    async def demo():
        print("\n--- First update cycle (initial processing) ---")
        await kms.run_update_cycle()

        # Simulate a change
        print("\n--- Simulating change to doc1.md ---")
        time.sleep(0.1) # Ensure mtime changes
        with open(os.path.join(TEST_DOCS_PATH, "doc1.md"), "a") as f:
            f.write("\n\nSome appended content to simulate an update.")
        
        # Simulate adding a new file
        print("\n--- Simulating adding doc3.md ---")
        with open(os.path.join(TEST_DOCS_PATH, "doc3.md"), "w") as f:
            f.write("# Document 3\nA brand new document.")

        print("\n--- Second update cycle (processing changes) ---")
        await kms.run_update_cycle()
        
        # Simulate deleting a file
        print("\n--- Simulating deleting doc2.md ---")
        os.remove(os.path.join(TEST_DOCS_PATH, "doc2.md"))
        
        print("\n--- Third update cycle (processing deletion) ---")
        await kms.run_update_cycle()

        # Clean up dummy directory
        import shutil
        shutil.rmtree(TEST_DOCS_PATH)
        print(f"\nCleaned up {TEST_DOCS_PATH}")

    asyncio.run(demo())