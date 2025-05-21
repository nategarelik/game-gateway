# PixelForgeAgent Documentation

## Purpose

The `PixelForgeAgent` specializes in generating pixel art assets for game development, such as sprites, textures, and concept art. It serves as an interface between the game development state or direct requests and an underlying diffusion model toolchain, specifically the `RetroDiffusionToolchainBridge`. Its role is to interpret asset generation requirements and translate them into calls to the toolchain, integrating the generated assets back into the development process or providing them as a direct response.

## Core Methods

### `handle_direct_request(self, request_data: dict) -> dict`

This method handles immediate requests to generate an image asset. It is designed for scenarios where a specific asset is needed on demand, outside of the agent's autonomous execution loop.

*   **Expected Inputs (`request_data`):** A dictionary containing the details for the asset generation. Key parameters include:
    *   `prompt` (str): The textual description for the image to be generated.
    *   `parameters` (dict, optional): A dictionary of parameters specific to the `RetroDiffusionToolchainBridge`, such as `resolution` (e.g., `[width, height]`), `tileable` (bool), `animation_frames` (int), `palette_lock` (bool), etc.
*   **Logic:**
    1.  Validates that a `prompt` is provided in the `request_data`.
    2.  Calls the `generate_asset` method of the internal `RetroDiffusionToolchainBridge` instance, passing the `prompt`, `parameters`, and the agent's ID.
    3.  Waits for the result from the toolchain bridge (currently a blocking call with a 60-second timeout).
    4.  Processes the result, which is expected to be a `MockImageData` object (or similar structure for real image data).
*   **Outputs:** A dictionary indicating the status and result of the generation.
    *   On success: `{"status": "success", "message": "...", "asset_id": "...", "image_data_b64": "..."}` (or `image_path`).
    *   On failure (e.g., missing prompt, timeout, toolchain error): `{"status": "error", "message": "..."}`.

### `execute(self, state: GameDevState) -> GameDevState`

This method defines the agent's behavior within a larger game development workflow, driven by the current `GameDevState`. It is intended to be called periodically to allow the agent to check for and process pending asset generation tasks defined within the state.

*   **Expected Inputs (`state`):** An instance of the `GameDevState` object, which holds the current state and requirements of the game development project.
*   **Logic:**
    1.  Logs the start of the execution with the current state.
    2.  Attempts to retrieve a list of pending pixel art requests from the `GameDevState`. This is conceptually expected via a method like `get_pending_pixel_art_requests` or by checking a specific data structure within the state (e.g., `state.data["pixel_art_tasks"]`).
    3.  If pending requests are found, it iterates through them.
    4.  For each task, it extracts the `asset_name`, `prompt`, and `parameters`.
    5.  It calls its own `handle_direct_request` method with the task details to generate the asset.
    6.  If the generation is successful, it attempts to update the `GameDevState` with the generated asset's information (e.g., ID, data/path) using a method like `update_asset_info` or `update_asset_path`.
    7.  If tasks were processed from a simple list in `state.data`, it clears that list.
    8.  Handles potential `AttributeError` if the `GameDevState` object does not have the expected methods for task processing or updating.
*   **Outputs:** The updated `GameDevState` object after processing any pending tasks.

## Toolchain Interaction

The `PixelForgeAgent` primarily interacts with the `RetroDiffusionToolchainBridge` ([`src/toolchains/retro_diffusion_bridge.py`](src/toolchains/retro_diffusion_bridge.py:0)).

*   An instance of `RetroDiffusionToolchainBridge` is created during the `PixelForgeAgent`'s initialization.
*   The agent passes its `mcp_server` instance to the bridge, as the bridge likely uses the server for managing worker queues or communication.
*   Configuration parameters like `t5_model_path` and `diffusion_model_path` can be passed to the bridge constructor via the agent's `toolchain_config`.
*   The agent's `handle_direct_request` method is the primary point where it calls the bridge's `generate_asset` method to initiate the image generation process.
*   The agent relies on the bridge to handle the specifics of interacting with the underlying diffusion model and returning the generated asset data.

## Configuration

The `PixelForgeAgent` can be configured during initialization via the `toolchain_config` dictionary and the `prompt_template` list.

*   `agent_id` (str): A unique identifier for the agent instance.
*   `mcp_server` (Any): An instance of the MCP Server the agent is connected to.
*   `role` (str, optional): The role of the agent (defaults to "PixelForgeAgent").
*   `prompt_template` (List[str], optional): A list of strings defining the agent's initial system prompt for guiding its behavior (defaults to `DEFAULT_PROMPT_TEMPLATE`).
*   `toolchain_config` (Dict[str, Any], optional): Configuration specific to the toolchain bridge. This dictionary can include keys like `t5_model_path` and `diffusion_model_path` which are passed to the `RetroDiffusionToolchainBridge` constructor.

## Example Usage

The `pixel_forge.py` file includes an `if __name__ == '__main__':` block demonstrating basic usage of the `PixelForgeAgent`. This example shows how to:

1.  Set up basic logging.
2.  Create a mock `MockMCPServer` instance, as required by the agent and toolchain bridge.
3.  Instantiate the `PixelForgeAgent`, passing the mock server and an optional `toolchain_config`.
4.  Test the `handle_direct_request` method with a sample payload, including a prompt and parameters like resolution and tileability.
5.  Test the `execute` method using a `TestGameDevState` mock class. This mock demonstrates how a `GameDevState` might indicate a need for a new sprite and provide its requirements, which the agent would then process.
6.  Shuts down the toolchain bridge's internal executor.

This example provides a runnable demonstration of the agent's core functionalities and its interaction with the toolchain bridge and a mock game state.