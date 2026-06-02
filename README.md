# Vortex

A native GNOME video and music downloader powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Built with GTK4 + libadwaita. Feels like a first-party GNOME app.

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![GNOME](https://img.shields.io/badge/GNOME-46+-green)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Python](https://img.shields.io/badge/python-3.11+-yellow)

---

## Features

- Download video and audio from YouTube and 1,800+ supported sites
- Format picker — choose quality (4K / 1080p / 720p / 480p / 360p)
- Audio extraction — MP3, M4A, FLAC, Opus with quality control
- Playlist support — toggle between single video or full playlist
- Unlimited simultaneous downloads with live progress per item
- Embed metadata and thumbnails into downloaded files
- Subtitle download with language picker
- Browser cookie integration for age-restricted and members-only content
- Persistent download history
- Speed limiter, proxy support, retry control
- In-app yt-dlp updater
- Follows system dark / light mode automatically

---

## Requirements

- Fedora 40+ or any GNOME 46+ Linux distribution
- Python 3.11+
- GTK4 + libadwaita
- FFmpeg
- yt-dlp

---

## Install from Source

**1. Install dependencies:**

```bash
sudo dnf install python3-gobject python3-gobject-devel gtk4 libadwaita ffmpeg yt-dlp
```

For Ubuntu/Debian:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 ffmpeg
pip install yt-dlp --break-system-packages
```

**2. Clone the repo:**

```bash
git clone https://github.com/devkay-48/vortex.git
cd vortex
```

**3. Run:**

```bash
cd src && python3 main.py
```

---

## Install Desktop Entry (optional)

To make Vortex appear in GNOME Activities:

```bash
cat > ~/.local/share/applications/org.gnome.Vortex.desktop << EOF
[Desktop Entry]
Name=Vortex
Comment=Video and music downloader
Exec=python3 /home/$USER/vortex/src/main.py
Icon=org.gnome.Vortex
Terminal=false
Type=Application
Categories=Network;FileTransfer;
EOF

cp data/icons/org.gnome.Vortex.svg ~/.local/share/icons/hicolor/scalable/apps/
update-desktop-database ~/.local/share/applications/
```

---

## Supported Sites

Vortex supports every site yt-dlp supports — including YouTube, SoundCloud, Vimeo, Twitter/X, Instagram, TikTok, Twitch, and [1,800+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

## Roadmap

- [ ] Flatpak release on Flathub
- [ ] Playlist management UI
- [ ] Download scheduling
- [ ] Thumbnail preview in download queue

---

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the engine behind everything
- [GNOME](https://www.gnome.org/) — HIG and libadwaita
- [FFmpeg](https://ffmpeg.org/) — audio/video processing
