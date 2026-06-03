# Vortex

A native GNOME application for downloading videos and music from YouTube, SoundCloud, and 1,800+ other sites — powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Built with GTK4 + libadwaita. Feels like a first-party GNOME app.

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![GNOME](https://img.shields.io/badge/GNOME-50-green)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Python](https://img.shields.io/badge/python-3.11+-yellow)

---

## Features

- Paste any URL — preview title, thumbnail, and duration before downloading
- Video quality picker — Best, 1080p, 720p, 480p, 360p
- Audio-only mode — extract MP3, M4A, FLAC, or Opus with quality control
- Live progress bar with speed, ETA, and cancel button
- Auto-retry with browser cookies for age-restricted and members-only content
- Persistent download history with copy-URL and clear-all
- Settings: download folder, speed limit, proxy, retry count, authentication
- FFmpeg checked at launch with friendly install instructions
- Follows system dark/light mode automatically

---

## Requirements

- Fedora 40+ or any GNOME 46+ Linux distribution
- Python 3.11+
- GTK4 + libadwaita
- FFmpeg
- yt-dlp

---

## Install via Flatpak

Download `Vortex.flatpak` from the [Releases](../../releases) page, then:

```bash
flatpak install Vortex.flatpak
flatpak run org.gnome.Vortex
```

> FFmpeg is required separately: `sudo dnf install ffmpeg` (Fedora) or `sudo apt install ffmpeg` (Ubuntu/Debian)

---

## Install from Source

**1. Install dependencies (Fedora):**

```bash
sudo dnf install python3-gobject python3-gobject-devel gtk4 libadwaita ffmpeg yt-dlp
```

**For Ubuntu/Debian:**

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 ffmpeg
pip install yt-dlp --break-system-packages
```

**2. Clone and run:**

```bash
git clone https://github.com/devkay-48/vortex.git
cd vortex/src && python3 main.py
```

---

## Install Desktop Entry (optional)

To make Vortex appear in GNOME Activities:

```bash
cp data/icons/org.gnome.Vortex.svg ~/.local/share/icons/hicolor/scalable/apps/
update-desktop-database ~/.local/share/applications/
```

---

## Supported Sites

Vortex supports every site yt-dlp supports — YouTube, SoundCloud, Vimeo, Twitter/X, Instagram, TikTok, Twitch, and [1,800+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

## Roadmap

- [ ] Flathub submission
- [ ] Playlist support with item selection
- [ ] Multiple simultaneous downloads
- [ ] In-app yt-dlp updater
- [ ] Subtitle language picker UI
- [ ] Proper app icon

---

## Age-Restricted Content

Vortex automatically retries with your browser cookies when a video requires sign-in. For this to work:

1. **Close Chrome completely** before downloading
2. Or go to **Settings → Authentication** and select your browser manually

---

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the engine behind everything
- [GNOME](https://www.gnome.org/) — HIG and libadwaita
- [FFmpeg](https://ffmpeg.org/) — audio/video processing
