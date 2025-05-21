import uuid
import json
import re
from datetime import datetime
from concurrent.futures import Future # Used by provider, though not explicitly in AssetRequest

# Placeholder for GameDevState and Agent if these classes are not globally available
# For the context of these classes, they primarily interact with MCPServer
# and asset data, not directly with the full agent execution cycle.

class AssetRequest:
    def __init__(self, requester_id: str, asset_spec: str, constraints: dict = None):
        self.id = str(uuid.uuid4())
        self.requester_id = requester_id
        self.asset_spec = asset_spec # Textual description of the asset needed
        self.constraints = constraints or {} # e.g., {"palette": "NES", "tileable": True}
        self.timestamp = datetime.now().isoformat()
        self.status = "pending" # pending, bidding, fulfilled, failed
        self.bids = [] # List of AssetBid objects
        self.selected_bid = None
        # generation_parameters are extracted for direct use by RetroDiffusion, etc.
        self.generation_parameters = self._extract_generation_parameters()
        print(f"AssetRequest created: {self.id} by {self.requester_id} for '{self.asset_spec}'")

    def _extract_generation_parameters(self) -> dict:
        """Extract generation parameters from the asset spec and constraints."""
        parameters = {}
        
        # Extract resolution (e.g., "64x64 sprite of a hero")
        resolution_match = re.search(r'(\d+)x(\d+)', self.asset_spec + " " + self.constraints.get("resolution_str",""))
        if "resolution" in self.constraints and isinstance(self.constraints["resolution"], list):
            parameters["resolution"] = self.constraints["resolution"]
        elif resolution_match:
            try:
                parameters["resolution"] = [int(resolution_match.group(1)), int(resolution_match.group(2))]
            except ValueError: pass # Ignore if conversion fails
            
        # Extract palette information
        if "palette" in self.constraints:
            parameters["palette"] = self.constraints["palette"] # Could be a name or list of hex
            parameters["palette_lock"] = self.constraints.get("palette_lock", True)
            
        # Extract tileable information
        if "tileable" in self.constraints:
            parameters["tileable"] = bool(self.constraints["tileable"])
            
        # Extract animation information (e.g., "animated hero, 16 frames")
        animation_match = re.search(r'(\d+)\s*frames?', self.asset_spec, re.IGNORECASE)
        if "animation_frames" in self.constraints:
            parameters["animation_frames"] = int(self.constraints["animation_frames"])
        elif animation_match:
            try:
                parameters["animation_frames"] = int(animation_match.group(1))
            except ValueError: pass
        
        # Add other spec/constraint parsing as needed
        print(f"AssetRequest {self.id}: Extracted generation_parameters: {parameters}")
        return parameters

    def add_bid(self, bid): # bid is an AssetBid object
        self.bids.append(bid)
        self.status = "bidding"

    def select_bid(self, bid_id):
        for bid in self.bids:
            if bid.id == bid_id:
                self.selected_bid = bid
                self.status = "bid_selected"
                return True
        return False

class AssetBid:
    def __init__(self, provider_id: str, request_id: str, cost: float = 0.0, time_estimate: float = 0.0, match_info: dict = None):
        self.id = str(uuid.uuid4())
        self.provider_id = provider_id
        self.request_id = request_id
        self.cost = cost # e.g., in some virtual currency or computational unit
        self.time_estimate = time_estimate # e.g., in seconds
        self.match_info = match_info # For library providers: {"asset_id": "...", "variance": 0.1}
        self.timestamp = datetime.now().isoformat()
        print(f"AssetBid created: {self.id} by {self.provider_id} for request {self.request_id}")


class PixelForgeProvider:
    def __init__(self, mcp_server): # mcp_server should have generate_retro_asset
        self.mcp_server = mcp_server
        self.id = "PixelForgeProvider_" + str(uuid.uuid4())[:8]
        print(f"PixelForgeProvider initialized: {self.id}")

    def can_fulfill(self, request: AssetRequest) -> bool:
        """Check if this provider can fulfill the request (typically yes for generation)."""
        # PixelForge generates, so it can attempt most pixel art requests.
        # Could add more sophisticated checks based on asset_spec keywords.
        return "pixel" in request.asset_spec.lower() or \
               "sprite" in request.asset_spec.lower() or \
               "retro" in request.asset_spec.lower()

    def estimate_cost(self, request: AssetRequest) -> float:
        """Estimate the cost of fulfilling the request."""
        params = request.generation_parameters
        resolution = params.get("resolution", [64, 64])
        animation_frames = params.get("animation_frames", 1)
        
        base_cost = 0.001  # Base cost (e.g., virtual currency)
        try:
            resolution_factor = (int(resolution[0]) * int(resolution[1])) / (64 * 64)
        except (TypeError, ValueError):
            resolution_factor = 1.0
        animation_factor = int(animation_frames)
        
        total_cost = base_cost * resolution_factor * animation_factor
        return max(total_cost, 0.0001) # Minimum cost

    def _estimate_time(self, request: AssetRequest) -> float:
        """Estimate the time to fulfill the request."""
        params = request.generation_parameters
        resolution = params.get("resolution", [64, 64])
        animation_frames = params.get("animation_frames", 1)
        
        base_time = 5  # Base time in seconds for a simple asset
        try:
            resolution_factor = (int(resolution[0]) * int(resolution[1])) / (64 * 64)
        except (TypeError, ValueError):
            resolution_factor = 1.0
        animation_factor = int(animation_frames)
        
        total_time = base_time * resolution_factor * animation_factor
        return max(total_time, 1.0) # Minimum time

    def submit_bid(self, request: AssetRequest) -> AssetBid | None:
        """Submit a bid for the request."""
        if not self.can_fulfill(request):
            return None
            
        cost = self.estimate_cost(request)
        time_estimate = self._estimate_time(request)
        
        bid = AssetBid(
            provider_id=self.id,
            request_id=request.id,
            cost=cost,
            time_estimate=time_estimate
        )
        return bid
        
    def fulfill_request(self, request: AssetRequest) -> dict:
        """Fulfill the request by generating the asset. Returns a dict with asset details."""
        print(f"{self.id}: Fulfilling request {request.id} for '{request.asset_spec}'")
        if not self.mcp_server or not hasattr(self.mcp_server, 'generate_retro_asset'):
            raise ConnectionError("MCPServer or generate_retro_asset method not available to PixelForgeProvider.")

        # The asset_spec is the textual prompt for generation.
        # request.generation_parameters contains structured data like resolution.
        future = self.mcp_server.generate_retro_asset(
            prompt=request.asset_spec, 
            parameters=request.generation_parameters,
            agent_id=self.id # Provider acts as the agent requesting generation here
        )
        
        # Wait for the result (blocking for this example)
        # result is an image data object (e.g., MockImageData)
        generated_asset_object = future.result(timeout=120) # Longer timeout for generation
        
        asset_id = str(uuid.uuid4())
        asset_data_b64 = generated_asset_object.to_base64() if hasattr(generated_asset_object, 'to_base64') else None
        
        print(f"{self.id}: Asset {asset_id} generated for request {request.id}.")
        return {
            "asset_id": asset_id,
            "asset_data_b64": asset_data_b64,
            "metadata": {
                "source_request_id": request.id,
                "original_prompt": request.asset_spec,
                "generation_parameters": request.generation_parameters,
                "provider_id": self.id,
                "timestamp": datetime.now().isoformat()
            }
        }

# Placeholder for ColorDifferenceCalculator
class ColorDifferenceCalculator:
    def calculate_palette_variance(self, palette1_str_or_list, palette2_str_or_list):
        print(f"ColorDifferenceCalculator: Calculating variance (placeholder) between {palette1_str_or_list} and {palette2_str_or_list}")
        return 5.0 # Mock variance

class AssetLibraryProvider:
    def __init__(self, mcp_server): # mcp_server might not be strictly needed if it only serves from its own index
        self.mcp_server = mcp_server
        self.id = "AssetLibraryProvider_" + str(uuid.uuid4())[:8]
        self.asset_index = {}  # This would be populated: e.g., {"asset_guid": {"data": "...", "tags": [], "palette": []}}
        self.color_calculator = ColorDifferenceCalculator()
        print(f"AssetLibraryProvider initialized: {self.id}")

    def load_asset_to_index(self, asset_id, data, tags, palette_info, prompt_info):
        self.asset_index[asset_id] = {
            "id": asset_id,
            "data_b64": data, # Assuming b64 encoded data
            "tags": tags, # list of strings
            "palette": palette_info, # e.g. list of hex strings
            "prompt": prompt_info, # original prompt if known
            "timestamp": datetime.now().isoformat()
        }
        print(f"AssetLibraryProvider: Loaded asset {asset_id} to index.")

    def _find_matching_asset(self, request: AssetRequest) -> dict | None:
        """Find a matching asset in the library. Placeholder."""
        print(f"{self.id}: Searching for asset matching spec '{request.asset_spec}' (placeholder search)")
        # Simple keyword match for placeholder
        for asset_id, asset_details in self.asset_index.items():
            # Check if any part of asset_spec is in asset_details tags or prompt
            if any(keyword in asset_details.get("prompt","").lower() for keyword in request.asset_spec.lower().split()) or \
               any(keyword in " ".join(asset_details.get("tags",[])).lower() for keyword in request.asset_spec.lower().split()):
                
                # Further check constraints if any (e.g. resolution, tileable)
                # This is a very basic placeholder. Real matching would be more complex.
                # For example, check request.generation_parameters against asset metadata.
                print(f"{self.id}: Potential match found: {asset_id} for request {request.id}")
                return asset_details
        return None
        
    def _calculate_variance(self, request: AssetRequest, asset_details: dict) -> float:
        """Calculate the variance between the request and the asset. Placeholder."""
        variance = 10.0 # Default high variance
        if "palette" in request.constraints and "palette" in asset_details:
            variance = self.color_calculator.calculate_palette_variance(
                request.constraints["palette"],
                asset_details["palette"]
            )
        # Add other variance calculations (e.g., resolution, animation frames)
        print(f"{self.id}: Calculated variance for asset {asset_details['id']} against request {request.id}: {variance}%")
        return variance
        
    def can_fulfill(self, request: AssetRequest) -> bool:
        """Check if this provider can fulfill the request from its library."""
        return self._find_matching_asset(request) is not None

    def submit_bid(self, request: AssetRequest) -> AssetBid | None:
        """Submit a bid for the request if a matching asset is found."""
        matching_asset = self._find_matching_asset(request)
        if not matching_asset:
            return None
            
        variance = self._calculate_variance(request, matching_asset)
        
        # Library assets are typically cheaper and faster
        bid = AssetBid(
            provider_id=self.id,
            request_id=request.id,
            cost=0.0001, # Very low cost for existing asset
            time_estimate=0.1, # Very fast retrieval
            match_info={"asset_id": matching_asset["id"], "variance_percent": variance}
        )
        return bid
        
    def fulfill_request(self, request: AssetRequest) -> dict:
        """Fulfill the request by providing the matching asset from the library."""
        matching_asset = self._find_matching_asset(request)
        if not matching_asset:
            print(f"{self.id}: Error fulfilling request {request.id} - no matching asset found (should have been caught by can_fulfill or bid).")
            raise ValueError(f"No matching asset found for request {request.id} by {self.id}")
            
        print(f"{self.id}: Fulfilling request {request.id} with library asset {matching_asset['id']}.")
        return {
            "asset_id": matching_asset["id"],
            "asset_data_b64": matching_asset["data_b64"],
            "metadata": {
                "source_request_id": request.id,
                "original_prompt": matching_asset.get("prompt", "N/A"),
                "tags": matching_asset.get("tags", []),
                "variance_percent": self._calculate_variance(request, matching_asset),
                "provider_id": self.id,
                "timestamp": datetime.now().isoformat(),
                "library_retrieval_timestamp": matching_asset.get("timestamp")
            }
        }

if __name__ == '__main__':
    print("--- Testing Negotiation Protocol Extensions ---")

    # Mock MCPServer for PixelForgeProvider
    class MockMCPServer:
        def generate_retro_asset(self, prompt, parameters=None, agent_id=None):
            print(f"MockMCPServer (for Negotiation): generate_retro_asset called by {agent_id} for '{prompt}' with {parameters}")
            future = Future()
            class MockAssetData:
                def __init__(self, p, pa): self.p=p; self.pa=pa; self.id=str(uuid.uuid4())
                def to_base64(self): return f"b64_mock_data_for_{self.id}"
            future.set_result(MockAssetData(prompt, parameters))
            return future

    mock_mcp = MockMCPServer()
    
    # --- Test AssetRequest ---
    req1_constraints = {"resolution": [32,32], "palette": "PICO-8", "tileable": True, "animation_frames": 8}
    req1 = AssetRequest("Agent007", "animated 32x32 pixel art slime, PICO-8 palette, tileable", req1_constraints)
    print(f"Request 1 ID: {req1.id}, Gen Params: {req1.generation_parameters}")
    assert req1.generation_parameters.get("resolution") == [32,32]
    assert req1.generation_parameters.get("animation_frames") == 8

    # --- Test PixelForgeProvider ---
    pf_provider = PixelForgeProvider(mcp_server=mock_mcp)
    if pf_provider.can_fulfill(req1):
        pf_bid = pf_provider.submit_bid(req1)
        print(f"PixelForgeProvider Bid: Cost={pf_bid.cost}, Time={pf_bid.time_estimate}")
        req1.add_bid(pf_bid)
        # Simulate bid selection
        req1.select_bid(pf_bid.id)
        if req1.selected_bid:
            fulfillment_data = pf_provider.fulfill_request(req1)
            print(f"PixelForgeProvider Fulfillment: asset_id={fulfillment_data['asset_id']}, data_len={len(fulfillment_data['asset_data_b64'])}")
            assert fulfillment_data['asset_data_b64'] is not None

    # --- Test AssetLibraryProvider ---
    lib_provider = AssetLibraryProvider(mcp_server=None) # MCP not strictly needed for basic lib ops
    lib_provider.load_asset_to_index(
        asset_id="lib_slime_001", 
        data="b64_existing_slime_data", 
        tags=["slime", "pixel art", "animated", "green"], 
        palette_info=["#00FF00", "#00AA00"],
        prompt_info="a green animated pixel slime"
    )
    
    req2_spec = "green pixel slime" # More generic request
    req2 = AssetRequest("Agent008", req2_spec, {"palette": ["#00FF00"]})

    if lib_provider.can_fulfill(req2):
        lib_bid = lib_provider.submit_bid(req2)
        print(f"AssetLibraryProvider Bid: MatchInfo={lib_bid.match_info}")
        req2.add_bid(lib_bid)
        req2.select_bid(lib_bid.id)
        if req2.selected_bid:
            lib_fulfillment = lib_provider.fulfill_request(req2)
            print(f"AssetLibraryProvider Fulfillment: asset_id={lib_fulfillment['asset_id']}, data={lib_fulfillment['asset_data_b64']}")
            assert lib_fulfillment['asset_id'] == "lib_slime_001"
    
    print("--- Negotiation Protocol Extensions Test Finished ---")