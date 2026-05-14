from pathlib import Path

from app.config import Settings
from app.media.commands import run_command


def synthesize_with_piper(text: str, output_wav: Path, settings: Settings) -> None:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    _ensure_piper_ready(settings)
    input_txt = output_wav.parent / "input.txt"
    input_txt.write_text(text, encoding="utf-8")
    args = [settings.piper_binary_path, "--model", settings.piper_voice_path, "--output_file", str(output_wav)]
    if settings.piper_config_path:
        args.extend(["--config", settings.piper_config_path])
    run_command(args, input_text=text, timeout_seconds=settings.command_timeout_seconds)


def _ensure_piper_ready(settings: Settings) -> None:
    if not Path(settings.piper_binary_path).is_file():
        raise RuntimeError(f"Piper binary not found: {settings.piper_binary_path}")
    if not Path(settings.piper_voice_path).is_file():
        raise RuntimeError(
            "Piper voice model not found: "
            f"{settings.piper_voice_path}. Run: runtime/bin/python scripts/install-piper-voice.py"
        )
    if settings.piper_config_path and not Path(settings.piper_config_path).is_file():
        raise RuntimeError(f"Piper voice config not found: {settings.piper_config_path}")
