from pathlib import Path
import unicodedata

from app.config import Settings


PRESET_HINTS = {
    "vieneu:binh": "binh",
    "vieneu:tuyen": "tuyen",
    "vieneu:nguyen": "nguyen",
}


def synthesize_with_vieneu(text: str, output_wav: Path, voice_id: str, settings: Settings) -> None:
    try:
        from vieneu import Vieneu
    except ImportError as error:
        raise RuntimeError("VieNeu is not installed. Run: runtime/bin/python -m pip install vieneu") from error

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    tts = Vieneu(emotion=settings.vieneu_emotion)
    preset_id = find_preset_id(tts.list_preset_voices(), voice_id)
    voice = tts.get_preset_voice(preset_id)
    audio = tts.infer(text=text, voice=voice)
    tts.save(audio, str(output_wav))


def find_preset_id(voices: list[tuple[str, str]], voice_id: str) -> str:
    hint = PRESET_HINTS.get(voice_id, voice_id.split(":")[-1])
    normalized_hint = normalize_text(hint)
    for description, preset_id in voices:
        haystack = normalize_text(f"{description} {preset_id}")
        if normalized_hint in haystack:
            return preset_id
    available = ", ".join(f"{description} ({preset_id})" for description, preset_id in voices)
    raise RuntimeError(f"VieNeu preset not found for {voice_id}. Available presets: {available}")


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
