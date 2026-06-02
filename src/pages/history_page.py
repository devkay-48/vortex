import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.queue import DownloadQueue


class HistoryPage(Gtk.Box):

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Header bar actions
        self._toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self._toolbar.set_margin_start(16)
        self._toolbar.set_margin_end(16)
        self._toolbar.set_margin_top(8)
        self._toolbar.set_margin_bottom(8)

        title = Gtk.Label(label="Download History")
        title.add_css_class("heading")
        title.set_hexpand(True)
        title.set_halign(Gtk.Align.START)
        self._toolbar.append(title)

        clear_btn = Gtk.Button(label="Clear All")
        clear_btn.add_css_class("destructive-action")
        clear_btn.add_css_class("flat")
        clear_btn.connect("clicked", self._on_clear_clicked)
        self._toolbar.append(clear_btn)

        self.append(self._toolbar)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(sep)

        # Scrollable list
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scroll.set_vexpand(True)
        self.append(scroll)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._list_box)

        self._empty_page = Adw.StatusPage(
            title="No Downloads Yet",
            description="Completed and failed downloads will appear here.",
            icon_name="document-open-recent-symbolic"
        )
        self._empty_page.set_vexpand(True)

        self._stack = Gtk.Stack()
        self._stack.set_vexpand(True)
        # replace scroll with stack
        self.remove(scroll)
        self.append(self._stack)

        self._stack.add_named(scroll, "list")
        self._stack.add_named(self._empty_page, "empty")

        self._load_history()

    def _load_history(self):
        # Clear existing rows
        while True:
            child = self._list_box.get_first_child()
            if child is None:
                break
            self._list_box.remove(child)

        entries = DownloadQueue().all()

        if not entries:
            self._stack.set_visible_child_name("empty")
            return

        self._stack.set_visible_child_name("list")

        clamp = Adw.Clamp(maximum_size=800, tightening_threshold=600)
        clamp.set_margin_top(12)
        clamp.set_margin_bottom(12)
        self._list_box.append(clamp)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        clamp.set_child(inner)

        group = Adw.PreferencesGroup()
        inner.append(group)

        for entry in entries:
            row = self._make_row(entry)
            group.add(row)

    def _make_row(self, entry: dict) -> Adw.ActionRow:
        success = entry.get("success", True)
        title   = entry.get("title") or entry.get("url", "Unknown")
        ts      = entry.get("timestamp", "")
        url     = entry.get("url", "")

        # Format timestamp nicely
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(ts)
            ts_display = dt.strftime("%b %d, %Y  %H:%M")
        except Exception:
            ts_display = ts

        row = Adw.ActionRow()
        row.set_title(title[:80])
        row.set_subtitle(ts_display)
        row.set_tooltip_text(url)

        # Status icon
        icon_name = "emblem-ok-symbolic" if success else "dialog-error-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.add_css_class("success" if success else "error")
        icon.set_valign(Gtk.Align.CENTER)
        row.add_prefix(icon)

        # Copy URL button
        copy_btn = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_btn.set_tooltip_text("Copy URL")
        copy_btn.add_css_class("flat")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.connect("clicked", self._on_copy_url, url)
        row.add_suffix(copy_btn)

        return row

    def _on_copy_url(self, btn, url: str):
        btn.get_root().get_clipboard().set(url)

    def _on_clear_clicked(self, btn):
        dialog = Adw.AlertDialog(
            heading="Clear History?",
            body="All download history will be permanently deleted.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("clear", "Clear All")
        dialog.set_response_appearance("clear", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_clear_confirmed)
        dialog.present(self.get_root())

    def _on_clear_confirmed(self, dialog, response):
        if response == "clear":
            DownloadQueue().clear()
            self._load_history()

    def refresh(self):
        """Call this after a download completes to update the list."""
        self._load_history()
