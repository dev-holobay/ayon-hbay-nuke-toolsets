"""Nuke menu setup for HBAY Shared Toolsets.

This file is loaded second by Nuke's startup process.
Sets up the shared toolsets menu and functionality.
"""
import os
import logging
from pathlib import Path

import nuke

from hbay_nuke_toolsets.api import (
    setup_toolsets_menu
)

log = logging.getLogger("ayon.hbay_nuke_toolsets")

icon_path = Path(os.path.dirname(os.path.abspath(__file__))) / "shared_toolset.png"

def main():
    """Initialize shared toolsets menu in Nuke."""
    try:
        log.info("Holobay Nuke Toolsets: Setting up menu")
        toolbar = nuke.menu("Nodes")
        setup_toolsets_menu(toolbar, icon_path=str(icon_path))
        log.info("Holobay Nuke Toolsets: Menu setup complete")
    except Exception as e:
        log.error(f"Failed to setup HBAY Nuke Toolsets menu: {e}",
                  exc_info=True)


# Run menu setup
main()
