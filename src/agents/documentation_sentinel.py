# src/agents/documentation_sentinel.py
import asyncio
import os
import time # For simple timestamping, consider more robust methods for production
from .base_agent import BaseAgent
# from src.mcp_server.models.knowledge_management_models import DocumentChunk # If specific models are defined

class DocumentationSentinelAgent(BaseAgent):
    """
    DocumentationSentinelAgent is responsible for monitoring specified documentation
    sources (e.g., local markdown files, code comments, potentially URLs in the future)
    for changes. When updates are detected, it can process these changes,
    potentially notifying other agents or systems (like a Knowledge Management system)
    via the MCP server.
    """
    def __init__(self, agent_id: str, mcp_server_url: str, capabilities: list = None, watch_paths: list = None):
        super().__init__(agent_id, mcp_server_url, capabilities or ["documentation_monitoring", "change_detection"])
        self.watch_paths = watch_paths if watch_paths is not None else ["docs/"] # Default paths to watch
        self.watched_file_states = {} # Stores {path: last_modified_timestamp}
        self.knowledge_management_system_endpoint = f"{mcp_server_url}/knowledge_update" # Example

    async def initialize_watched_files(self):
        """Initializes the state of watched files."""
        print(f"DocumentationSentinel ({self.agent_id}): Initializing watched files...")
        for path_pattern in self.watch_paths:
            # This is a simplified example; real implementation might use glob, walk specific dirs, etc.
            if os.path.isdir(path_pattern):
                for root, _, files in os.walk(path_pattern):
                    for file in files:
                        if file.endswith((".md", ".py")): # Example file types
                            filepath = os.path.join(root, file)
                            try:
                                self.watched_file_states[filepath] = os.path.getmtime(filepath)
                            except FileNotFoundError:
                                print(f"DocumentationSentinel ({self.agent_id}): File not found during init: {filepath}")
            elif os.path.isfile(path_pattern):
                 try:
                    self.watched_file_states[path_pattern] = os.path.getmtime(path_pattern)
                 except FileNotFoundError:
                    print(f"DocumentationSentinel ({self.agent_id}): File not found during init: {path_pattern}")
        print(f"DocumentationSentinel ({self.agent_id}): Initialized {len(self.watched_file_states)} files.")

    async def check_for_updates(self) -> list:
        """
        Checks watched files for modifications.
        Returns a list of updated file paths.
        """
        updated_files = []
        for filepath, last_mod_time in list(self.watched_file_states.items()): # list() for safe iteration if dict changes
            try:
                current_mod_time = os.path.getmtime(filepath)
                if current_mod_time > last_mod_time:
                    print(f"DocumentationSentinel ({self.agent_id}): Detected change in {filepath}")
                    self.watched_file_states[filepath] = current_mod_time
                    updated_files.append(filepath)
            except FileNotFoundError:
                print(f"DocumentationSentinel ({self.agent_id}): Watched file removed: {filepath}")
                del self.watched_file_states[filepath] # Stop watching removed file
        return updated_files

    async def process_document_update(self, filepath: str):
        """
        Processes an updated document. Placeholder for now.
        This would involve reading the file, potentially chunking it,
        and sending it to a knowledge management system or an LLM for embedding.
        """
        print(f"DocumentationSentinel ({self.agent_id}): Processing update for {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Placeholder: Simulate chunking and creating a "DocumentChunk"
            # document_chunk = DocumentChunk(source_uri=filepath, content=content, last_modified=time.time())
            
            # Placeholder: Notify MCP or Knowledge Management System
            event_data = {
                "document_path": filepath,
                "update_type": "modification", # or "creation", "deletion"
                "timestamp": time.time(),
                # "chunk_summary": f"Content of {filepath} updated." # Or actual chunk data
            }
            print(f"DocumentationSentinel ({self.agent_id}): Posting doc_update event for {filepath}")
            await self.post_event_to_mcp(event_type="documentation_updated", event_data=event_data)

            # Example: Directly post to a hypothetical knowledge management system
            # await self.http_client.post(self.knowledge_management_system_endpoint, json=document_chunk.dict())

        except Exception as e:
            print(f"DocumentationSentinel ({self.agent_id}): Error processing {filepath}: {e}")
            await self.post_event_to_mcp(
                event_type="agent_internal_error",
                event_data={"error": str(e), "context": f"Processing document update for {filepath}"}
            )


    async def process_task(self, task_details: dict) -> dict:
        """
        Process a task, e.g., 'monitor_documentation' or 'rescan_sources'.
        For now, this agent might operate more on a continuous loop or triggered externally.
        """
        print(f"DocumentationSentinel ({self.agent_id}) received task: {task_details}")
        task_type = task_details.get("type")
        task_id = task_details.get("task_id", "N/A")

        if task_type == "scan_documentation_sources":
            await self.initialize_watched_files() # Re-initialize and scan
            updated_files = await self.check_for_updates() # Check immediately after scan
            for updated_file in updated_files:
                await self.process_document_update(updated_file)
            
            message = f"Documentation scan complete. Found {len(updated_files)} initial updates."
            await self.post_event_to_mcp(
                event_type="agent_task_completed",
                event_data={"task_id": task_id, "agent_id": self.agent_id, "result": {"updated_files_count": len(updated_files)}, "message": message}
            )
            return {"status": "completed", "task_id": task_id, "message": message}
        
        # Default behavior if task type is not recognized or if it's a general "run" command
        # This agent might primarily run a monitoring loop rather than discrete tasks.
        # For this example, we'll just acknowledge.
        unsupported_message = f"Task type '{task_type}' not fully supported for direct processing by DocumentationSentinel. Agent primarily monitors."
        print(f"DocumentationSentinel ({self.agent_id}): {unsupported_message}")
        await self.post_event_to_mcp(
            event_type="agent_task_info",
            event_data={"task_id": task_id, "agent_id": self.agent_id, "message": unsupported_message}
        )
        return {"status": "info", "task_id": task_id, "message": unsupported_message}

    async def monitoring_loop(self, interval_seconds: int = 60):
        """
        Continuously monitors documentation sources for changes.
        """
        await self.initialize_watched_files()
        print(f"DocumentationSentinel ({self.agent_id}): Starting monitoring loop (interval: {interval_seconds}s)...")
        try:
            while True:
                updated_files = await self.check_for_updates()
                for filepath in updated_files:
                    await self.process_document_update(filepath)
                
                if updated_files:
                    print(f"DocumentationSentinel ({self.agent_id}): Processed {len(updated_files)} updates in this cycle.")
                
                await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            print(f"DocumentationSentinel ({self.agent_id}): Monitoring loop cancelled.")
        finally:
            print(f"DocumentationSentinel ({self.agent_id}): Monitoring loop stopped.")

if __name__ == '__main__':
    async def main_loop():
        mcp_url = "http://localhost:8000/mcp" # Example MCP URL
        agent = DocumentationSentinelAgent(
            agent_id="doc_sentinel_001", 
            mcp_server_url=mcp_url,
            watch_paths=["./docs", "./src"] # Watch project's docs and src for demo
        )
        
        # In a real deployment, registration would happen, and the loop might be started by MCP
        # await agent.register_with_mcp()

        # Start the monitoring loop (this will run indefinitely until cancelled)
        try:
            # For demonstration, run a task first
            example_task = {"task_id": "ds_task_scan_01", "type": "scan_documentation_sources"}
            await agent.process_task(example_task)

            # Then start the loop
            await agent.monitoring_loop(interval_seconds=10) # Short interval for demo
        except KeyboardInterrupt:
            print("DocumentationSentinel demo interrupted by user.")
        finally:
            await agent.shutdown()

    asyncio.run(main_loop())