from pathlib import Path
import shutil

from huggingface_hub import hf_hub_download

VOICE_REPO = "rhasspy/piper-voices"
VOICE_ONNX = "en/en_US/ryan/medium/en_US-ryan-medium.onnx"
VOICE_CONFIG = "en/en_US/ryan/medium/en_US-ryan-medium.onnx.json"
PROJECT_DIR = Path(__file__).resolve().parents[1]
TARGET_DIR = PROJECT_DIR / "data" / "models" / "piper"


def download_voice(filename: str, target_name: str) -> None:
    downloaded = hf_hub_download(repo_id=VOICE_REPO, filename=filename, repo_type="model")
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(downloaded, TARGET_DIR / target_name)


def main() -> None:
    download_voice(VOICE_ONNX, "en_US-ryan-medium.onnx")
    download_voice(VOICE_CONFIG, "en_US-ryan-medium.onnx.json")
    print(f"Piper voice installed in {TARGET_DIR}")


if __name__ == "__main__":
    main()
