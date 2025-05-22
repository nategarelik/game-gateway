# MCP Server Main Entry Point
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from src.mcp_server.api import routes as api_routes
from src.mcp_server.core.state_manager import StateManager
from src.mcp_server.core.prompt_registry import PromptRegistry

app = FastAPI(
    title="MCP Server",
    description="Master Control Program Server for Autonomous AI Agent Ecosystem",
    version="0.1.0"
)

# Load environment variables from .env file
load_dotenv()

# Include API routes
app.include_router(api_routes.router, prefix="/api/v1")

# Initialize core server components
app.state.registered_agents = {}
state_manager = StateManager(registered_agents=app.state.registered_agents)
prompt_registry = PromptRegistry()
app.state.state_manager = state_manager
app.state.prompt_registry = prompt_registry

@app.get("/")
async def root():
    return {"message": "MCP Server is running. Visit /docs for API documentation."}

if __name__ == "__main__":
    # For development, run with uvicorn directly:
    # uvicorn src.mcp_server.main:app --reload
    print("Starting MCP Server. Run with: uvicorn src.mcp_server.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)