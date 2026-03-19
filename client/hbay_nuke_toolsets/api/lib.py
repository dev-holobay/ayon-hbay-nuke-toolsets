"""Library functions for HBAY Nuke Toolsets."""

import os
import logging

from ayon_core.pipeline import get_current_project_name, Anatomy
from ayon_core.settings import get_project_settings, get_studio_settings

log = logging.getLogger("ayon.hbay_nuke_toolsets")


def get_toolset_sources():
    """Get toolset sources from AYON settings and anatomy.

    Uses AYON's anatomy system to resolve toolset paths from templates.
    Automatically gets all projects the user has access to.

    Returns:
        dict: Dictionary mapping project names to resolved toolset paths.
            Format: {
                "project_name": "/resolved/path/to/toolsets"
            }
    """
    sources = {}
    import nuke
    try:
        from ayon_core.addon import AddonsManager
        from ayon_api import get_projects

        manager = AddonsManager()
        addon = manager.get_enabled_addon("hbay_nuke_toolsets")

        if not addon:
            log.warning("HBAY Nuke Toolsets addon not found or not enabled")
            return sources

        # Get studio settings
        # studio_settings = get_studio_settings()
        #
        # if not studio_settings.get("enabled", True):
        #     log.info("HBAY Nuke Toolsets is disabled in settings")
        #     return sources

        # Get all projects user has access to
        projects = get_projects(fields=["name", "code"])

        for project in projects:
            project_name = project["name"]
            nuke.tprint(project_name)
            try:
                # Get project-specific settings (with studio fallback)
                project_settings = {} #addon.get_project_settings(project_name)

                template = project_settings.get(
                    "toolsets_path_template",
                    "{root[work]}/{project[name]}/sharedToolSets"
                )

                # Get project anatomy
                anatomy = Anatomy(project_name)

                # Format the template with anatomy roots
                toolsets_path = template.format(
                    root=anatomy.roots,
                    project={"name": project_name,
                             "code": project.get("code", "")}
                )

                # Normalize path
                toolsets_path = os.path.normpath(toolsets_path).replace("\\",
                                                                        "/")

                # Add to sources if directory exists or can be created
                if os.path.isdir(toolsets_path) or _try_create_dir(
                        toolsets_path):
                    sources[project_name] = toolsets_path
                    log.debug(
                        f"Added toolset source: {project_name} -> {toolsets_path}")
                else:
                    log.debug(
                        f"Skipping {project_name}: path not accessible: {toolsets_path}")

            except Exception as e:
                log.warning(
                    f"Failed to resolve toolset path for project {project_name}: {e}")
                continue

    except Exception as e:
        log.error(f"Failed to get toolset sources: {e}", exc_info=True)

    nuke.tprint(sources)
    return sources


def _try_create_dir(path):
    """Try to create a directory, return True if successful or already exists.

    Args:
        path (str): Directory path to create

    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
            log.debug(f"Created directory: {path}")
        return True
    except (OSError, PermissionError) as e:
        log.debug(f"Cannot create directory {path}: {e}")
        return False


def ensure_folder(path):
    """Ensure directory exists, create if needed.

    Args:
        path (str): Directory path to ensure exists
    """
    directory = os.path.dirname(path) if os.path.splitext(path)[1] else path

    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
            log.debug(f"Created directory: {directory}")
        except OSError as e:
            log.warning(f"Failed to create directory {directory}: {e}")
