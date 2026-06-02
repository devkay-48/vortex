import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk


class UrlBar(Gtk.Box):
    """
    Smart URL entry bar.
    Emits 'url-submitted' signal with the URL string when user hits Enter or clicks Inspect.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Outer card
        clamp = Adw.Clamp(maximum_size=800, tightening_threshold=600)
        self.append(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(8)
        box.set_margin_start(16)
        box.set_margin_end(16)
        clamp.set_child(box)

        # Entry row inside a preferences group
        group = Adw.PreferencesGroup()
        box.append(group)

        self._entry = Adw.EntryRow(title="Paste a YouTube, SoundCloud, or any URL…")
        self._entry.set_show_apply_button(True)
        self._entry.connect("apply", self._on_apply)
        self._entry.connect("entry-activated", self._on_activated)
        group.add(self._entry)

        # Paste button suffix
        paste_btn = Gtk.Button(icon_name="edit-paste-symbolic")
        paste_btn.set_tooltip_text("Paste from clipboard")
        paste_btn.add_css_class("flat")
        paste_btn.set_valign(Gtk.Align.CENTER)
        paste_btn.connect("clicked", self._on_paste)
        self._entry.add_suffix(paste_btn)

        # Spinner suffix (hidden until loading)
        self._spinner = Gtk.Spinner()
        self._spinner.set_valign(Gtk.Align.CENTER)
        self._spinner.set_visible(False)
        self._entry.add_suffix(self._spinner)

    def _on_apply(self, entry):
        self._submit()

    def _on_activated(self, entry):
        self._submit()

    def _on_paste(self, btn):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.read_text_async(None, self._on_clipboard_text, None)

    def _on_clipboard_text(self, clipboard, result, _user_data):
        try:
            text = clipboard.read_text_finish(result)
            if text:
                self._entry.set_text(text.strip())
                self._submit()
        except Exception:
            pass

    def _submit(self):
        url = self._entry.get_text().strip()
        if url:
            self.set_loading(True)
            # Emit via GLib so parent can connect normally
            GLib.idle_add(self._fire_signal, url)

    def _fire_signal(self, url):
        self.emit_url(url)
        return False

    def emit_url(self, url: str):
        """Override or monkey-patch this in the parent page to handle the URL."""
        pass

    def set_loading(self, loading: bool):
        self._spinner.set_visible(loading)
        if loading:
            self._spinner.start()
        else:
            self._spinner.stop()
        self._entry.set_sensitive(not loading)

    def clear(self):
        self._entry.set_text("")
        self.set_loading(False)
