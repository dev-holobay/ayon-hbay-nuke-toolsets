"""Toolset management functionality for Nuke.

Refactored from original base.py implementation.
"""

import os
import logging
import shutil

import nuke
import nukescripts

from ayon_core.pipeline import get_current_project_name, get_current_context, \
    Anatomy
from ayon_core.settings import get_project_settings
from .lib import get_toolset_sources, ensure_folder

log = logging.getLogger("ayon.hbay_nuke_toolsets")


class CreateToolsetsPanel(nukescripts.PythonPanel):
    """Panel for creating shared toolsets in Nuke.

    Allows artists to publish toolsets to shared locations
    organized by project and folder structure.
    """

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self,
            'Create a Shared ToolSet',
            'com.hbay.CreateSharedToolset'
        )

        # Get toolset sources from settings
        self.roots = get_toolset_sources()
        self.user_folders = []

        # Build folder list for each source
        # Use list() to create a copy since _build_folder_list modifies self.roots
        for source_name, root_path in list(self.roots.items()):
            self._build_folder_list(root_path, source_name)

        # Create UI knobs
        self.menu_choice = nuke.Enumeration_Knob(
            'menuItemChoice',
            'ToolSets location',
            self.user_folders
        )
        self.menu_choice.setTooltip(
            "The location where the ToolSet will be stored. "
            "Select 'root' to place in the main location."
        )

        self.menu_path = nuke.String_Knob('itemName', 'ToolSet name:')
        self.menu_path.setTooltip(
            "ToolSet name. Use '/' to create submenus, "
            "e.g., '3D/Basic3D' creates a '3D' submenu with 'Basic3D' toolset."
        )

        # Add knobs to panel
        self.addKnob(self.menu_choice)
        self.addKnob(self.menu_path)

        log.debug(f"CreateToolsetsPanel initialized with roots: {self.roots}")

    def _build_folder_list(self, full_path, menu_path):
        """Recursively build list of available folders.

        Args:
            full_path (str): Filesystem path to scan
            menu_path (str): Menu path representation
        """
        # Ensure directory exists
        if not os.path.isdir(full_path):
            ensure_folder(full_path)
            return

        try:
            file_contents = sorted(os.listdir(str(full_path)), key=str.lower)
        except OSError as e:
            log.warning(f"Cannot read directory {full_path}: {e}")
            return
        if not menu_path in self.user_folders:
            self.user_folders.append(menu_path)
        for item in file_contents:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                # Avoid duplicates in root
                if menu_path == item:
                    self.user_folders.append(item)
                    self.roots[item] = item_path.replace("\\", "/")
                else:
                    menu_name = f"{menu_path}/{item}"
                    self.user_folders.append(menu_name)
                    self.roots[menu_name] = item_path.replace("\\", "/")
                    # Recurse into subdirectory
                    self._build_folder_list(item_path, menu_name)

    def _create_preset(self):
        """Create the toolset file in the selected location.

        Returns:
            bool: True if toolset was created successfully
        """
        selected_location = str(self.menu_choice.value())
        toolset_name = str(self.menu_path.value())

        if not toolset_name:
            nuke.message("Please enter a toolset name")
            return False

        root = self.roots.get(selected_location)
        if not root:
            nuke.message(f"Invalid location: {selected_location}")
            return False

        try:
            # Use Nuke's built-in createToolset function
            if nuke.createToolset(filename=toolset_name, overwrite=1,
                                  rootPath=root):
                # Nuke creates in a ToolSets subdirectory, move it to root
                temp_path = os.path.join(root, "ToolSets", f"{toolset_name}.nk")
                final_path = os.path.join(root, f"{toolset_name}.nk")

                temp_path = temp_path.replace("\\", "/")
                final_path = final_path.replace("\\", "/")

                ensure_folder(final_path)

                if os.path.exists(temp_path):
                    shutil.move(temp_path, final_path)
                    log.info(f"Created toolset: {final_path}")

                    # Clean up temp ToolSets directory
                    toolsets_dir = os.path.join(root, "ToolSets")
                    if os.path.isdir(toolsets_dir):
                        try:
                            shutil.rmtree(toolsets_dir)
                        except OSError as e:
                            log.warning(f"Failed to remove temp directory: {e}")

                return True
            else:
                nuke.message("Failed to create toolset")
                return False

        except Exception as e:
            log.error(f"Error creating toolset: {e}", exc_info=True)
            nuke.message(f"Error creating toolset: {str(e)}")
            return False

    def _get_preset_path(self):
        """Update menu path based on selection."""
        self.menu_path.setValue("")

    def knobChanged(self, knob):
        """Handle knob changes in the panel."""
        if knob == self.menu_choice:
            self._get_preset_path()


def create_toolsets_panel():
    """Show the create toolsets panel.

    Returns:
        bool: True if panel was confirmed, False otherwise
    """
    if not nuke.nodesSelected():
        nuke.message("No nodes are selected")
        return False

    panel = CreateToolsetsPanel()
    result = panel.showModalDialog()

    # If OK was pressed, create the preset
    if result:
        panel._create_preset()
        refresh_toolsets_menu()

    return result


def create_toolset_in_context():
    """Create a toolset using the current AYON context path.

    Uses the current context hierarchy (asset/shot path) as the folder structure.
    Example: /assets/props/eagle/compositing -> {root[work]}/sharedToolSets/assets/props/eagle/

    Returns:
        bool: True if toolset was created successfully
    """
    if not nuke.nodesSelected():
        nuke.message("No nodes are selected")
        return False

    try:
        # Get current context
        context = get_current_context()
        project_name = get_current_project_name()

        if not context or not project_name:
            nuke.message(
                "No AYON context found. Please work in a valid AYON context.")
            return False

        if not context.get("folder_path"):
            nuke.message(
                "Cannot determine context path from current AYON context.")
            return False

        context_path = context.get("folder_path")

        all_project_settings = get_project_settings(project_name)
        project_settings = all_project_settings[
            "hbay_nuke_toolsets"]
        template = project_settings.get("toolsets_path_template",
                                        "{root[work]}/{project[name]}/sharedToolSets")

        # Get anatomy and resolve template
        anatomy = Anatomy(project_name)
        base_path = template.format(
            root=anatomy.roots,
            project={"name": project_name, "code": project_name}
        )

        # Add context path to base
        toolset_dir = os.path.join(base_path, context_path.lstrip("/")).replace(
            "\\", "/")

        # Ensure directory exists
        ensure_folder(toolset_dir)

        # Show simple dialog for toolset name
        toolset_name = nuke.getInput("Toolset name:", "")

        if not toolset_name:
            return False

        # Create the toolset
        result = _create_toolset_file(toolset_name, toolset_dir, context_path)
        if result:
            refresh_toolsets_menu()
        return result

    except Exception as e:
        log.error(f"Failed to create toolset in context: {e}", exc_info=True)
        nuke.message(f"Error: {str(e)}")
        return False


def _create_toolset_file(toolset_name, toolset_dir, context_label=""):
    """Create a toolset file in the specified directory.

    Args:
        toolset_name (str): Name of the toolset
        toolset_dir (str): Directory path where toolset should be created
        context_label (str): Optional label for logging/display

    Returns:
        bool: True if successful
    """
    try:
        # Use Nuke's built-in createToolset function
        if nuke.createToolset(filename=toolset_name, overwrite=1,
                              rootPath=toolset_dir):
            # Nuke creates in a ToolSets subdirectory, move it to root
            temp_path = os.path.join(toolset_dir, "ToolSets",
                                     f"{toolset_name}.nk")
            final_path = os.path.join(toolset_dir, f"{toolset_name}.nk")

            temp_path = temp_path.replace("\\", "/")
            final_path = final_path.replace("\\", "/")

            ensure_folder(final_path)

            if os.path.exists(temp_path):
                shutil.move(temp_path, final_path)
                log_path = f"{context_label}/{toolset_name}.nk" if context_label else final_path
                log.info(f"Created toolset: {log_path}")

                # Clean up temp ToolSets directory
                toolsets_dir = os.path.join(toolset_dir, "ToolSets")
                if os.path.isdir(toolsets_dir):
                    try:
                        shutil.rmtree(toolsets_dir)
                    except OSError as e:
                        log.warning(f"Failed to remove temp directory: {e}")

            return True
        else:
            nuke.message("Failed to create toolset")
            return False

    except Exception as e:
        log.error(f"Error creating toolset file: {e}", exc_info=True)
        nuke.message(f"Error creating toolset: {str(e)}")
        return False


def delete_toolset(root_path, file_name):
    """Delete a toolset file.

    Args:
        root_path (str): Root path of the toolset location
        file_name (str): Full path to the toolset file
    """
    if nuke.ask(
            f'Are you sure you want to delete ToolSet {os.path.basename(file_name)}?'):
        try:
            os.remove(file_name)
            log.info(f"Deleted toolset: {file_name}")
            refresh_toolsets_menu()
        except OSError as e:
            log.error(f"Failed to delete toolset: {e}")
            nuke.message(f"Failed to delete toolset: {str(e)}")


def refresh_toolsets_menu():
    """Refresh the shared toolsets menu."""
    toolbar = nuke.menu("Nodes")
    menu = toolbar.findItem("sharedToolSets")

    if menu:
        menu.clearMenu()
        setup_toolsets_menu(toolbar)
        log.info("Toolsets menu refreshed")


def setup_toolsets_menu(toolbar):
    """Setup the shared toolsets menu in Nuke.

    Args:
        toolbar: Nuke toolbar menu object
    """
    menu = toolbar.addMenu("sharedToolSets", "sharedToolSets.png")

    # Add control commands
    menu.addCommand(
        "Create",
        "from hbay_nuke_toolsets.api import create_toolsets_panel; "
        "create_toolsets_panel()",
        icon="ToolsetCreate.png"
    )
    menu.addCommand(
        "Create in Context",
        "from hbay_nuke_toolsets.api import create_toolset_in_context; "
        "create_toolset_in_context()",
        icon="ToolsetCreate.png"
    )
    menu.addCommand(
        "Refresh",
        "from hbay_nuke_toolsets.api import refresh_toolsets_menu; "
        "refresh_toolsets_menu()"
    )
    menu.addCommand("-", "", "")

    # Populate with available toolsets
    has_toolsets = _populate_toolsets_menu(menu, delete_mode=False)

    # Add delete menu if enabled in settings
    if has_toolsets:
        try:
            from ayon_api import get_addon_settings
            from ..version import __version__

            studio_settings = get_addon_settings("hbay_nuke_toolsets",
                                                 str(__version__))

            if studio_settings.get("enable_delete_mode", False):
                menu.addCommand("-", "", "")
                delete_menu = menu.addMenu("Delete", "ToolsetDelete.png")
                _populate_toolsets_menu(delete_menu, delete_mode=True)
        except Exception as e:
            log.warning(f"Failed to check delete mode setting: {e}")


def _populate_toolsets_menu(menu, delete_mode=False):
    """Populate menu with available toolsets organized by project.

    Args:
        menu: Nuke menu object
        delete_mode (bool): If True, add delete commands instead of load

    Returns:
        bool: True if any toolsets were found
    """
    all_toolsets_list = []
    sources = get_toolset_sources()
    has_toolsets = False

    # Add toolsets from each source with project as submenu
    for source_name, root_path in sources.items():
        if os.path.isdir(root_path):
            # Create a submenu for this project
            project_menu = menu.addMenu(source_name)

            if _create_toolset_menu_items(
                    project_menu,
                    root_path,
                    root_path,
                    delete_mode,
                    all_toolsets_list
            ):
                has_toolsets = True

    return has_toolsets


def _create_toolset_menu_items(menu, root_path, full_path, delete_mode,
                               all_toolsets_list):
    """Recursively create menu items for toolsets.

    Args:
        menu: Nuke menu object
        root_path (str): Root path for this source
        full_path (str): Current directory being scanned
        delete_mode (bool): If True, create delete commands
        all_toolsets_list (list): List tracking added toolsets

    Returns:
        bool: True if any items were added
    """
    try:
        file_contents = sorted(os.listdir(str(full_path)), key=str.lower)
    except OSError as e:
        log.warning(f"Cannot read directory {full_path}: {e}")
        return False

    exclude_paths = nuke.getToolsetExcludePaths()
    has_items = False

    if not file_contents:
        return False

    # First pass: add directories as submenus
    for item in file_contents:
        new_path = os.path.join(full_path, item).replace("\\", "/")

        # Check if path should be ignored
        ignore = False
        if ".svn" in new_path or ".git" in new_path:
            ignore = True
        else:
            for exclude in exclude_paths:
                exclude = exclude.replace("\\", "/")
                if exclude in new_path:
                    ignore = True
                    break

        if os.path.isdir(new_path) and not ignore:
            if os.listdir(new_path):
                all_toolsets_list.append(item)
                submenu = menu.addMenu(item)
                if _create_toolset_menu_items(
                        submenu,
                        root_path,
                        new_path,
                        delete_mode,
                        all_toolsets_list
                ):
                    has_items = True

    # Second pass: add .nk files as commands
    for item in file_contents:
        full_file_path = os.path.join(full_path, item).replace("\\", "/")

        if not os.path.isdir(full_file_path):
            if item.endswith(".nk"):
                toolset_name = item[:-3]  # Remove .nk extension

                if delete_mode:
                    menu.addCommand(
                        toolset_name,
                        f'from hbay_nuke_toolsets.api import delete_toolset; '
                        f'delete_toolset("{root_path}", "{full_file_path}")'
                    )
                    has_items = True
                else:
                    menu.addCommand(
                        toolset_name,
                        f'nuke.loadToolset("{full_file_path}")'
                    )
                    log.debug(f"Added toolset: {full_file_path}")
                    has_items = True

    return has_items
