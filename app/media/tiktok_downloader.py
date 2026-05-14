from pathlib import Path
import sys
from urllib.parse import urlparse

from app.media.commands import run_command

ALLOWED_HOSTS = {"tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"}


def validate_tiktok_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use http or https")
    host = parsed.netloc.lower()
    if host not in ALLOWED_HOSTS and not host.endswith(".tiktok.com"):
        raise ValueError("Only TikTok URLs are supported")
    return url.strip()


def download_tiktok_video(
    url: str,
    output_dir: Path,
    max_duration_seconds: int,
    max_download_bytes: int,
    timeout_seconds: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "video.%(ext)s")
    run_command(
        [
            sys.executable,
            "-m",
            "yt_dlp",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--format",
            "bv*+ba/best",
            "--merge-output-format",
            "mp4",
            "--socket-timeout",
            str(timeout_seconds),
            "--retries",
            "2",
            "--fragment-retries",
            "2",
            "--max-filesize",
            str(max_download_bytes),
            "--match-filter",
            f"duration <= {max_duration_seconds}",
            "-o",
            output_template,
            url,
        ],
        timeout_seconds=timeout_seconds,
    )
    video_path = _find_downloaded_video(output_dir)
    if video_path.stat().st_size > max_download_bytes:
        video_path.unlink(missing_ok=True)
        raise ValueError("Downloaded video exceeds configured size limit")
    return video_path


def _find_downloaded_video(output_dir: Path) -> Path:
    mp4 = output_dir / "video.mp4"
    if mp4.exists():
        return mp4
    candidates = list(output_dir.glob("video.*"))
    if not candidates:
        raise RuntimeError("Video download did not produce a file")
    return candidates[0]
