import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from pages.download_page import DownloadPage
from pages.settings_page import SettingsPage
from pages.history_page import HistoryPage


class VortexWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Vortex")
        self.set_default_size(800, 650)
        self._build_ui()

    def _build_ui(self):
        self._toast_overlay = Adw.ToastOverlay()
        self.set_content(self._toast_overlay)

        toolbar_view = Adw.ToolbarView()
        self._toast_overlay.set_child(toolbar_view)

        header = Adw.HeaderBar()
        header.set_centering_policy(Adw.CenteringPolicy.STRICT)
        toolbar_view.add_top_bar(header)

        self._stack = Adw.ViewStack()
        toolbar_view.set_content(self._stack)

        switcher = Adw.ViewSwitcher()
        switcher.set_stack(self._stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Settings (created early so download_page can reference it)
        self._settings_page = SettingsPage()

        # History page
        self._history_page = HistoryPage()

        # Download page
        self._download_page = DownloadPage(
            toast_overlay=self._toast_overlay,
            settings=self._settings_page,
            history_page=self._history_page,
        )

        # Add to stack in display order
        self._stack.add_titled_with_icon(
            self._download_page, "download", "Download",
            "folder-download-symbolic"
        )
        self._stack.add_titled_with_icon(
            self._history_page, "history", "History",
            "document-open-recent-symbolic"
        )
        self._stack.add_titled_with_icon(
            self._settings_page, "settings", "Settings",
            "preferences-system-symbolic"
        )

        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self._stack)
        toolbar_view.add_bottom_bar(switcher_bar)
