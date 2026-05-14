import pytest

from app.media.tiktok_downloader import validate_tiktok_url


def test_accepts_tiktok_url():
    assert validate_tiktok_url("https://www.tiktok.com/@user/video/123")


def test_rejects_non_tiktok_url():
    with pytest.raises(ValueError):
        validate_tiktok_url("https://example.com/video")
