import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class FormatPicker(Gtk.Box):
    """
    Video/Audio toggle + quality/format combo rows.
    Call populate(formats) after parse_formats() returns.
    Call get_download_args() to get the yt-dlp args list.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.set_visible(False)
        self._formats = {"video": [], "audio": []}
        self._mode = "video"
        self._build_ui()

    def _build_ui(self):
        clamp = Adw.Clamp(maximum_size=800, tightening_threshold=600)
        self.append(clamp)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_margin_start(16)
        outer.set_margin_end(16)
        outer.set_margin_bottom(8)
        clamp.set_child(outer)

        # Mode toggle
        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        toggle_box.set_halign(Gtk.Align.CENTER)
        toggle_box.add_css_class("linked")
        outer.append(toggle_box)

        self._video_btn = Gtk.ToggleButton(label="Video")
        self._video_btn.set_active(True)
        self._video_btn.add_css_class("pill")
        toggle_box.append(self._video_btn)

        self._audio_btn = Gtk.ToggleButton(label="Audio Only")
        self._audio_btn.set_group(self._video_btn)
        self._audio_btn.add_css_class("pill")
        toggle_box.append(self._audio_btn)

        self._video_btn.connect("toggled", self._on_mode_toggled)

        # Preferences group
        self._group = Adw.PreferencesGroup()
        outer.append(self._group)

        # Video quality row
        self._quality_row = Adw.ComboRow(title="Quality")
        self._group.add(self._quality_row)

        # Audio format row (visible in audio mode only)
        self._audio_fmt_row = Adw.ComboRow(title="Format")
        self._audio_fmt_row.set_visible(False)
        self._group.add(self._audio_fmt_row)

        # Audio quality row
        self._audio_q_row = Adw.ComboRow(title="Audio Quality")
        aq_model = Gtk.StringList.new(["Best (0)", "Standard (5)", "Small (9)"])
        self._audio_q_row.set_model(aq_model)
        self._audio_q_row.set_visible(False)
        self._group.add(self._audio_q_row)

    def _on_mode_toggled(self, btn):
        if self._video_btn.get_active():
            self._mode = "video"
            self._quality_row.set_visible(True)
            self._audio_fmt_row.set_visible(False)
            self._audio_q_row.set_visible(False)
        else:
            self._mode = "audio"
            self._quality_row.set_visible(False)
            self._audio_fmt_row.set_visible(True)
            self._audio_q_row.set_visible(True)

    def populate(self, formats: dict):
        """Load parsed format lists into the combo rows."""
        self._formats = formats

        # Video quality
        video_labels = [f["label"] for f in formats["video"]]
        self._quality_row.set_model(Gtk.StringList.new(video_labels))

        # Audio format
        audio_labels = [f["label"] for f in formats["audio"]]
        self._audio_fmt_row.set_model(Gtk.StringList.new(audio_labels))

        self.set_visible(True)

    def get_download_args(self, output_dir: str = None) -> list:
        """Build and return yt-dlp args based on current picker state."""
        import os
        out = output_dir or os.path.expanduser("~/Downloads")
        template = os.path.join(out, "%(title)s.%(ext)s")

        if self._mode == "video":
            idx = self._quality_row.get_selected()
            fmt = self._formats["video"][idx] if idx < len(self._formats["video"]) else self._formats["video"][0]
            if fmt["format_id"] == "bv*+ba/b":
                f_arg = "bv*+ba/b"
            else:
                h = fmt["height"]
                f_arg = f"bv*[height<={h}]+ba/b[height<={h}]"
            return ["-f", f_arg, "--embed-metadata", "-o", template]

        else:
            # Audio mode
            idx = self._audio_fmt_row.get_selected()
            fmt = self._formats["audio"][idx] if idx < len(self._formats["audio"]) else self._formats["audio"][0]
            ext = fmt.get("ext") or "mp3"
            if ext in ("", "none"):
                ext = "mp3"

            aq_idx = self._audio_q_row.get_selected()
            aq_map = {0: "0", 1: "5", 2: "9"}
            aq = aq_map.get(aq_idx, "0")

            return [
                "-x",
                "--audio-format", ext,
                "--audio-quality", aq,
                "--embed-metadata",
                "--embed-thumbnail",
                "-o", template
            ]

    def reset(self):
        self._video_btn.set_active(True)
        self._formats = {"video": [], "audio": []}
        self.set_visible(False)
