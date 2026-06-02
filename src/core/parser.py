import re

PROGRESS_RE = re.compile(
    r'\[download\]\s+([0-9.]+)%\s+of\s+~?\s*([0-9.]+)(KiB|MiB|GiB)'
    r'\s+at\s+([0-9.]+)(KiB/s|MiB/s|GiB/s)\s+ETA\s+([0-9:]+)'
)


def parse_progress_line(line: str) -> dict | None:
    m = PROGRESS_RE.search(line)
    if not m:
        return None
    return {
        "percent": float(m.group(1)),
        "total":   f"{m.group(2)} {m.group(3)}",
        "speed":   f"{m.group(4)} {m.group(5)}",
        "eta":     m.group(6),
    }


def parse_formats(data: dict) -> dict:
    formats = data.get("formats", [])
    video_seen = set()
    audio_seen = set()
    video_list = []
    audio_list = []

    for f in reversed(formats):
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        height = f.get("height")
        ext    = f.get("ext", "?")
        fsize  = f.get("filesize") or f.get("filesize_approx")
        size_str = _human_size(fsize) if fsize else "? MB"

        if vcodec != "none" and height:
            key = height
            if key not in video_seen:
                video_seen.add(key)
                label = f"{height}p — {ext.upper()}  (~{size_str})"
                video_list.append({
                    "label":  label,
                    "height": height,
                    "ext":    ext,
                    "format_id": f.get("format_id", ""),
                })
        elif vcodec == "none" and acodec != "none":
            abr = f.get("abr")
            key = (ext, int(abr) if abr else 0)
            if key not in audio_seen:
                audio_seen.add(key)
                abr_str = f"{int(abr)}kbps" if abr else ""
                label = f"{ext.upper()}  {abr_str}  (~{size_str})"
                audio_list.append({
                    "label": label,
                    "ext":   ext,
                    "abr":   abr,
                    "format_id": f.get("format_id", ""),
                })

    video_list.sort(key=lambda x: x["height"], reverse=True)
    audio_list.sort(key=lambda x: x.get("abr") or 0, reverse=True)

    video_list.insert(0, {"label": "Best available", "height": None, "ext": "", "format_id": "bv*+ba/b"})
    audio_list.insert(0, {"label": "Best available", "ext": "", "abr": None, "format_id": "ba/b"})

    return {"video": video_list, "audio": audio_list}


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.0f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.0f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"
