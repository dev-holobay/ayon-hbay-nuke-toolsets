from ayon_server.settings import BaseSettingsModel, SettingsField


class HbayNukeToolsetsSettings(BaseSettingsModel):
    """Settings for HBAY Nuke Toolsets addon."""

    enabled: bool = SettingsField(
        True,
        title="Enable Shared Toolsets"
    )

    toolsets_path_template: str = SettingsField(
        "{root[work]}/{project[name]}/sharedToolSets",
        title="Toolsets Path Template",
        description=(
            "Path template for toolset storage using AYON anatomy tokens. "
            "Examples: '{root[work]}/sharedToolSets' or '{root[work]}/_gen/pipeline/sharedToolSets'"
        ),
        scope=["studio", "project"]
    )

    enable_delete_mode: bool = SettingsField(
        False,
        title="Enable Delete Mode",
        description="Allow users to delete toolsets from the menu",
        scope=["studio"]
    )


DEFAULT_VALUES = {
    "enabled": True,
    "toolsets_path_template": "{root[work]}/{project[name]}/sharedToolSets",
    "enable_delete_mode": False
}
