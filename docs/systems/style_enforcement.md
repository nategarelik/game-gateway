# Style Enforcement System Documentation

The Style Enforcement System is a crucial component designed to maintain artistic and technical consistency across assets generated within the Autonomous AI Agent Ecosystem. It provides mechanisms to define style guides and validate assets against these guides.

The core Python module for this system is located at [`src/systems/style_enforcement_system.py`](../../src/systems/style_enforcement_system.py).

## Purpose

The primary goal of this system is to ensure that all generated game assets (textures, models, animations, etc.) adhere to predefined stylistic and technical specifications. This includes:
*   **Palette Adherence:** Ensuring colors used in assets belong to an approved palette.
*   **Animation Rules:** Checking if animations follow specific timing, easing, or complexity rules.
*   **General Consistency:** Validating assets against broader style guide rules, such as naming conventions, resolution standards, or thematic elements.

This system is intended to be used by asset-generating agents (like `PixelForgeAgent`) either during or after the asset creation process.

## Core Components and Concepts

### 1. `StyleGuide`
   *   A conceptual class representing a comprehensive style guide.
   *   Holds `guide_id`, `name`, and a dictionary of `rules` (e.g., `{"palette": ["#FF0000", ...], "texture_resolution": "1024x1024"}`).
   *   Provides a `get_rule(rule_name, default=None)` method.

### 2. `AssetMetadata`
   *   Represents metadata for an asset being checked (e.g., `asset_id`, `asset_type`, `properties` like `{"colors": [], "resolution": "512x512"}`).

### 3. `PaletteValidator`
   *   **Purpose:** Validates if an asset's colors conform to a specified palette.
   *   **Initialization:** Takes an `allowed_palette` (list of hex color strings) and a conceptual `tolerance`.
   *   **Method: `validate_colors(asset_colors: List[str]) -> Tuple[bool, List[str]]`**
        *   Checks if `asset_colors` are present in the `allowed_palette_set`.
        *   Current implementation uses exact matching (case-insensitive).
        *   Returns `(is_valid, offending_colors)`.

### 4. `ProceduralAnimationRulesEngine`
   *   **Purpose:** A conceptual engine to check animation properties against a defined ruleset.
   *   **Initialization:** Takes a `ruleset` dictionary (e.g., `{"max_frame_duration_ms": 100}`).
   *   **Method: `check_animation_properties(animation_properties: Dict[str, Any]) -> Tuple[bool, List[str]]`**
        *   Placeholder implementation that can check example rules like maximum frame duration.
        *   Returns `(is_compliant, issues_found)`.

### 5. `StyleConsistencyChecker`
   *   **Purpose:** Performs broader style consistency checks using a `StyleGuide`.
   *   **Initialization:** Takes a `StyleGuide` instance.
   *   **Method: `check_asset_consistency(asset_metadata: AssetMetadata) -> Tuple[bool, List[str]]`**
        *   Placeholder implementation that can check rules like `texture_resolution` or conceptual naming conventions based on `asset_type`.
        *   Returns `(is_consistent, inconsistencies_found)`.

### 6. `StyleEnforcementSystem` (Facade)
   *   **Purpose:** The main entry point for using the system. It integrates the various validation components.
   *   **Initialization:** Takes a `global_style_guide` (an instance of `StyleGuide`). It then initializes its internal `PaletteValidator`, `ProceduralAnimationRulesEngine`, and `StyleConsistencyChecker` based on this global guide.
   *   **Method: `validate_asset_style(asset_metadata: AssetMetadata, asset_colors: Optional[List[str]] = None) -> Dict[str, Any]`**
        *   Performs a comprehensive style validation.
        *   Invokes palette validation (if `asset_colors` are provided).
        *   Invokes animation rule checks (if `asset_metadata` indicates an animation type and provides details).
        *   Invokes general style consistency checks.
        *   Returns a dictionary summarizing all results, including an `overall_valid` boolean flag.
        *   Example return:
            ```json
            {
                "overall_valid": false,
                "palette_check": {"valid": false, "offending_colors": ["#123456"]},
                "animation_check": {"compliant": true, "message": "No animation details provided."},
                "consistency_check": {"consistent": true, "inconsistencies": []}
            }
            ```

## Interaction Flow

1.  A `StyleGuide` is defined for the project or specific context.
2.  The `StyleEnforcementSystem` is initialized with this `StyleGuide`.
3.  An asset generation agent (e.g., `PixelForgeAgent`) creates an asset.
4.  The agent prepares `AssetMetadata` for the generated asset and, if applicable, extracts its `asset_colors`.
5.  The agent calls `style_system.validate_asset_style(asset_metadata, asset_colors)`.
6.  The `StyleEnforcementSystem` uses its internal components to perform all relevant checks.
7.  The agent receives a dictionary of validation results and can act accordingly (e.g., flag the asset, request regeneration with corrected parameters, or approve the asset).

## Example Usage (from `if __name__ == '__main__':`)

The `style_enforcement_system.py` script includes a demonstration in its `if __name__ == '__main__':` block:

```python
# In src/systems/style_enforcement_system.py

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

# 3. Example Asset Validation
asset1_meta = AssetMetadata(
    asset_id="TX_Rock_Diffuse", 
    asset_type="texture",
    properties={"resolution": "512x512"}
)
asset1_colors = ["#FFFFFF", "#000000", "#FA0000"] # "#FA0000" will fail exact match
validation_results1 = style_system.validate_asset_style(asset_metadata=asset1_meta, asset_colors=asset1_colors)
# print(validation_results1) 
# Expected: overall_valid=False due to palette mismatch with current exact checker.
```
This example shows how to define a style guide, initialize the system, and validate different mock assets against it.

## Future Enhancements

*   **Advanced Color Validation:** Implement proper color distance metrics (e.g., Delta E) and tolerance levels for palette validation instead of exact hex matching.
*   **Image Analysis Integration:** Integrate with image processing libraries to automatically extract colors, resolutions, and other properties from actual asset files rather than relying solely on `AssetMetadata`.
*   **Detailed Rule Engine:** Develop a more sophisticated rules engine for animation and general consistency checks, potentially using a dedicated rules language or library.
*   **Dynamic Guide Loading:** Allow `StyleGuide` instances to be loaded from configuration files (e.g., JSON, YAML).
*   **MCP Integration:** Define how style guides are managed and distributed via the MCP, and how validation results are reported as events.
*   **Automated Feedback Loops:** Enable the system to provide specific feedback to agents to guide asset regeneration if validation fails.