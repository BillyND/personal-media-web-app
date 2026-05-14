from pathlib import Path

import pytest

from app.db.connection import resolve_safe_path


def test_resolve_safe_path_rejects_traversal(tmp_path):
    outside = Path(tmp_path).parent / "outside.txt"
    with pytest.raises(ValueError):
        resolve_safe_path(tmp_path, str(outside))
