"""
Toolchain Bridges Package
-------------------------

This package provides standardized bridge interfaces to various external toolchains
used by the AI agents.

Available Bridges:
- MuseToolchainBridge: For interacting with a Unity Muse-like environment.
- RetroDiffusionToolchainBridge: For interacting with a Retro Diffusion-like image generation pipeline.
- BaseToolchainBridge: An abstract base class for creating new toolchain bridges.
"""

from .base_toolchain_bridge import BaseToolchainBridge
from .muse_bridge import MuseBridge
from .retro_diffusion_bridge import RetroDiffusionBridge

__all__ = [
    "BaseToolchainBridge",
    "MuseToolchainBridge",
    "format_muse_command",
    "RetroDiffusionToolchainBridge",
    "validate_retro_diffusion_parameters"
]

# Optional: Configure a package-level logger if desired,
# though individual modules currently set up their own.
# import logging
# logging.getLogger(__name__).addHandler(logging.NullHandler())