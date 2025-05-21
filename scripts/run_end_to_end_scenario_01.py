# scripts/run_end_to_end_scenario_01.py
import asyncio
import logging
import os
import sys
import time
from typing import List, Dict, Any

# Ensure src directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import necessary components (assuming they are in src)
# Agents
from agents.level_architect_agent import LevelArchitectAgent # Assuming this exists as per context
from agents.pixel_forge_agent import PixelForgeAgent
from agents.base_agent import BaseAgent # For type hinting if needed

# Toolchains
from toolchains.retro_diffusion_bridge import RetroDiffusionBridge
# from toolchains.muse_bridge import MuseBridge # If Muse was used in this scenario

# Configure basic logging for the scenario
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("E2E_Scenario_01")

# --- Mock MCP and Global Event Log ---
MOCK_MCP_URL = "http://localhost:8000/mcp_mock"
event_log: List[Dict[str, Any]] = []

def log_event(event_type: str, source: str, details: Dict[str, Any]):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    log_entry = {"timestamp": timestamp, "event_type": event_type, "source": source, "details": details}
    logger.info(f"EVENT: {log_entry}")
    event_log.append(log_entry)

# --- Scenario Specific Agent Logic (Simplified/Mocked for this script) ---

async def run_level_architect_design_phase(
    architect: Any, # Should be LevelArchitectAgent instance
    design_task_details: Dict[str, Any],
    retro_diffusion_bridge: RetroDiffusionBridge # LA will use this directly for simplicity
):
    log_event("task_received", architect.agent_id, {"task_id": design_task_details["task_id"], "description": "Received level design task"})
    
    # 1. Architect conceptualizes level (mocked)
    await asyncio.sleep(0.2)
    level_concept = f"Enchanted forest clearing with {design_task_details['theme_elements']}"
    log_event("design_progress", architect.agent_id, {"task_id": design_task_details["task_id"], "status": "Conceptualized layout", "concept": level_concept})

    # 2. Architect decides it needs a specific asset (e.g., glowing mushroom sprite)
    asset_prompt = "A vibrant, glowing mushroom sprite for an enchanted forest"
    log_event("asset_requirement_identified", architect.agent_id, {"task_id": design_task_details["task_id"], "asset_needed": asset_prompt})

    # 3. Architect requests PixelForge (via RetroDiffusionBridge directly in this mock) to generate it
    # In a real system, this would be an MCP task to PixelForgeAgent.
    # PixelForgeAgent would then use its internal bridge.
    # Here, LA directly uses the bridge as a shortcut for the scenario.
    log_event("toolchain_request_sent", architect.agent_id, {
        "toolchain": "RetroDiffusionBridge", 
        "request_type": "GENERATE_IMAGE_ASSET", 
        "prompt": asset_prompt
    })
    
    asset_future = retro_diffusion_bridge.generate_image(
        prompt=asset_prompt, 
        resolution="128x128", # Smaller for a sprite
        agent_id=architect.agent_id # LA is initiating this tool use
    )
    
    try:
        # .result() is blocking, but RetroDiffusionBridge uses a thread, so it works.
        # In a fully async agent, one would 'await future' if the bridge was fully async.
        asset_result = asset_future.result(timeout=10) # Wait for the threaded task
        log_event("toolchain_response_received", architect.agent_id, {"toolchain": "RetroDiffusionBridge", "result_status": asset_result.get("status"), "asset_details": asset_result})
        
        if asset_result.get("status") == "success_mock":
            generated_asset_path = asset_result.get("image_path", "unknown_path")
            log_event("asset_integration", architect.agent_id, {"task_id": design_task_details["task_id"], "asset_id": generated_asset_path, "status": "Asset integrated into design concept"})
        else:
            log_event("asset_generation_failed", architect.agent_id, {"task_id": design_task_details["task_id"], "error": "Asset generation via toolchain failed", "details": asset_result})
            
    except Exception as e:
        log_event("toolchain_error", architect.agent_id, {"toolchain": "RetroDiffusionBridge", "error": str(e)})

    # 4. Architect finalizes design (mocked)
    await asyncio.sleep(0.1)
    log_event("task_completed", architect.agent_id, {"task_id": design_task_details["task_id"], "status": "Level design phase complete", "final_design_summary": f"Completed: {level_concept} with asset: {asset_prompt}"})


async def main_scenario():
    logger.info("--- Starting E2E Scenario 01: Level Design with Asset Generation ---")

    # --- Setup Components ---
    # Mock MCP Server (represented by the event_log and direct calls)
    log_event("mcp_status", "MCP_Simulator", {"status": "Scenario Initialized"})

    # Initialize Toolchains (these start their own worker threads if not already started by other means)
    # No explicit mcp_server instance needed for bridges if they don't use it beyond logging.
    # The BaseToolchainBridge takes mcp_server, but it's used for logging context.
    # We can pass a simple mock object if needed by the base class.
    class MockMCPServerForBridge:
        def __init__(self, name="ScenarioMockMCP"):
            self.name = name
    
    mock_mcp_for_bridge = MockMCPServerForBridge()
    
    retro_bridge = RetroDiffusionBridge(mcp_server=mock_mcp_for_bridge)
    # muse_bridge = MuseBridge(mcp_server=mock_mcp_for_bridge) # If needed

    # Initialize Agents
    # For LevelArchitectAgent, we'll use a placeholder if its real __init__ is complex
    # or if its process_task is too intricate to call directly for this scenario.
    # The context says LA is implemented. We'll assume a simple init.
    try:
        level_architect = LevelArchitectAgent(agent_id="LevelArchitect_E2E_01", mcp_server_url=MOCK_MCP_URL)
        # We will call our scenario-specific logic instead of its real process_task
    except TypeError as e: # Catch if LevelArchitectAgent init is more complex
        logger.warning(f"Could not init LevelArchitectAgent normally ({e}), using placeholder object.")
        class PlaceholderArchitect:
            agent_id = "LevelArchitect_E2E_01_Placeholder"
        level_architect = PlaceholderArchitect()


    # PixelForgeAgent is not directly "tasked" in this simplified scenario;
    # its capability is invoked via the RetroDiffusionBridge by the LevelArchitect.
    # If LA were to create an MCP task for PF, we'd init PF here.
    # pixel_forge = PixelForgeAgent(agent_id="PixelForge_E2E_01", mcp_server_url=MOCK_MCP_URL)


    log_event("component_setup_complete", "ScenarioRunner", {"agents_initialized": [level_architect.agent_id], "toolchains_initialized": [retro_bridge.bridge_name]})

    # --- Run Scenario Steps ---
    
    # 1. MCP (simulated) assigns a high-level task to LevelArchitectAgent
    main_task_id = "e2e_task_design_forest_clearing_001"
    design_task = {
        "task_id": main_task_id,
        "type": "design_level_area",
        "description": "Design a small enchanted forest clearing.",
        "theme_elements": ["glowing flora", "ancient stones", "mystical atmosphere"],
        "output_requirements": ["layout_map_concept", "key_asset_list"]
    }
    log_event("mcp_task_dispatch", "MCP_Simulator", {"target_agent": level_architect.agent_id, "task_id": main_task_id})

    # 2. LevelArchitectAgent processes the task (using our scenario-specific function)
    await run_level_architect_design_phase(level_architect, design_task, retro_bridge)
    
    # --- Scenario End ---
    log_event("mcp_status", "MCP_Simulator", {"status": "Scenario Complete"})
    logger.info("--- E2E Scenario 01 Finished ---")

    # Print all logged events
    print("\n--- Full Event Log ---")
    for entry in event_log:
        print(entry)
    
    # Shutdown toolchain bridges
    retro_bridge.shutdown()
    # muse_bridge.shutdown() # If used

if __name__ == "__main__":
    asyncio.run(main_scenario())

    # Expected output will show a sequence of events:
    # - MCP initializing and dispatching task
    # - LevelArchitect receiving task, conceptualizing, identifying asset need
    # - LevelArchitect requesting asset via RetroDiffusionBridge
    # - RetroDiffusionBridge processing and returning (mock) asset
    # - LevelArchitect integrating asset and completing task
    # - MCP scenario completion