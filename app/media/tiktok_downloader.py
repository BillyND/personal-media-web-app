from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

ALLOWED_HOSTS = {"tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"}


def validate_tiktok_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must use http or https")
    host = parsed.netloc.lower()
    if host not in ALLOWED_HOSTS and not host.endswith(".tiktok.com"):
        raise ValueError("Only TikTok URLs are supported")
    return url.strip()


def download_tiktok_video(url: str, output_dir: Path, max_duration_seconds: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "video.%(ext)s")
    options = {
        "outtmpl": output_template,
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=False)
        duration = info.get("duration") if info else None
        if duration and duration > max_duration_seconds:
            raise ValueError("Video is longer than configured limit")
        downloader.download([url])
    mp4 = output_dir / "video.mp4"
    if mp4.exists():
        return mp4
    candidates = list(output_dir.glob("video.*"))
    if not candidates:
        raise RuntimeError("Video download did not produce a file")
    return candidates[0]
