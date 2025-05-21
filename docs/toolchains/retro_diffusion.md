# Retro Diffusion Bridge Documentation

The [`RetroDiffusionBridge`](../../src/toolchains/retro_diffusion_bridge.py) class provides an interface to a (conceptual or mocked) Retro Diffusion Pipeline. It is designed for generating 2D assets such as images, textures, and sprite sheets, primarily for use by agents like the `PixelForgeAgent`.

This bridge inherits from [`BaseToolchainBridge`](../../src/toolchains/base_toolchain_bridge.py), leveraging its asynchronous request queuing and processing mechanism. This ensures that interactions with the potentially time-consuming Retro Diffusion process do not block the calling agent or the main application.

## Purpose

The main objective of the `RetroDiffusionBridge` is to enable agents within the Autonomous AI Agent Ecosystem to request 2D asset generation from the Retro Diffusion toolchain. It abstracts the direct interaction details, offering a simplified Python API.

## Core Functionality

### Initialization (`__init__`)

```python
class RetroDiffusionBridge(BaseToolchainBridge):
    def __init__(self, mcp_server, model_path: str = None, output_dir: str = "generated_assets/retro_diffusion"):
        # ...
```

*   `mcp_server`: An instance of the Master Control Program server (or a mock), used for context.
*   `model_path` (optional): A conceptual path to the Retro Diffusion model. In the current mock implementation, this defaults to `"mock_retro_diffusion_model.pth"` and is not directly used for generation.
*   `output_dir` (optional): The directory where (mock) generated assets will be saved. Defaults to `"generated_assets/retro_diffusion"`. The bridge ensures this directory exists.

### Request Handling (`_handle_specific_request`)

This internal method is called by the `BaseToolchainBridge`'s worker thread to process requests from the queue.
For the `RetroDiffusionBridge`, it currently simulates the asset generation process:
1.  Logs the request details (agent ID, request ID, prompt).
2.  Simulates processing time, partly based on the length of the prompt.
3.  Generates a unique-ish filename for the mock asset based on the request type, a hash of the prompt, and the current timestamp. The file is saved in the configured `output_dir`.
4.  Creates an empty mock file at the generated `output_path` containing a string with the prompt.
5.  Based on the `request_type`, it constructs a JSON-like dictionary response.
6.  Supported `request_type` values:
    *   `GENERATE_IMAGE_ASSET`
    *   `GENERATE_TEXTURE_ASSET`
    *   `GENERATE_SPRITE_SHEET`
7.  If an unsupported `request_type` is received, it raises a `ValueError`.
8.  If mock file creation fails, it returns an error status in the response.

### Public Interface Methods

The `RetroDiffusionBridge` offers the following public methods for agents to submit asset generation requests. Each method returns a `concurrent.futures.Future` object, which will eventually hold the result (a dictionary detailing the mock asset) or an exception if processing failed.

*   **`generate_image(self, prompt: str, resolution: str = "512x512", agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "resolution": resolution}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "asset_type": "image",
            "prompt": "A pixel art knight character",
            "image_path": "generated_assets/retro_diffusion/generate_image_asset_abcdef12_1678886400.png",
            "resolution": "512x512",
            "format": "png"
        }
        ```

*   **`generate_texture(self, prompt: str, resolution: str = "1024x1024", tileable: bool = True, agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "resolution": resolution, "tileable": tileable}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "asset_type": "texture",
            "prompt": "Seamless grassy ground texture",
            "texture_path": "generated_assets/retro_diffusion/generate_texture_asset_12345678_1678886405.png",
            "resolution": "1024x1024",
            "tileable": true
        }
        ```

*   **`generate_sprite_sheet(self, prompt: str, sprite_size: str = "64x64", num_frames: int = 8, agent_id: str = None) -> Future`**
    *   Payload sent: `{"prompt": prompt, "sprite_size": sprite_size, "num_frames": num_frames}`
    *   Mocked Response Example:
        ```json
        {
            "request_id": "...",
            "status": "success_mock",
            "asset_type": "sprite_sheet",
            "prompt": "Explosion animation frames",
            "sheet_path": "generated_assets/retro_diffusion/generate_sprite_sheet_fedcba98_1678886410_spritesheet.png",
            "sprite_size": "64x64",
            "num_frames": 16
        }
        ```

## Interaction Flow

1.  An agent (e.g., `PixelForgeAgent`) requires a 2D asset.
2.  The agent calls the appropriate generation method on a `RetroDiffusionBridge` instance (e.g., `retro_bridge.generate_image(...)`).
3.  The `RetroDiffusionBridge` queues the request via `_submit_request` (from `BaseToolchainBridge`) and returns a `Future` to the agent.
4.  The bridge's worker thread processes the request.
5.  `_handle_specific_request` simulates generation, creates a mock asset file, and prepares a response dictionary.
6.  The response dictionary (or an exception) is set on the `Future`.
7.  The agent retrieves the result from the `Future` (e.g., via `future.result()` or `await future`).

## Example Usage (from `if __name__ == '__main__':`)

The script's `if __name__ == '__main__':` block provides a synchronous demonstration:

```python
# In src/toolchains/retro_diffusion_bridge.py

class MockMCPServer:
    def __init__(self):
        self.name = "MockMCPServerForRetro"

# ... (inside if __name__ == '__main__')
mock_mcp = MockMCPServer()
retro_bridge = RetroDiffusionBridge(mcp_server=mock_mcp)

logger.info("Submitting requests to RetroDiffusionBridge...")

future_img = retro_bridge.generate_image(prompt="A pixel art knight character", agent_id="PixelForge01")
# ... other requests ...

logger.info("Requests submitted. Waiting for results (blocking)...")

try:
    result_img = future_img.result(timeout=10) # .result() is blocking
    logger.info(f"Image Asset Result: {result_img}")
    assert os.path.exists(result_img["image_path"]) # Verifies mock file creation
except Exception as e:
    logger.error(f"Image Asset Failed: {e}")

# ... handling for other future results ...

retro_bridge.shutdown()
logger.info("RetroDiffusionBridge demo finished.")
```
This example shows how to submit requests and retrieve their results, including a basic check for the existence of the mock generated files.

## Future Enhancements

*   Integration with an actual Retro Diffusion pipeline or API.
*   Real image data generation instead of mock files.
*   More sophisticated parameter handling and validation if the real toolchain supports it.
*   Error handling specific to the Retro Diffusion toolchain.