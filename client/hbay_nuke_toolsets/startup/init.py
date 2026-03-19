"""Nuke initialization for HBAY Shared Toolsets.

This file is loaded first by Nuke's startup process.
Performs basic initialization before menu.py is loaded.
"""

import os
import logging

# Setup logging
logging.basicConfig()
log = logging.getLogger("ayon.hbay_nuke_toolsets")
log.setLevel(logging.INFO)

log.info("HBAY Nuke Toolsets: Initialization started")
