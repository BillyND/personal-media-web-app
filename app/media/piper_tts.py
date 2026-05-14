from pathlib import Path

from app.config import Settings
from app.media.commands import run_command


def synthesize_with_piper(text: str, output_wav: Path, settings: Settings) -> None:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    input_txt = output_wav.parent / "input.txt"
    input_txt.write_text(text, encoding="utf-8")
    args = [settings.piper_binary_path, "--model", settings.piper_voice_path, "--output_file", str(output_wav)]
    if settings.piper_config_path:
        args.extend(["--config", settings.piper_config_path])
    run_command(args, input_text=text)
