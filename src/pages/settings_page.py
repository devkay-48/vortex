import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from core.engine import update_ytdlp

SCHEMA_ID = "org.gnome.Vortex"


class SettingsPage(Adw.PreferencesPage):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_icon_name("preferences-system-symbolic")
        self.set_title("Settings")

        try:
            self._settings = Gio.Settings.new(SCHEMA_ID)
        except Exception as e:
            print(f"[Vortex] GSettings error: {e}")
            self._settings = None

        self._build_output_group()
        self._build_network_group()
        self._build_auth_group()
        self._build_advanced_group()
        self._build_about_group()

    # ------------------------------------------------------------------ #
    # OUTPUT
    # ------------------------------------------------------------------ #

    def _build_output_group(self):
        group = Adw.PreferencesGroup(title="Output")
        self.add(group)

        self._folder_row = Adw.EntryRow(title="Download Folder")
        saved = self._get("download-folder")
        self._folder_row.set_text(
            saved if saved else GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
        )
        self._folder_row.connect("changed", lambda r: self._set("download-folder", r.get_text()))

        browse_btn = Gtk.Button(icon_name="folder-open-symbolic")
        browse_btn.set_tooltip_text("Browse…")
        browse_btn.add_css_class("flat")
        browse_btn.set_valign(Gtk.Align.CENTER)
        browse_btn.connect("clicked", self._on_browse_folder)
        self._folder_row.add_suffix(browse_btn)
        group.add(self._folder_row)

        tmpl_row = Adw.EntryRow(title="Filename Template")
        tmpl_row.set_text(self._get("filename-template") or "%(title)s")
        tmpl_row.connect("changed", lambda r: self._set("filename-template", r.get_text()))
        group.add(tmpl_row)

        sep_row = Adw.SwitchRow(
            title="Separate Music / Video Folders",
            subtitle="Music → Music/, Video → Videos/ inside download folder"
        )
        sep_row.set_active(self._get_bool("separate-folders"))
        sep_row.connect("notify::active", lambda r, _: self._set_bool("separate-folders", r.get_active()))
        group.add(sep_row)

    def _on_browse_folder(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title("Choose Download Folder")
        dialog.select_folder(self.get_root(), None, self._on_folder_chosen, None)

    def _on_folder_chosen(self, dialog, result, _):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                self._folder_row.set_text(path)
                self._set("download-folder", path)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # NETWORK
    # ------------------------------------------------------------------ #

    def _build_network_group(self):
        group = Adw.PreferencesGroup(title="Network")
        self.add(group)

        self._speed_row = Adw.SwitchRow(title="Limit Download Speed")
        self._speed_row.set_active(self._get_bool("speed-limit-enabled"))
        self._speed_row.connect("notify::active", self._on_speed_toggle)
        group.add(self._speed_row)

        self._speed_spin = Adw.SpinRow.new_with_range(64, 102400, 64)
        self._speed_spin.set_title("Speed Limit")
        self._speed_spin.set_subtitle("KB/s")
        self._speed_spin.set_value(self._get_int("speed-limit-kbps"))
        self._speed_spin.set_sensitive(self._get_bool("speed-limit-enabled"))
        self._speed_spin.connect(
            "notify::value",
            lambda r, _: self._set_int("speed-limit-kbps", int(r.get_value()))
        )
        group.add(self._speed_spin)

        retry_row = Adw.SpinRow.new_with_range(0, 50, 1)
        retry_row.set_title("Retry Count")
        retry_row.set_subtitle("Retries on network failure")
        retry_row.set_value(self._get_int("retry-count"))
        retry_row.connect(
            "notify::value",
            lambda r, _: self._set_int("retry-count", int(r.get_value()))
        )
        group.add(retry_row)

        proxy_row = Adw.EntryRow(title="Proxy URL")
        proxy_row.set_text(self._get("proxy-url") or "")
        proxy_row.connect("changed", lambda r: self._set("proxy-url", r.get_text()))
        group.add(proxy_row)

    def _on_speed_toggle(self, row, _):
        enabled = row.get_active()
        self._set_bool("speed-limit-enabled", enabled)
        self._speed_spin.set_sensitive(enabled)

    # ------------------------------------------------------------------ #
    # AUTHENTICATION
    # ------------------------------------------------------------------ #

    def _build_auth_group(self):
        group = Adw.PreferencesGroup(
            title="Authentication",
            description="Let yt-dlp use your browser cookies for age-restricted or members-only content."
        )
        self.add(group)

        browsers = ["None", "Firefox", "Chrome", "Chromium", "Brave", "Edge"]
        cookie_row = Adw.ComboRow(title="Browser Cookie Source")
        cookie_row.set_model(Gtk.StringList.new(browsers))

        saved = self._get("cookie-source") or "none"
        idx = next((i for i, b in enumerate(browsers) if b.lower() == saved.lower()), 0)
        cookie_row.set_selected(idx)
        cookie_row.connect("notify::selected", self._on_cookie_changed)
        self._cookie_browsers = browsers
        self._cookie_row = cookie_row
        group.add(cookie_row)

    def _on_cookie_changed(self, row, _):
        idx = row.get_selected()
        val = self._cookie_browsers[idx].lower()
        self._set("cookie-source", val)

    # ------------------------------------------------------------------ #
    # ADVANCED
    # ------------------------------------------------------------------ #

    def _build_advanced_group(self):
        group = Adw.PreferencesGroup(title="Advanced")
        self.add(group)

        for key, title, subtitle in [
            ("embed-metadata",  "Embed Metadata",    "Title, artist, year written into the file"),
            ("embed-thumbnail", "Embed Thumbnail",   "Album art embedded in audio files"),
            ("write-subtitles", "Download Subtitles","Save .srt subtitle file alongside video"),
        ]:
            row = Adw.SwitchRow(title=title, subtitle=subtitle)
            row.set_active(self._get_bool(key))
            row.connect("notify::active", lambda r, _, k=key: self._set_bool(k, r.get_active()))
            group.add(row)

        # Subtitle language with quick-pick chips
        lang_row = Adw.EntryRow(title="Subtitle Language")
        saved_lang = self._get("subtitle-language") or "en"
        lang_row.set_text(saved_lang)
        lang_row.connect("changed", lambda r: self._set("subtitle-language", r.get_text()))
        group.add(lang_row)

        # Language chips row
        chips_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        chips_box.set_margin_start(16)
        chips_box.set_margin_end(16)
        chips_box.set_margin_top(4)
        chips_box.set_margin_bottom(8)

        chip_label = Gtk.Label(label="Quick pick: ")
        chip_label.add_css_class("dim-label")
        chip_label.add_css_class("caption")
        chips_box.append(chip_label)

        for lang_code in ["en", "es", "fr", "de", "ar", "zh", "pt", "ja", "hi", "ru"]:
            chip = Gtk.Button(label=lang_code)
            chip.add_css_class("pill")
            chip.add_css_class("flat")
            chip.add_css_class("caption")
            chip.connect("clicked", lambda _, c=lang_code, r=lang_row: r.set_text(c))
            chips_box.append(chip)

        group.add(Adw.PreferencesRow())  # spacer trick — wrap chips in a row
        # Actually append chips_box directly to page since PreferencesGroup supports it
        self.add(self._wrap_widget(chips_box))

    def _wrap_widget(self, widget):
        """Wrap a plain widget in a PreferencesGroup so it sits cleanly on the page."""
        g = Adw.PreferencesGroup()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(widget)
        g.add(box)
        return g

    # ------------------------------------------------------------------ #
    # ABOUT / UPDATE
    # ------------------------------------------------------------------ #

    def _build_about_group(self):
        group = Adw.PreferencesGroup(title="About")
        self.add(group)

        # yt-dlp version row + update button
        update_row = Adw.ActionRow(
            title="yt-dlp",
            subtitle="Keep yt-dlp updated for best compatibility"
        )
        self._update_btn = Gtk.Button(label="Update Now")
        self._update_btn.add_css_class("flat")
        self._update_btn.set_valign(Gtk.Align.CENTER)
        self._update_btn.connect("clicked", self._on_update_ytdlp)
        update_row.add_suffix(self._update_btn)
        group.add(update_row)

        # App version
        version_row = Adw.ActionRow(title="Vortex", subtitle="v1.0.0")
        group.add(version_row)

    def _on_update_ytdlp(self, btn):
        btn.set_sensitive(False)
        btn.set_label("Updating…")
        update_ytdlp(self._on_update_done)

    def _on_update_done(self, success, message):
        self._update_btn.set_sensitive(True)
        self._update_btn.set_label("Update Now")
        # Show result as a toast on the root window
        root = self.get_root()
        if root and hasattr(root, '_toast_overlay'):
            toast = Adw.Toast(title=message[:100], timeout=5)
            root._toast_overlay.add_toast(toast)
        else:
            print(f"[Vortex] yt-dlp update: {message}")

    # ------------------------------------------------------------------ #
    # HELPERS
    # ------------------------------------------------------------------ #

    def _get(self, key):
        return self._settings.get_string(key) if self._settings else ""

    def _set(self, key, val):
        if self._settings:
            self._settings.set_string(key, val)

    def _get_bool(self, key):
        return self._settings.get_boolean(key) if self._settings else False

    def _set_bool(self, key, val):
        if self._settings:
            self._settings.set_boolean(key, val)

    def _get_int(self, key):
        return self._settings.get_int(key) if self._settings else 0

    def _set_int(self, key, val):
        if self._settings:
            self._settings.set_int(key, val)

    def get_output_dir(self) -> str:
        path = self._get("download-folder")
        if not path:
            path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD)
        return path

    def get_extra_args(self) -> list:
        args = []
        if self._get_bool("speed-limit-enabled"):
            kbps = self._get_int("speed-limit-kbps")
            args += ["--rate-limit", f"{kbps}K"]
        proxy = self._get("proxy-url")
        if proxy:
            args += ["--proxy", proxy]
        cookie = self._get("cookie-source")
        if cookie and cookie != "none":
            args += ["--cookies-from-browser", cookie]
        retries = self._get_int("retry-count")
        args += ["--retries", str(retries)]
        return args
