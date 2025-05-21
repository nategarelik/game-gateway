# MCP Server Main Entry Point
import uvicorn
from fastapi import FastAPI

from src.mcp_server.api import routes as api_routes
from src.mcp_server.core.state_manager import StateManager
from src.mcp_server.core.prompt_registry import PromptRegistry
# Potentially import core server logic if needed for initialization
# from src.mcp_server.core.server import MCPServer

app = FastAPI(
    title="MCP Server",
    description="Master Control Program Server for Autonomous AI Agent Ecosystem",
    version="0.1.0" # This should ideally match or be derived from api_routes.MCP_SERVER_VERSION
)

# Include API routes
app.include_router(api_routes.router, prefix="/api/v1") # Added a version prefix

# Initialize core server components
state_manager = StateManager()
prompt_registry = PromptRegistry()

# Make them accessible in routes via app.state
app.state.state_manager = state_manager
app.state.prompt_registry = prompt_registry
app.state.registered_agents = {} # Initialize registered agents store

# Example: Initialize core server components if necessary
# mcp_instance = MCPServer()
# app.state.mcp_instance = mcp_instance

@app.get("/")
async def root():
    return {"message": "MCP Server is running. Visit /docs for API documentation."}

if __name__ == "__main__":
    # TODO: Initialize and run the MCP Server
    # For development, run with uvicorn directly:
    # uvicorn src.mcp_server.main:app --reload
    print("Starting MCP Server. Run with: uvicorn src.mcp_server.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)