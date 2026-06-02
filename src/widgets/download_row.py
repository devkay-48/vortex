import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import os


class DownloadRow(Gtk.Box):
    """
    A self-contained download queue row.
    Shows thumbnail placeholder, title, progress bar, speed, ETA,
    cancel button, and open-folder button on completion.
    """

    def __init__(self, title: str, url: str, output_dir: str = None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self._title = title
        self._url = url
        self._output_dir = output_dir or GLib.get_user_special_dir(
            GLib.UserDirectory.DIRECTORY_DOWNLOAD
        )
        self._handle = None
        self._cancelled = False
        self._build_ui()

    def _build_ui(self):
        self.add_css_class("card")
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(6)
        self.set_margin_bottom(6)

        # Main row
        main_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        main_row.set_margin_start(12)
        main_row.set_margin_end(12)
        main_row.set_margin_top(10)
        main_row.set_margin_bottom(10)
        self.append(main_row)

        # Icon placeholder
        icon = Gtk.Image.new_from_icon_name("folder-download-symbolic")
        icon.set_pixel_size(32)
        icon.set_valign(Gtk.Align.CENTER)
        icon.add_css_class("dim-label")
        main_row.append(icon)

        # Text + progress column
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        col.set_hexpand(True)
        col.set_valign(Gtk.Align.CENTER)
        main_row.append(col)

        # Title
        self._title_label = Gtk.Label(label=self._title)
        self._title_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self._title_label.set_halign(Gtk.Align.START)
        self._title_label.set_max_width_chars(60)
        col.append(self._title_label)

        # Progress bar
        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_hexpand(True)
        col.append(self._progress_bar)

        # Status label
        self._status_label = Gtk.Label(label="Waiting…")
        self._status_label.add_css_class("dim-label")
        self._status_label.add_css_class("caption")
        self._status_label.set_halign(Gtk.Align.START)
        col.append(self._status_label)

        # Action buttons column
        self._btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self._btn_box.set_valign(Gtk.Align.CENTER)
        main_row.append(self._btn_box)

        # Cancel button
        self._cancel_btn = Gtk.Button(icon_name="media-playback-stop-symbolic")
        self._cancel_btn.add_css_class("destructive-action")
        self._cancel_btn.add_css_class("circular")
        self._cancel_btn.set_tooltip_text("Cancel")
        self._cancel_btn.set_valign(Gtk.Align.CENTER)
        self._cancel_btn.connect("clicked", self._on_cancel)
        self._btn_box.append(self._cancel_btn)

        # Open folder button (hidden until done)
        self._open_btn = Gtk.Button(icon_name="folder-open-symbolic")
        self._open_btn.add_css_class("flat")
        self._open_btn.add_css_class("circular")
        self._open_btn.set_tooltip_text("Open download folder")
        self._open_btn.set_valign(Gtk.Align.CENTER)
        self._open_btn.set_visible(False)
        self._open_btn.connect("clicked", self._on_open_folder)
        self._btn_box.append(self._open_btn)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def set_handle(self, handle):
        self._handle = handle

    def update_progress(self, parsed: dict):
        pct = parsed.get("percent", 0) / 100.0
        self._progress_bar.set_fraction(pct)
        speed = parsed.get("speed", "")
        eta = parsed.get("eta", "")
        self._status_label.set_label(
            f"{parsed.get('percent', 0):.1f}%  •  {speed}  •  ETA {eta}"
        )

    def set_done(self, success: bool, message: str = ""):
        self._cancel_btn.set_visible(False)
        self._open_btn.set_visible(True)
        if success:
            self._progress_bar.set_fraction(1.0)
            self._status_label.set_label("✓ Complete")
            self._title_label.remove_css_class("dim-label")
        else:
            self._status_label.set_label(f"✗ {message[:80]}")
            self._title_label.add_css_class("dim-label")

    def set_cancelled(self):
        self._cancel_btn.set_visible(False)
        self._progress_bar.set_fraction(0)
        self._status_label.set_label("Cancelled")
        self._title_label.add_css_class("dim-label")

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #

    def _on_cancel(self, btn):
        if self._handle:
            self._handle.cancel()
        self.set_cancelled()

    def _on_open_folder(self, btn):
        try:
            import subprocess
            subprocess.Popen(["xdg-open", self._output_dir])
        except Exception:
            pass
