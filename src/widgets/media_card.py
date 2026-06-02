import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GdkPixbuf, Gio, GLib
import threading
import urllib.request


class MediaCard(Gtk.Box):
    """
    Shows thumbnail, title, uploader, and duration
    after a successful yt-dlp --dump-json call.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.set_visible(False)
        self._build_ui()

    def _build_ui(self):
        clamp = Adw.Clamp(maximum_size=800, tightening_threshold=600)
        self.append(clamp)

        # Card frame
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        card.add_css_class("card")
        card.set_margin_top(0)
        card.set_margin_bottom(8)
        card.set_margin_start(16)
        card.set_margin_end(16)
        card.set_margin_top(8)
        clamp.set_child(card)

        # Thumbnail
        thumb_frame = Gtk.Frame()
        thumb_frame.add_css_class("thumbnail-frame")
        thumb_frame.set_valign(Gtk.Align.CENTER)

        self._thumb = Gtk.Picture()
        self._thumb.set_size_request(160, 90)
        self._thumb.set_content_fit(Gtk.ContentFit.COVER)
        self._thumb.add_css_class("rounded")
        thumb_frame.set_child(self._thumb)
        card.append(thumb_frame)

        # Text info
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info.set_valign(Gtk.Align.CENTER)
        info.set_hexpand(True)
        info.set_margin_top(12)
        info.set_margin_bottom(12)
        card.append(info)

        self._title_label = Gtk.Label(label="")
        self._title_label.set_halign(Gtk.Align.START)
        self._title_label.set_wrap(True)
        self._title_label.set_max_width_chars(60)
        self._title_label.add_css_class("heading")
        info.append(self._title_label)

        self._uploader_label = Gtk.Label(label="")
        self._uploader_label.set_halign(Gtk.Align.START)
        self._uploader_label.add_css_class("dim-label")
        info.append(self._uploader_label)

        self._duration_label = Gtk.Label(label="")
        self._duration_label.set_halign(Gtk.Align.START)
        self._duration_label.add_css_class("dim-label")
        info.append(self._duration_label)

    def populate(self, data: dict):
        """Fill the card with metadata from yt-dlp --dump-json output."""
        title    = data.get("title", "Unknown title")
        uploader = data.get("uploader") or data.get("channel") or "Unknown uploader"
        duration = data.get("duration")
        thumb_url = self._best_thumbnail(data)

        self._title_label.set_label(title)
        self._uploader_label.set_label(uploader)

        if duration:
            mins, secs = divmod(int(duration), 60)
            hrs, mins  = divmod(mins, 60)
            if hrs:
                self._duration_label.set_label(f"{hrs}:{mins:02d}:{secs:02d}")
            else:
                self._duration_label.set_label(f"{mins}:{secs:02d}")
        else:
            self._duration_label.set_label("")

        if thumb_url:
            self._load_thumbnail_async(thumb_url)

        self.set_visible(True)

    def clear(self):
        self._title_label.set_label("")
        self._uploader_label.set_label("")
        self._duration_label.set_label("")
        self._thumb.set_paintable(None)
        self.set_visible(False)

    def _best_thumbnail(self, data: dict) -> str | None:
        thumbs = data.get("thumbnails", [])
        if thumbs:
            # Pick the largest by preference
            for t in reversed(thumbs):
                url = t.get("url", "")
                if url.startswith("http"):
                    return url
        return data.get("thumbnail")

    def _load_thumbnail_async(self, url: str):
        def fetch():
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    data = resp.read()
                GLib.idle_add(self._set_thumbnail_bytes, data)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    def _set_thumbnail_bytes(self, data: bytes):
        try:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pixbuf = loader.get_pixbuf()
            texture = Gdk_texture_from_pixbuf(pixbuf)
            self._thumb.set_paintable(texture)
        except Exception:
            pass
        return False


def Gdk_texture_from_pixbuf(pixbuf):
    from gi.repository import Gdk
    return Gdk.Texture.new_for_pixbuf(pixbuf)
