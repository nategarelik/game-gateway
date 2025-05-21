# src/systems/style_enforcement_system.py
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# --- Conceptual Data Structures ---

class StyleGuide:
    """
    Represents a comprehensive style guide for a project or a specific asset type.
    This is a conceptual class; its attributes would be defined by the project's needs.
    """
    def __init__(self, guide_id: str, name: str, rules: Dict[str, Any]):
        self.guide_id = guide_id
        self.name = name
        self.rules = rules # e.g., {"palette": ["#FF0000", ...], "texture_resolution": "1024x1024", "animation_style": "cel_shaded"}

    def get_rule(self, rule_name: str, default: Any = None) -> Any:
        return self.rules.get(rule_name, default)

class AssetMetadata:
    """
    Represents metadata associated with an asset being checked.
    This would typically include information about the asset's colors,
    resolution, animation properties, etc.
    """
    def __init__(self, asset_id: str, asset_type: str, properties: Dict[str, Any]):
        self.asset_id = asset_id
        self.asset_type = asset_type # e.g., "texture", "model", "sprite_animation"
        self.properties = properties # e.g., {"colors": ["#FE0000", ...], "frame_count": 16}

# --- Core System Components (Conceptual Implementations) ---

class PaletteValidator:
    """
    Validates if an asset's colors adhere to a specified palette.
    This is a conceptual "middleware" callable during asset generation or validation.
    """
    def __init__(self, allowed_palette: List[str], tolerance: float = 0.05):
        """
        Args:
            allowed_palette: A list of hex color strings (e.g., ["#RRGGBB", ...]).
            tolerance: A conceptual tolerance for color matching (0.0 to 1.0).
                       Not used in this placeholder.
        """
        self.allowed_palette_set = set(color.upper() for color in allowed_palette)
        self.tolerance = tolerance
        logger.info(f"PaletteValidator initialized with {len(self.allowed_palette_set)} colors.")

    def validate_colors(self, asset_colors: List[str]) -> Tuple[bool, List[str]]:
        """
        Checks if the provided asset colors are within the allowed palette.

        Args:
            asset_colors: A list of hex color strings extracted from the asset.

        Returns:
            A tuple: (is_valid: bool, offending_colors: List[str])
                     is_valid is True if all colors are in the palette.
                     offending_colors lists colors not found in the palette.
        """
        if not self.allowed_palette_set: # If no palette is defined, consider it valid
            return True, []
            
        offending_colors = []
        for color in asset_colors:
            # Simple exact match for placeholder. Real implementation would involve
            # color distance calculation and tolerance.
            if color.upper() not in self.allowed_palette_set:
                offending_colors.append(color)
        
        is_valid = not bool(offending_colors)
        if not is_valid:
            logger.warning(f"Palette validation failed. Offending colors: {offending_colors}")
        return is_valid, offending_colors

class ProceduralAnimationRulesEngine:
    """
    A conceptual rules engine for procedural animation.
    This would define and apply rules for animation styles, timing, physics, etc.
    """
    def __init__(self, ruleset: Dict[str, Any]):
        """
        Args:
            ruleset: A dictionary defining animation rules.
                     e.g., {"max_frame_duration_ms": 100, "easing_function_preference": "ease-in-out"}
        """
        self.ruleset = ruleset
        logger.info(f"ProceduralAnimationRulesEngine initialized with rules: {ruleset}")

    def check_animation_properties(self, animation_properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Checks if given animation properties conform to the defined rules.
        Placeholder implementation.

        Args:
            animation_properties: Dict of properties like {"frame_count": 24, "avg_duration_ms": 50}

        Returns:
            Tuple (is_compliant: bool, issues: List[str])
        """
        issues = []
        # Example rule check (conceptual)
        max_duration = self.ruleset.get("max_frame_duration_ms")
        if max_duration and animation_properties.get("avg_duration_ms", 0) > max_duration:
            issues.append(f"Average frame duration {animation_properties.get('avg_duration_ms')}ms exceeds max {max_duration}ms.")
        
        # Add more rule checks here based on self.ruleset
        
        is_compliant = not bool(issues)
        if not is_compliant:
            logger.warning(f"Animation rule check failed. Issues: {issues}")
        return is_compliant, issues

class StyleConsistencyChecker:
    """
    Performs broader style consistency checks across different asset properties
    or against a general style guide.
    """
    def __init__(self, style_guide: StyleGuide):
        self.style_guide = style_guide
        logger.info(f"StyleConsistencyChecker initialized with guide: {style_guide.name}")

    def check_asset_consistency(self, asset_metadata: AssetMetadata) -> Tuple[bool, List[str]]:
        """
        Checks if the asset's metadata is consistent with the overall style guide.
        Placeholder implementation.

        Args:
            asset_metadata: An AssetMetadata object.

        Returns:
            Tuple (is_consistent: bool, inconsistencies: List[str])
        """
        inconsistencies = []
        
        # Example: Check texture resolution if defined in the guide for textures
        if asset_metadata.asset_type == "texture":
            expected_resolution = self.style_guide.get_rule("texture_resolution")
            actual_resolution = asset_metadata.properties.get("resolution")
            if expected_resolution and actual_resolution and actual_resolution != expected_resolution:
                inconsistencies.append(f"Texture resolution {actual_resolution} does not match guide {expected_resolution}.")

        # Example: Check naming conventions (very conceptual)
        expected_prefix = self.style_guide.get_rule(f"{asset_metadata.asset_type}_name_prefix")
        if expected_prefix and not asset_metadata.asset_id.startswith(expected_prefix):
            inconsistencies.append(f"Asset ID '{asset_metadata.asset_id}' does not follow naming prefix '{expected_prefix}'.")

        # Add more consistency checks here...

        is_consistent = not bool(inconsistencies)
        if not is_consistent:
            logger.warning(f"Style consistency check failed for asset {asset_metadata.asset_id}. Issues: {inconsistencies}")
        return is_consistent, inconsistencies


class StyleEnforcementSystem:
    """
    Main facade for the Style Enforcement System.
    It integrates various components like palette validators and consistency checkers.
    This system would typically be invoked by asset generation agents (e.g., PixelForgeAgent).
    """
    def __init__(self, global_style_guide: StyleGuide):
        self.global_style_guide = global_style_guide
        # Initialize components based on the global guide or specific configurations
        self.palette_validator = PaletteValidator(global_style_guide.get_rule("palette", []))
        self.animation_rules_engine = ProceduralAnimationRulesEngine(global_style_guide.get_rule("animation_rules", {}))
        self.consistency_checker = StyleConsistencyChecker(global_style_guide)
        logger.info("StyleEnforcementSystem initialized.")

    def validate_asset_style(self, asset_metadata: AssetMetadata, asset_colors: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Performs a comprehensive style validation for a given asset.

        Args:
            asset_metadata: Metadata of the asset to validate.
            asset_colors: Optional list of hex colors from the asset, for palette validation.

        Returns:
            A dictionary summarizing the validation results.
            e.g., {
                "overall_valid": True,
                "palette_check": {"valid": True, "offending_colors": []},
                "animation_check": {"compliant": True, "issues": []},
                "consistency_check": {"consistent": True, "inconsistencies": []}
            }
        """
        results = {}
        overall_valid = True

        # 1. Palette Validation (if colors are provided)
        if asset_colors is not None:
            pal_valid, pal_offending = self.palette_validator.validate_colors(asset_colors)
            results["palette_check"] = {"valid": pal_valid, "offending_colors": pal_offending}
            if not pal_valid: overall_valid = False
        else:
            results["palette_check"] = {"valid": True, "message": "No colors provided for validation."}


        # 2. Animation Rules Check (if applicable asset type and properties)
        if asset_metadata.asset_type in ["sprite_animation", "model_animation"]: # Example types
            anim_props = asset_metadata.properties.get("animation_details", {})
            if anim_props:
                anim_compliant, anim_issues = self.animation_rules_engine.check_animation_properties(anim_props)
                results["animation_check"] = {"compliant": anim_compliant, "issues": anim_issues}
                if not anim_compliant: overall_valid = False
            else:
                results["animation_check"] = {"compliant": True, "message": "No animation details provided."}
        
        # 3. General Style Consistency Check
        const_consistent, const_inconsistencies = self.consistency_checker.check_asset_consistency(asset_metadata)
        results["consistency_check"] = {"consistent": const_consistent, "inconsistencies": const_inconsistencies}
        if not const_consistent: overall_valid = False

        results["overall_valid"] = overall_valid
        logger.info(f"Style validation for asset {asset_metadata.asset_id}: Overall valid = {overall_valid}. Results: {results}")
        return results

# --- Example Usage ---
if __name__ == "__main__":
    # Configure basic logging for the example
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. Define a Style Guide
    game_style_guide_rules = {
        "palette": ["#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF"],
        "texture_resolution": "512x512",
        "animation_rules": {"max_frame_duration_ms": 120, "min_frame_count": 5},
        "texture_name_prefix": "TX_",
        "model_name_prefix": "MDL_"
    }
    main_guide = StyleGuide(guide_id="sg_main_fantasy", name="Main Fantasy Style", rules=game_style_guide_rules)

    # 2. Initialize the Style Enforcement System
    style_system = StyleEnforcementSystem(global_style_guide=main_guide)

    # 3. Example Asset 1: A texture that mostly conforms
    asset1_meta = AssetMetadata(
        asset_id="TX_Rock_Diffuse", 
        asset_type="texture",
        properties={"resolution": "512x512"}
    )
    asset1_colors = ["#FFFFFF", "#000000", "#FA0000"] # Slight variation, but current validator is exact
    
    print(f"\n--- Validating Asset 1: {asset1_meta.asset_id} ---")
    validation_results1 = style_system.validate_asset_style(asset_metadata=asset1_meta, asset_colors=asset1_colors)
    print(f"Validation Results for {asset1_meta.asset_id}: {validation_results1}")

    # 4. Example Asset 2: An animation with some issues
    asset2_meta = AssetMetadata(
        asset_id="Player_Jump_Anim", # Missing MDL_ prefix for a model animation (conceptual)
        asset_type="model_animation",
        properties={
            "animation_details": {"frame_count": 20, "avg_duration_ms": 150}, # Duration too long
            "resolution": "N/A" # Not a texture
        }
    )
    # No specific colors to check for an animation itself, perhaps for its icon/preview
    print(f"\n--- Validating Asset 2: {asset2_meta.asset_id} ---")
    validation_results2 = style_system.validate_asset_style(asset_metadata=asset2_meta)
    print(f"Validation Results for {asset2_meta.asset_id}: {validation_results2}")

    # 5. Example Asset 3: A texture with incorrect resolution and bad colors
    asset3_meta = AssetMetadata(
        asset_id="TX_Wood_Planks",
        asset_type="texture",
        properties={"resolution": "1024x1024"} # Non-conforming resolution
    )
    asset3_colors = ["#FFFFFF", "#123456", "#ABCDEF"] # Colors not in palette
    print(f"\n--- Validating Asset 3: {asset3_meta.asset_id} ---")
    validation_results3 = style_system.validate_asset_style(asset_metadata=asset3_meta, asset_colors=asset3_colors)
    print(f"Validation Results for {asset3_meta.asset_id}: {validation_results3}")