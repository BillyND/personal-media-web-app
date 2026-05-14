from pathlib import Path

from app.config import Settings


def transcribe_audio(audio_path: Path, transcript_path: Path, settings: Settings) -> None:
    from faster_whisper import WhisperModel

    model = WhisperModel(settings.whisper_model, compute_type=settings.whisper_compute_type)
    segments, _ = model.transcribe(str(audio_path))
    text = "\n".join(segment.text.strip() for segment in segments if segment.text.strip())
    transcript_path.write_text(text, encoding="utf-8")
