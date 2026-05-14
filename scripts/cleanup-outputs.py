from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import shutil


def main() -> None:
    output_dir = Path(os.getenv("OUTPUT_DIR", "./data/outputs")).resolve()
    seconds = int(os.getenv("AUTO_DELETE_SECONDS", os.getenv("AUTO_DELETE_DAYS", "30")))
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=seconds)
    if not output_dir.exists():
        return
    for child in output_dir.iterdir():
        if not child.is_dir():
            continue
        modified = datetime.fromtimestamp(child.stat().st_mtime, timezone.utc)
        if modified < cutoff:
            shutil.rmtree(child)


if __name__ == "__main__":
    main()
