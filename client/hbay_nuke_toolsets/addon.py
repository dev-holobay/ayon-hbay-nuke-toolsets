"""AYON addon implementation for HBAY Nuke Toolsets."""

import os

from ayon_core.addon import AYONAddon, IHostAddon
from .version import __version__

NUKE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class HbayNukeToolsetsAddon(AYONAddon, IHostAddon):
    """HBAY Nuke Toolsets client addon.

    Provides shared toolsets functionality for Nuke,
    bootstrapped via Nuke's startup system.
    """

    name = "hbay_nuke_toolsets"
    version = __version__
    host_name = "nuke"

    def add_implementation_envs(self, env, _app):
        # Add requirements to NUKE_PATH
        new_nuke_paths = [
            os.path.join(NUKE_ROOT_DIR, "startup")
        ]
        old_nuke_path = env.get("NUKE_PATH") or ""
        for path in old_nuke_path.split(os.pathsep):
            if not path:
                continue

            norm_path = os.path.normpath(path)
            if norm_path not in new_nuke_paths:
                new_nuke_paths.append(norm_path)

        env["NUKE_PATH"] = os.pathsep.join(new_nuke_paths)

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
        # We use Nuke's native plugin path system via startup/init.py and menu.py
        # rather than AYON launch hooks
        return []

    def get_workfile_extensions(self):
        """Get workfile extensions this addon works with.

        Returns:
            list: List of file extensions
        """
        return [".nk"]


def get_addon():
    """Get addon instance (for compatibility).

    Returns:
        HbayNukeToolsetsAddon: The addon instance
    """
    from ayon_core.addon import AddonsManager

    manager = AddonsManager()
    return manager.get_enabled_addon("hbay_nuke_toolsets")
