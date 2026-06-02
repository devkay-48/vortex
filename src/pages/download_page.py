import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from widgets.url_bar import UrlBar
from widgets.media_card import MediaCard
from widgets.format_picker import FormatPicker
from widgets.download_row import DownloadRow
from core.engine import inspect_url, start_download
from core.parser import parse_formats
from core.errors import map_error


class DownloadPage(Gtk.Box):

    def __init__(self, toast_overlay: Adw.ToastOverlay, settings=None, history_page=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self._toast_overlay = toast_overlay
        self._settings = settings
        self._history_page = history_page
        self._current_url = None
        self._current_data = None
        self._allow_playlist = False
        self._active_downloads = []  # list of DownloadRow
        self._build_ui()

    def _build_ui(self):
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        scroll.set_vexpand(True)
        self.append(scroll)

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._content)

        # URL bar
        self._url_bar = UrlBar()
        self._url_bar.emit_url = self._on_url_submitted
        self._content.append(self._url_bar)

        # Playlist toggle (hidden until URL resolves)
        self._playlist_revealer = Gtk.Revealer()
        self._playlist_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self._playlist_revealer.set_reveal_child(False)
        self._content.append(self._playlist_revealer)

        playlist_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        playlist_box.set_margin_start(16)
        playlist_box.set_margin_end(16)
        playlist_box.set_margin_top(4)
        playlist_box.set_margin_bottom(4)
        self._playlist_revealer.set_child(playlist_box)

        playlist_label = Gtk.Label(label="Download full playlist")
        playlist_label.add_css_class("dim-label")
        playlist_label.set_hexpand(True)
        playlist_label.set_halign(Gtk.Align.START)
        playlist_box.append(playlist_label)

        self._playlist_switch = Gtk.Switch()
        self._playlist_switch.set_active(False)
        self._playlist_switch.set_valign(Gtk.Align.CENTER)
        self._playlist_switch.connect("notify::active", self._on_playlist_toggled)
        playlist_box.append(self._playlist_switch)

        # Media info + format picker (revealed after URL resolves)
        self._info_revealer = Gtk.Revealer()
        self._info_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self._info_revealer.set_reveal_child(False)
        self._content.append(self._info_revealer)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._info_revealer.set_child(info_box)

        self._media_card = MediaCard()
        info_box.append(self._media_card)

        self._format_picker = FormatPicker()
        info_box.append(self._format_picker)

        # Action buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)
        btn_box.set_margin_bottom(8)
        self._content.append(btn_box)

        self._new_btn = Gtk.Button(label="New Download")
        self._new_btn.add_css_class("pill")
        self._new_btn.set_visible(False)
        self._new_btn.connect("clicked", self._on_new_clicked)
        btn_box.append(self._new_btn)

        self._dl_button = Gtk.Button(label="Download")
        self._dl_button.add_css_class("suggested-action")
        self._dl_button.add_css_class("pill")
        self._dl_button.set_size_request(200, -1)
        self._dl_button.set_visible(False)
        self._dl_button.connect("clicked", self._on_download_clicked)
        btn_box.append(self._dl_button)

        # Active downloads queue list
        self._queue_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._content.append(self._queue_box)

        # Empty state
        self._empty_hint = Adw.StatusPage(
            title="Paste a URL to get started",
            description="YouTube, SoundCloud, and hundreds of other sites supported.",
            icon_name="folder-download-symbolic",
        )
        self._empty_hint.set_vexpand(True)
        self._content.append(self._empty_hint)

    # ------------------------------------------------------------------ #
    # URL inspection
    # ------------------------------------------------------------------ #

    def _on_url_submitted(self, url: str):
        self._current_url = url
        self._empty_hint.set_visible(False)
        self._media_card.clear()
        self._format_picker.reset()
        self._dl_button.set_visible(False)
        self._new_btn.set_visible(False)
        self._info_revealer.set_reveal_child(False)
        self._playlist_revealer.set_reveal_child(False)
        self._playlist_switch.set_active(False)
        self._allow_playlist = False
        inspect_url(url, self._on_inspect_done, allow_playlist=False)

    def _on_inspect_done(self, data, error):
        self._url_bar.set_loading(False)
        if error:
            self._show_toast(f"Could not load URL: {map_error(error)}")
            self._empty_hint.set_visible(True)
            return
        self._current_data = data
        self._media_card.populate(data)
        formats = parse_formats(data)
        self._format_picker.populate(formats)
        self._info_revealer.set_reveal_child(True)
        self._playlist_revealer.set_reveal_child(True)
        self._dl_button.set_visible(True)

    def _on_playlist_toggled(self, switch, _):
        self._allow_playlist = switch.get_active()

    # ------------------------------------------------------------------ #
    # Download
    # ------------------------------------------------------------------ #

    def _on_download_clicked(self, btn):
        if not self._current_url:
            return

        output_dir = self._settings.get_output_dir() if self._settings else None
        extra_args = self._settings.get_extra_args() if self._settings else []
        args = extra_args + self._format_picker.get_download_args(output_dir=output_dir)

        browser = None
        if self._settings:
            src = self._settings._get("cookie-source")
            browser = src if src and src != "none" else "chrome"

        title = self._current_data.get("title", self._current_url) if self._current_data else self._current_url

        # Create a download row for this job
        row = DownloadRow(
            title=title,
            url=self._current_url,
            output_dir=output_dir,
        )
        self._queue_box.prepend(row)
        self._active_downloads.append(row)

        # Capture row/url/title in closure
        current_url = self._current_url
        current_data = self._current_data

        def on_progress(parsed, r=row):
            r.update_progress(parsed)

        def on_done(returncode, stderr, r=row, t=title, u=current_url, d=current_data):
            if returncode == -99:
                r.set_cancelled()
                return
            if returncode == 0:
                r.set_done(success=True)
                self._show_toast(f"Downloaded: {t[:50]}")
                self._write_queue(t, u, success=True)
            else:
                msg = map_error(stderr)
                r.set_done(success=False, message=msg)
                self._show_toast(f"Failed: {msg}")
                self._write_queue(t, u, success=False)
            if self._history_page:
                self._history_page.refresh()

        handle = start_download(
            current_url,
            args,
            on_progress,
            on_done,
            browser=browser,
            allow_playlist=self._allow_playlist,
        )
        row.set_handle(handle)

        # Reset UI for next download immediately
        self._on_new_clicked(None)

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #

    def _on_new_clicked(self, btn):
        self._current_url = None
        self._current_data = None
        self._url_bar.clear()
        self._media_card.clear()
        self._format_picker.reset()
        self._info_revealer.set_reveal_child(False)
        self._playlist_revealer.set_reveal_child(False)
        self._playlist_switch.set_active(False)
        self._allow_playlist = False
        self._dl_button.set_visible(False)
        self._new_btn.set_visible(False)
        # Keep empty hint hidden if there are active downloads
        if not self._active_downloads:
            self._empty_hint.set_visible(True)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _write_queue(self, title: str, url: str, success: bool):
        try:
            from core.queue import DownloadQueue
            DownloadQueue().add(title=title, url=url, success=success)
        except Exception as e:
            print(f"[Vortex] Queue write error: {e}")

    def _show_toast(self, message: str):
        toast = Adw.Toast(title=message, timeout=4)
        self._toast_overlay.add_toast(toast)
