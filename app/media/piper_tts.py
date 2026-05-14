from pathlib import Path

from app.config import Settings
from app.media.commands import run_command


def synthesize_with_piper(
    text: str,
    output_wav: Path,
    settings: Settings,
    model_path: str | None = None,
    config_path: str | None = None,
) -> None:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    model_path = model_path or settings.piper_voice_path
    config_path = config_path or settings.piper_config_path
    _ensure_piper_ready(settings, model_path, config_path)
    input_txt = output_wav.parent / "input.txt"
    input_txt.write_text(text, encoding="utf-8")
    args = [settings.piper_binary_path, "--model", model_path, "--output_file", str(output_wav)]
    if config_path:
        args.extend(["--config", config_path])
    run_command(args, input_text=text, timeout_seconds=settings.command_timeout_seconds)


def _ensure_piper_ready(settings: Settings, model_path: str, config_path: str | None) -> None:
    if not Path(settings.piper_binary_path).is_file():
        raise RuntimeError(f"Piper binary not found: {settings.piper_binary_path}")
    if not Path(model_path).is_file():
        raise RuntimeError(
            "Piper voice model not found: "
            f"{model_path}. Run: runtime/bin/python scripts/install-piper-voice.py"
        )
    if config_path and not Path(config_path).is_file():
        raise RuntimeError(f"Piper voice config not found: {config_path}")
