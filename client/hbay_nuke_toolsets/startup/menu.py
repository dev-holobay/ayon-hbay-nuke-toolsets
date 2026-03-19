"""Nuke menu setup for HBAY Shared Toolsets.

This file is loaded second by Nuke's startup process.
Sets up the shared toolsets menu and functionality.
"""

import logging
import nuke

from hbay_nuke_toolsets.api import (
    setup_toolsets_menu,
    refresh_toolsets_menu
)

log = logging.getLogger("ayon.hbay_nuke_toolsets")


def main():
    """Initialize shared toolsets menu in Nuke."""
    try:
        log.info("Holobay Nuke Toolsets: Setting up menu")
        toolbar = nuke.menu("Nodes")
        setup_toolsets_menu(toolbar)
        log.info("Holobay Nuke Toolsets: Menu setup complete")
    except Exception as e:
        log.error(f"Failed to setup HBAY Nuke Toolsets menu: {e}", exc_info=True)


# Run menu setup
main()
