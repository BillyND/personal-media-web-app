from pathlib import Path

from app.media.commands import run_command


def convert_wav_to_mp3(input_wav: Path, output_mp3: Path) -> None:
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    run_command(["ffmpeg", "-y", "-i", str(input_wav), "-vn", "-codec:a", "libmp3lame", str(output_mp3)])


def extract_mp3(input_video: Path, output_mp3: Path) -> None:
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    run_command(["ffmpeg", "-y", "-i", str(input_video), "-vn", "-codec:a", "libmp3lame", str(output_mp3)])
