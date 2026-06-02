"""
Central error map: yt-dlp stderr fragments → human-readable messages.
"""

ERROR_MAP = {
    "Private video":               "This video is private.",
    "Sign in to confirm your age": "Age-restricted — enable cookies in Settings.",
    "members-only":                "Members-only content — enable cookies in Settings.",
    "Errno -3":                    "No internet connection. Check your network.",
    "Errno -2":                    "No internet connection. Check your network.",
    "ffmpeg not found":            "FFmpeg is missing: sudo dnf install ffmpeg",
    "ffprobe not found":           "FFmpeg is missing: sudo dnf install ffmpeg",
    "Unable to extract":           "URL not supported or the video was removed.",
    "PoToken":                     "YouTube auth required — enable Firefox cookies in Settings.",
    "HTTP Error 403":              "Access forbidden. Try enabling browser cookies in Settings.",
    "HTTP Error 404":              "Video not found — it may have been deleted.",
    "HTTP Error 429":              "Too many requests — wait a moment and try again.",
    "This video is not available": "This video is unavailable in your region.",
    "Video unavailable":           "This video is unavailable.",
    "No video formats found":      "No downloadable formats found for this URL.",
    "Unsupported URL":             "This URL is not supported by yt-dlp.",
    "timed out":                   "Connection timed out. Check your network.",
}


def map_error(stderr: str) -> str:
    """Match stderr against known error fragments, return friendly message."""
    if not stderr:
        return "Unknown error."
    for fragment, message in ERROR_MAP.items():
        if fragment.lower() in stderr.lower():
            return message
    # Fallback: return first 120 chars of stderr
    return stderr[:120]
