import uuid
import json
from queue import Queue
from concurrent.futures import Future
from threading import Thread
from datetime import datetime
import re # For AssetRequest parameter extraction, though AssetRequest is in a different section

# Placeholder for actual image data representation / manipulation
# For example, using Pillow (PIL) or a custom class
class MockImageData:
    def __init__(self, prompt, params, data="mock_pixel_data"):
        self.prompt = prompt
        self.params = params
        self.data = data
        self.id = str(uuid.uuid4())

    def to_base64(self):
        # In a real scenario, this would convert image data to base64 string
        return f"base64_encoded_image_for_{self.id}"

    def __str__(self):
        return f"MockImageData(id={self.id}, prompt='{self.prompt}')"

class T5TextEncoder:
    def __init__(self, model_path=None):
        # Initialize the T5 model
        self.model = self._load_model(model_path)
        print(f"T5TextEncoder initialized (model path: {model_path if model_path else 'default'})")

    def _load_model(self, model_path):
        """Load the T5 model from the specified path or use a default."""
        # Placeholder: Implementation would load a pre-trained T5 model
        print(f"T5TextEncoder: Loading T5 model (placeholder)... Path: {model_path}")
        return "mock_t5_model"
        
    def encode(self, prompt):
        """Encode a prompt using the T5 model."""
        # Placeholder: Implementation would use the T5 model to encode the prompt
        print(f"T5TextEncoder: Encoding prompt (placeholder): '{prompt}'")
        return f"encoded_{prompt}"

class RetroDiffusionModel:
    def __init__(self, model_path=None):
        # Initialize the diffusion model
        self.model = self._load_model(model_path)
        print(f"RetroDiffusionModel initialized (model path: {model_path if model_path else 'default'})")
        
    def _load_model(self, model_path):
        """Load the diffusion model from the specified path or use a default."""
        # Placeholder: Implementation would load a pre-trained diffusion model
        print(f"RetroDiffusionModel: Loading diffusion model (placeholder)... Path: {model_path}")
        return "mock_diffusion_model"
        
    def generate(self, encoded_prompt, resolution=[64, 64], palette_lock=True, tileable=False, animation_frames=1):
        """Generate an image using the diffusion model."""
        # Placeholder: Implementation would use the diffusion model to generate an image
        print(f"RetroDiffusionModel: Generating image (placeholder) for '{encoded_prompt}' with params: res={resolution}, palette_lock={palette_lock}, tileable={tileable}, frames={animation_frames}")
        # Return a mock image data object
        return MockImageData(prompt=encoded_prompt, params={"resolution": resolution, "palette_lock": palette_lock, "tileable": tileable, "animation_frames": animation_frames})

class RetroPostProcessor:
    def __init__(self):
        print("RetroPostProcessor initialized")
        pass
        
    def process(self, image: MockImageData, edge_detection=True, alpha_optimization=True, generate_lod=False):
        """Apply post-processing to an image."""
        print(f"RetroPostProcessor: Processing image (placeholder): {image.id}")
        processed_image = image # Start with the original image
        
        if edge_detection:
            processed_image = self._apply_edge_detection(processed_image)
            
        if alpha_optimization:
            processed_image = self._optimize_alpha(processed_image)
            
        if generate_lod:
            processed_image = self._generate_lod(processed_image)
            
        print(f"RetroPostProcessor: Finished processing image {image.id}")
        return processed_image
        
    def _apply_edge_detection(self, image: MockImageData):
        """Apply pixel perfect edge detection."""
        print(f"RetroPostProcessor: Applying edge detection (placeholder) to {image.id}")
        # Modify image.data or create new MockImageData
        return image 
            
    def _optimize_alpha(self, image: MockImageData):
        """Optimize the alpha channel."""
        print(f"RetroPostProcessor: Optimizing alpha (placeholder) for {image.id}")
        return image
            
    def _generate_lod(self, image: MockImageData):
        """Generate LOD versions of the image."""
        print(f"RetroPostProcessor: Generating LOD (placeholder) for {image.id}")
        return image

class RetroDiffusionPipeline:
    def __init__(self):
        self.t5_encoder = T5TextEncoder()
        self.diffusion_model = RetroDiffusionModel()
        self.post_processor = RetroPostProcessor()
        print("RetroDiffusionPipeline initialized")
        
    def generate_asset(self, prompt, parameters=None):
        """Generate an asset using the Retro Diffusion Pipeline."""
        parameters = parameters or {}
        
        # Validate and apply default parameters
        validated_params = validate_retro_diffusion_parameters(parameters)
        print(f"RetroDiffusionPipeline: Generating asset for prompt '{prompt}' with validated_params: {validated_params}")
                
        # Step 1: Encode the prompt using T5
        encoded_prompt = self.t5_encoder.encode(prompt)
        
        # Step 2: Generate the base image using the diffusion model
        base_image = self.diffusion_model.generate(
            encoded_prompt,
            resolution=validated_params["resolution"],
            palette_lock=validated_params["palette_lock"],
            tileable=validated_params["tileable"],
            animation_frames=validated_params["animation_frames"]
        )
        
        # Step 3: Apply post-processing
        # The design doc passes more parameters to post_processor.process
        # than are in validated_params directly. We should extract them or ensure they are passed.
        processed_image = self.post_processor.process(
            base_image,
            edge_detection=parameters.get("edge_detection", True), # Get from original or default
            alpha_optimization=parameters.get("alpha_optimization", True), # Get from original or default
            generate_lod=parameters.get("generate_lod", False) # Get from original or default
        )
        
        print(f"RetroDiffusionPipeline: Asset generation complete for prompt '{prompt}'. Result: {processed_image.id}")
        return processed_image

class RetroDiffusionToolchainBridge:
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server # Instance of MCPServer
        self.pipeline = RetroDiffusionPipeline()
        self.generation_queue = Queue()
        self.result_cache = {} # Cache for generated assets
        print("RetroDiffusionToolchainBridge initialized")
        
    def generate_asset(self, prompt, parameters=None, agent_id=None):
        """Generate an asset using the Retro Diffusion Pipeline. Returns a Future."""
        generation_id = str(uuid.uuid4())
        future = Future()
        
        parameters = parameters or {}
        # Ensure parameters are validated before caching or processing
        validated_parameters = validate_retro_diffusion_parameters(parameters)

        # Create the generation request
        request_payload = {
            "id": generation_id,
            "prompt": prompt,
            "parameters": validated_parameters, # Use validated parameters for processing
            "original_parameters": parameters, # Keep original for other uses if needed
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check the cache first using validated parameters for consistency
        cache_key = self._generate_cache_key(prompt, validated_parameters)
        if cache_key in self.result_cache:
            print(f"RetroDiffusionToolchainBridge: Cache hit for '{prompt}' with params {validated_parameters}. Key: {cache_key}")
            future.set_result(self.result_cache[cache_key])
            return future
        
        print(f"RetroDiffusionToolchainBridge: Cache miss for '{prompt}'. Adding to generation queue. Key: {cache_key}")
        # Store the future for later resolution
        self.generation_queue.put((request_payload, future))
        
        # Trigger the generation processing
        self._process_generation_queue()
        
        return future
        
    def _process_generation_queue(self):
        """Process the generation queue in a separate thread."""
        def worker():
            while not self.generation_queue.empty():
                request_payload, future = self.generation_queue.get()
                try:
                    print(f"RetroDiffusionToolchainBridge: Processing generation request {request_payload['id']} for prompt '{request_payload['prompt']}'")
                    # Generate the asset using the pipeline
                    # Pass the validated parameters to the pipeline's generate_asset method
                    result_asset = self.pipeline.generate_asset(
                        request_payload["prompt"],
                        request_payload["parameters"] # These are already validated
                    )
                    
                    # Cache the result
                    # Use the same validated parameters for cache key generation
                    cache_key = self._generate_cache_key(
                        request_payload["prompt"],
                        request_payload["parameters"]
                    )
                    self.result_cache[cache_key] = result_asset
                    print(f"RetroDiffusionToolchainBridge: Asset {result_asset.id} generated and cached with key {cache_key}.")
                    
                    # Resolve the future
                    future.set_result(result_asset)
                    
                except Exception as e:
                    # Log error, e.g., self.mcp_server.logger.error(...)
                    print(f"RetroDiffusionToolchainBridge: Error processing generation request {request_payload.get('id')}: {e}")
                    future.set_exception(e)
                finally:
                    self.generation_queue.task_done()
        
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def _generate_cache_key(self, prompt, parameters):
        """Generate a cache key for a generation request. Uses validated parameters."""
        # Ensure parameters are consistently ordered for caching
        parameters_str = json.dumps(parameters or {}, sort_keys=True)
        return f"{prompt}:{parameters_str}"

def validate_retro_diffusion_parameters(parameters):
    """Validate parameters for the Retro Diffusion Pipeline."""
    validated = {}
    parameters = parameters or {} # Ensure parameters is a dict

    # Resolution
    resolution = parameters.get("resolution")
    if isinstance(resolution, list) and len(resolution) == 2 and \
       isinstance(resolution[0], int) and isinstance(resolution[1], int) and \
       resolution[0] > 0 and resolution[1] > 0: # Basic check for positive integers
        # Power of 2 check from design doc
        is_power_of_two = lambda n: (n > 0) and (n & (n - 1) == 0)
        if is_power_of_two(resolution[0]) and is_power_of_two(resolution[1]):
            validated["resolution"] = resolution
        else:
            print(f"Warning: Resolution {resolution} not power of 2. Defaulting to [64,64].")
            validated["resolution"] = [64, 64] 
    else:
        validated["resolution"] = [64, 64]  # Default
        
    # Palette lock
    validated["palette_lock"] = bool(parameters.get("palette_lock", True))
    
    # Tileable
    validated["tileable"] = bool(parameters.get("tileable", False))
    
    # Animation frames
    animation_frames = parameters.get("animation_frames", 1)
    if isinstance(animation_frames, int) and animation_frames > 0:
        validated["animation_frames"] = animation_frames
    else:
        validated["animation_frames"] = 1  # Default
            
    # Other parameters from RetroDiffusionPipeline.generate_asset that might need validation
    # or pass-through if not handled by this validator specifically.
    # For now, this validator focuses on the ones explicitly detailed.
    print(f"Validated Retro Diffusion Parameters: {validated}")
    return validated

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    class MockMCPServer:
        def __init__(self):
            self.logger = print # Basic logger

    mock_mcp = MockMCPServer()
    retro_bridge = RetroDiffusionToolchainBridge(mock_mcp)

    # Test parameter validation
    params1 = {"resolution": [32, 32], "animation_frames": 10}
    validated1 = validate_retro_diffusion_parameters(params1)
    print(f"Params1: {params1} -> Validated1: {validated1}")

    params2 = {"resolution": [30, 30], "tileable": "true"} # Invalid resolution, string for bool
    validated2 = validate_retro_diffusion_parameters(params2)
    print(f"Params2: {params2} -> Validated2: {validated2}")
    
    params3 = {}
    validated3 = validate_retro_diffusion_parameters(params3)
    print(f"Params3: {params3} -> Validated3: {validated3}")

    # Test asset generation
    try:
        prompt = "a heroic knight"
        parameters = {"resolution": [32, 32], "tileable": True}
        
        print(f"\nRequesting asset for: '{prompt}' with params: {parameters}")
        future_asset = retro_bridge.generate_asset(prompt, parameters, agent_id="PixelForgeAgent_01")
        print("Asset generation requested, waiting for result...")
        
        asset_result = future_asset.result(timeout=10) # Wait for the future
        print(f"Generated Asset: {asset_result}")
        print(f"Base64 data: {asset_result.to_base64()}")

        # Test cache
        print(f"\nRequesting same asset again for: '{prompt}' with params: {parameters}")
        future_asset_cached = retro_bridge.generate_asset(prompt, parameters, agent_id="PixelForgeAgent_01")
        asset_result_cached = future_asset_cached.result(timeout=1) # Should be fast from cache
        print(f"Generated Asset (cached): {asset_result_cached}")
        assert asset_result.id == asset_result_cached.id, "Cache did not return the same asset instance!"

        prompt2 = "a spooky ghost"
        parameters2 = {"resolution": [16,16], "animation_frames": 5}
        print(f"\nRequesting asset for: '{prompt2}' with params: {parameters2}")
        future_asset2 = retro_bridge.generate_asset(prompt2, parameters2, agent_id="PixelForgeAgent_02")
        asset_result2 = future_asset2.result(timeout=10)
        print(f"Generated Asset 2: {asset_result2}")


    except Exception as e:
        print(f"An error occurred during example usage: {e}")
        import traceback
        traceback.print_exc()

    # Ensure threads can exit
    import time
    time.sleep(0.1)
    print("\nExample usage finished.")