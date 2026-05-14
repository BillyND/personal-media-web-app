import json
from pathlib import Path

from app.config import Settings, get_settings
from app.jobs.models import JOB_TIKTOK, JOB_TTS, Job
from app.jobs.repository import JobRepository
from app.media.audio_converter import convert_wav_to_mp3, extract_mp3
from app.media.piper_tts import synthesize_with_piper
from app.media.tiktok_downloader import download_tiktok_video, validate_tiktok_url
from app.media.transcriber import transcribe_audio


def process_job(job: Job, repository: JobRepository, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if job.type == JOB_TIKTOK:
        process_tiktok_job(job, repository, settings)
        return
    if job.type == JOB_TTS:
        process_tts_job(job, repository, settings)
        return
    raise ValueError(f"Unsupported job type: {job.type}")


def process_tiktok_job(job: Job, repository: JobRepository, settings: Settings) -> None:
    if not job.input_url:
        raise ValueError("TikTok URL is required")
    output_dir = Path(job.output_dir)
    url = validate_tiktok_url(job.input_url)
    video_path = download_tiktok_video(
        url,
        output_dir,
        settings.max_video_duration_seconds,
        settings.max_download_bytes,
        settings.command_timeout_seconds,
    )
    audio_path = output_dir / "audio.mp3"
    transcript_path = output_dir / "transcript.txt"
    metadata_path = output_dir / "metadata.json"

    extract_mp3(video_path, audio_path, settings.command_timeout_seconds)
    transcribe_audio(audio_path, transcript_path, settings)
    metadata_path.write_text(json.dumps({"type": "tiktok", "source_url": url}, indent=2), encoding="utf-8")

    repository.add_file(job.id, "video", video_path)
    repository.add_file(job.id, "audio", audio_path)
    repository.add_file(job.id, "transcript", transcript_path)
    repository.add_file(job.id, "metadata", metadata_path)


def process_tts_job(job: Job, repository: JobRepository, settings: Settings) -> None:
    text, voice_id = parse_tts_payload(job.input_text)
    voice = settings.get_tts_voice(voice_id)
    if not text:
        raise ValueError("Text is required")
    if len(text) > settings.max_tts_text_length:
        raise ValueError("Text exceeds configured length limit")

    output_dir = Path(job.output_dir)
    input_path = output_dir / "input.txt"
    wav_path = output_dir / "audio.wav"
    mp3_path = output_dir / "audio.mp3"
    metadata_path = output_dir / "metadata.json"

    input_path.write_text(text, encoding="utf-8")
    synthesize_with_piper(text, wav_path, settings, voice.model_path, voice.config_path)
    convert_wav_to_mp3(wav_path, mp3_path, settings.command_timeout_seconds)
    metadata_path.write_text(
        json.dumps(
            {
                "type": "tts",
                "voice_id": voice.id,
                "voice": voice.label,
                "language": voice.language,
                "text_length": len(text),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    repository.add_file(job.id, "input", input_path)
    repository.add_file(job.id, "audio", mp3_path)
    repository.add_file(job.id, "metadata", metadata_path)


def parse_tts_payload(input_text: str | None) -> tuple[str, str | None]:
    raw = (input_text or "").strip()
    if not raw:
        return "", None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw, None
    if not isinstance(payload, dict):
        return raw, None
    return str(payload.get("text", "")).strip(), payload.get("voice_id")
