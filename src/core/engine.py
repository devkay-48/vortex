import json
import threading
import subprocess
from gi.repository import GLib


def inspect_url(url: str, callback, allow_playlist: bool = False):
    def worker():
        try:
            cmd = ["yt-dlp", "--dump-json"]
            if not allow_playlist:
                cmd.append("--no-playlist")
            cmd.append(url)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout.splitlines()[0])
                GLib.idle_add(callback, data, None)
            else:
                GLib.idle_add(callback, None, result.stderr.strip())
        except subprocess.TimeoutExpired:
            GLib.idle_add(callback, None, "Request timed out. Check your connection.")
        except Exception as e:
            GLib.idle_add(callback, None, str(e))

    threading.Thread(target=worker, daemon=True).start()


class DownloadHandle:
    def __init__(self):
        self._proc = None
        self._cancelled = False

    def _set_proc(self, proc):
        self._proc = proc
        if self._cancelled:
            self._do_cancel()

    def cancel(self):
        self._cancelled = True
        if self._proc:
            self._do_cancel()

    def _do_cancel(self):
        try:
            if self._proc.poll() is None:
                self._proc.terminate()
        except Exception:
            pass


def _run_download(cmd, progress_cb, done_cb, handle):
    from core.parser import parse_progress_line
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        handle._set_proc(proc)
        for line in proc.stdout:
            parsed = parse_progress_line(line)
            if parsed:
                GLib.idle_add(progress_cb, parsed)
        proc.wait()
        stderr = proc.stderr.read()
        if handle._cancelled:
            GLib.idle_add(done_cb, -99, "cancelled")
        else:
            GLib.idle_add(done_cb, proc.returncode, stderr.strip())
    except Exception as e:
        GLib.idle_add(done_cb, -1, str(e))


def start_download(url: str, args: list, progress_cb, done_cb,
                   browser: str = None, allow_playlist: bool = False) -> DownloadHandle:
    handle = DownloadHandle()

    def worker():
        base_cmd = ["yt-dlp", "--progress", "--newline"]
        if not allow_playlist:
            base_cmd.append("--no-playlist")
        base_cmd += args + [url]

        try:
            proc = subprocess.Popen(
                base_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            handle._set_proc(proc)

            from core.parser import parse_progress_line
            for line in proc.stdout:
                parsed = parse_progress_line(line)
                if parsed:
                    GLib.idle_add(progress_cb, parsed)
            proc.wait()
            stderr = proc.stderr.read().strip()

            if handle._cancelled:
                GLib.idle_add(done_cb, -99, "cancelled")
                return

            needs_auth = any(k in stderr.lower() for k in [
                "sign in", "age", "private", "potoken", "members"
            ])

            if proc.returncode != 0 and needs_auth and browser:
                GLib.idle_add(progress_cb, {
                    "percent": 0, "speed": "retrying with cookies…", "eta": "--"
                })
                retry_cmd = ["yt-dlp", "--progress", "--newline"]
                if not allow_playlist:
                    retry_cmd.append("--no-playlist")
                retry_cmd += ["--cookies-from-browser", browser] + args + [url]
                _run_download(retry_cmd, progress_cb, done_cb, handle)
            else:
                GLib.idle_add(done_cb, proc.returncode, stderr)

        except Exception as e:
            GLib.idle_add(done_cb, -1, str(e))

    threading.Thread(target=worker, daemon=True).start()
    return handle


def update_ytdlp(callback):
    """Runs pip install -U yt-dlp in a thread. Fires callback(success, message)."""
    def worker():
        try:
            result = subprocess.run(
                ["pip", "install", "-U", "yt-dlp", "--break-system-packages"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.splitlines() if l.strip()]
                msg = lines[-1] if lines else "yt-dlp updated successfully."
                GLib.idle_add(callback, True, msg)
            else:
                GLib.idle_add(callback, False, result.stderr.strip() or "Update failed.")
        except subprocess.TimeoutExpired:
            GLib.idle_add(callback, False, "Update timed out.")
        except Exception as e:
            GLib.idle_add(callback, False, str(e))

    threading.Thread(target=worker, daemon=True).start()
