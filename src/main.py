import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(__file__))
from window import VortexWindow


class VortexApp(Adw.Application):

    def __init__(self):
        super().__init__(application_id="org.gnome.Vortex")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = VortexWindow(application=app)
        self.win.present()
        # Check deps after window is visible so dialog has a parent
        GLib.idle_add(self._check_dependencies)

    def _check_dependencies(self):
        missing = []
        if not shutil.which("ffmpeg"):
            missing.append("ffmpeg")
        if not shutil.which("yt-dlp"):
            missing.append("yt-dlp")

        if missing:
            self._show_missing_dialog(missing)
        return False  # don't repeat

    def _show_missing_dialog(self, missing: list):
        names = " and ".join(missing)
        if "ffmpeg" in missing and "yt-dlp" in missing:
            install_cmd = "sudo dnf install ffmpeg yt-dlp"
        elif "ffmpeg" in missing:
            install_cmd = "sudo dnf install ffmpeg"
        else:
            install_cmd = "sudo dnf install yt-dlp"

        dialog = Adw.AlertDialog(
            heading=f"Missing: {names}",
            body=f"Vortex requires {names} to work.\n\nInstall with:\n{install_cmd}",
        )
        dialog.add_response("close", "Close")
        dialog.add_response("copy", "Copy Command")
        dialog.set_default_response("copy")
        dialog.set_close_response("close")
        dialog.connect("response", self._on_dep_dialog_response, install_cmd)
        dialog.present(self.win)

    def _on_dep_dialog_response(self, dialog, response, install_cmd):
        if response == "copy":
            clipboard = self.win.get_clipboard()
            clipboard.set(install_cmd)
            toast = Adw.Toast(title="Command copied to clipboard", timeout=3)
            self.win._toast_overlay.add_toast(toast)


def main():
    app = VortexApp()
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    main()
