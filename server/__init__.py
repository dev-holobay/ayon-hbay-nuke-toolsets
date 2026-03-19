from ayon_server.addons import BaseServerAddon

from .settings import HbayNukeToolsetsSettings, DEFAULT_VALUES


class HbayNukeToolsetsAddon(BaseServerAddon):
    """HBAY Nuke Toolsets server addon.

    Provides shared toolsets functionality for Nuke artists,
    allowing them to publish and share toolsets across projects.
    """

    settings_model = HbayNukeToolsetsSettings

    async def get_default_settings(self):
        """Return default settings for the addon."""
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
