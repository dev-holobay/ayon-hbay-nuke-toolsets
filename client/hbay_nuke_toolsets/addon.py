"""AYON addon implementation for HBAY Nuke Toolsets."""

import os

from ayon_core.addon import AYONAddon
from .version import __version__

ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))


class HbayNukeToolsetsAddon(AYONAddon):
    """HBAY Nuke Toolsets client addon.

    Provides shared toolsets functionality for Nuke,
    bootstrapped via Nuke's startup system.
    """

    name = "hbay_nuke_toolsets"
    version = __version__

    def initialize(self, settings):
        """Initialize the addon.

        Args:
            settings (dict): Addon settings from AYON server
        """
        self.enabled = settings.get("enabled", True)

    def get_launch_hook_paths(self):
        """Get launch hook paths for this addon.

        Returns:
            list: Empty list - this addon uses Nuke's native startup system
        """
        return [os.path.join(ADDON_ROOT, "hooks")]
