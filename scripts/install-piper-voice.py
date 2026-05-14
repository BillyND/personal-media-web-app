from pathlib import Path
import shutil

from huggingface_hub import hf_hub_download

VOICE_REPO = "rhasspy/piper-voices"
PROJECT_DIR = Path(__file__).resolve().parents[1]
TARGET_DIR = PROJECT_DIR / "data" / "models" / "piper"
VOICES = [
    (
        "en/en_US/ryan/medium/en_US-ryan-medium.onnx",
        "en_US-ryan-medium.onnx",
    ),
    (
        "en/en_US/ryan/medium/en_US-ryan-medium.onnx.json",
        "en_US-ryan-medium.onnx.json",
    ),
    (
        "vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx",
        "vi_VN-vais1000-medium.onnx",
    ),
    (
        "vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx.json",
        "vi_VN-vais1000-medium.onnx.json",
    ),
]


def download_voice(filename: str, target_name: str) -> None:
    downloaded = hf_hub_download(repo_id=VOICE_REPO, filename=filename, repo_type="model")
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded, TARGET_DIR / target_name)


def main() -> None:
    for filename, target_name in VOICES:
        download_voice(filename, target_name)
    print(f"Piper voices installed in {TARGET_DIR}")


if __name__ == "__main__":
    main()
