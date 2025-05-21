# tests/agents/test_documentation_sentinel.py
import pytest
import asyncio
import os
import time
import shutil # Added for rmtree
from unittest.mock import AsyncMock, patch, mock_open

# Ensure the src directory is in the Python path for imports
import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))) # No longer needed with pyproject.toml

from src.agents.documentation_sentinel_agent import DocumentationSentinelAgent
from src.agents.base_agent import BaseAgent # Corrected import

MOCK_MCP_URL = "http://localhost:8000/mcp_mock"
TEST_DOCS_DIR = "test_docs_temp"
TEST_FILE_MD = os.path.join(TEST_DOCS_DIR, "test_doc.md")
TEST_FILE_PY = os.path.join(TEST_DOCS_DIR, "test_code.py")
TEST_SUBDIR = os.path.join(TEST_DOCS_DIR, "subdir")
TEST_FILE_SUBDIR_MD = os.path.join(TEST_SUBDIR, "another_doc.md")

@pytest.fixture
def sentinel_agent():
    """Provides a DocumentationSentinelAgent instance."""
    agent = DocumentationSentinelAgent(
        agent_id="test_doc_sentinel_01",
        mcp_server_url=MOCK_MCP_URL,
        monitored_sources=[TEST_FILE_MD, TEST_FILE_PY] # Example sources
    )
    agent.http_client = AsyncMock() # Mock HTTP client
    agent.http_client.post.return_value = AsyncMock(status_code=200, json=lambda: {"status": "ok"}) # Default success
    return agent

@pytest.mark.asyncio
async def test_sentinel_agent_initialization(sentinel_agent: DocumentationSentinelAgent):
    assert sentinel_agent.agent_id == "test_doc_sentinel_01"
    assert sentinel_agent.mcp_server_url == MOCK_MCP_URL
    assert "documentation_monitoring" in sentinel_agent.capabilities
    assert isinstance(sentinel_agent, BaseAgent)
    assert sentinel_agent.monitored_sources == [TEST_FILE_MD, TEST_FILE_PY]

@pytest.mark.asyncio
async def test_process_task_check_source_updates_success(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_check_001",
        "task_type": "CHECK_SOURCE_UPDATES",
        "source_uri": "docs/some_document.md" # This is a mock URI for the test
    }
    # Mocking os.path.exists and os.path.getmtime if the agent uses them directly
    # For now, the agent's CHECK_SOURCE_UPDATES is a placeholder.
    
    result = await sentinel_agent.process_task(task_details)
    
    assert result["status"] == "success"
    assert "mock update found" in result["message"] # Based on current placeholder logic
    
    # Check for 'doc_source_updated' event
    event_posted = False
    for call in sentinel_agent.http_client.post.call_args_list:
        if call[0][0].endswith('/post_event') and call[1]['json']['event_type'] == 'doc_source_updated':
            assert call[1]['json']['data']['source_uri'] == "docs/some_document.md"
            event_posted = True
            break
    assert event_posted

@pytest.mark.asyncio
async def test_process_task_check_source_updates_missing_uri(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_check_002",
        "task_type": "CHECK_SOURCE_UPDATES",
        # "source_uri": missing
    }
    result = await sentinel_agent.process_task(task_details)
    assert result["status"] == "failure"
    assert "Missing source_uri" in result["message"]

@pytest.mark.asyncio
async def test_process_task_process_document_chunk_success(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_proc_001",
        "task_type": "PROCESS_DOCUMENT_CHUNK",
        "document_uri": "docs/some_document.md",
        "chunk_content": "This is a test chunk.",
        "metadata": {"page": 1}
    }
    result = await sentinel_agent.process_task(task_details)
    assert result["status"] == "success"
    assert f"Processed chunk from {task_details['document_uri']}" in result["message"]

    # Check for 'doc_chunk_processed' event
    event_posted = False
    for call in sentinel_agent.http_client.post.call_args_list:
         if call[0][0].endswith('/post_event') and call[1]['json']['event_type'] == 'doc_chunk_processed':
            assert call[1]['json']['data']['document_uri'] == task_details['document_uri']
            event_posted = True
            break
    assert event_posted

@pytest.mark.asyncio
async def test_process_task_process_document_chunk_missing_data(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_proc_002",
        "task_type": "PROCESS_DOCUMENT_CHUNK",
        # "document_uri": missing
        "chunk_content": "Some content."
    }
    result = await sentinel_agent.process_task(task_details)
    assert result["status"] == "failure"
    assert "Missing document_uri or chunk_content" in result["message"]

@pytest.mark.asyncio
async def test_process_task_unknown_type(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_unknown_001",
        "task_type": "UNKNOWN_TASK_TYPE"
    }
    result = await sentinel_agent.process_task(task_details)
    assert result["status"] == "failure"
    assert "Unknown task type" in result["message"]

@pytest.mark.asyncio
async def test_check_all_sources_posts_events(sentinel_agent: DocumentationSentinelAgent):
    # Re-initialize monitored_sources for this specific test if needed, or use fixture's
    agent = sentinel_agent
    agent.monitored_sources = ["source1.md", "source2.txt"] # Override for clarity
    agent.http_client.post.reset_mock() # Reset mock for clean call count

    result = await agent.check_all_sources()
    assert result["status"] == "success"
    
    # Check that post_event_to_mcp was called for each source
    assert agent.http_client.post.call_count == len(agent.monitored_sources)
    
    posted_source_uris = []
    for call in agent.http_client.post.call_args_list:
        if call[0][0].endswith('/post_event') and call[1]['json']['event_type'] == 'doc_source_check_scheduled':
            posted_source_uris.append(call[1]['json']['data']['source_uri'])
            
    assert "source1.md" in posted_source_uris
    assert "source2.txt" in posted_source_uris

# Note: The original tests for file system interactions (initialize_watched_files, check_for_updates)
# are removed because the current DocumentationSentinelAgent does not implement that file watching logic.
# Its current capabilities are based on receiving tasks like "CHECK_SOURCE_UPDATES" (which is a placeholder)
# and "PROCESS_DOCUMENT_CHUNK". The `check_all_sources` method is also a placeholder.
# If file system watching is re-introduced to the agent, those tests would need to be adapted.

@pytest.mark.asyncio
async def test_generate_script_documentation(sentinel_agent: DocumentationSentinelAgent):
    script_name = "MyTestScript"
    script_content = "using UnityEngine; public class MyTestScript : MonoBehaviour {}"
    
    doc = await sentinel_agent.generate_script_documentation(script_content, script_name)
    
    assert f"# API Documentation for {script_name}.cs" in doc
    assert "## Overview" in doc
    assert "## Methods" in doc
    assert "- `Start()`: Initializes the script. (Mock description)" in doc
    assert "Generated by DocumentationSentinelAgent." in doc

@pytest.mark.asyncio
async def test_process_task_generate_script_docs_success(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_gen_script_001",
        "task_type": "GENERATE_SCRIPT_DOCS",
        "script_name": "PlayerController",
        "script_content": "using UnityEngine; public class PlayerController : MonoBehaviour { void Update() {} }"
    }
    
    # Mock the internal method to ensure it's called
    sentinel_agent.generate_script_documentation = AsyncMock(return_value="Mocked documentation content.")

    result = await sentinel_agent.process_task(task_details)
    
    sentinel_agent.generate_script_documentation.assert_awaited_once_with(
        task_details["script_content"], task_details["script_name"]
    )
    
    assert result["status"] == "success"
    assert "Generated documentation for PlayerController." in result["message"]
    assert result["generated_documentation"] == "Mocked documentation content."
    
    # Check for 'script_documentation_generated' event
    event_posted = False
    for call in sentinel_agent.http_client.post.call_args_list:
        if call[0][0].endswith('/post_event') and call[1]['json']['event_type'] == 'script_documentation_generated':
            assert call[1]['json']['data']['script_name'] == task_details['script_name']
            assert call[1]['json']['data']['documentation'] == "Mocked documentation content."
            event_posted = True
            break
    assert event_posted

@pytest.mark.asyncio
async def test_process_task_generate_script_docs_missing_data(sentinel_agent: DocumentationSentinelAgent):
    task_details = {
        "task_id": "doc_gen_script_002",
        "task_type": "GENERATE_SCRIPT_DOCS",
        "script_name": "MissingContentScript"
        # script_content is missing
    }
    
    result = await sentinel_agent.process_task(task_details)
    
    assert result["status"] == "failure"
    assert "Missing 'script_name' or 'script_content' for GENERATE_SCRIPT_DOCS" in result["message"]
    # Ensure generate_script_documentation was NOT called
    sentinel_agent.generate_script_documentation.assert_not_called()