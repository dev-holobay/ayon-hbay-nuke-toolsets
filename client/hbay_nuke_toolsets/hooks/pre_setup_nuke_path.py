import os

from ayon_applications import PreLaunchHook


class HbayNukeToolsetsPreLaunch(PreLaunchHook):
    app_groups = ["nuke"]  # Apply to nuke applications

    def execute(self):
        # Add your custom NUKE_PATH here

        your_addon_root = os.path.dirname(os.path.dirname(__file__))
        nuke_startup_path = os.path.join(your_addon_root, "startup")

        nuke_path = self.launch_context.env.get("NUKE_PATH", "")
        paths = [nuke_startup_path]
        if nuke_path:
            for p in nuke_path.split(os.pathsep):
                if not p in paths:
                    paths.append(p)

        self.launch_context.env["NUKE_PATH"] = os.pathsep.join(paths)
        self.log.info("NUKE_PATH updated with %s to %s", nuke_startup_path,
                      os.pathsep.join(paths))
