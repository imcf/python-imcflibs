"""Tests for `imcflibs.imagej.misc` utility functions."""

from imcflibs.imagej.misc import bytes_to_human_readable


def test_bytes_to_human_readable_simple():
    assert bytes_to_human_readable(500) == "500.0 bytes"
    assert bytes_to_human_readable(2048) == "2.0 KB"
    assert bytes_to_human_readable(1024 * 1024) == "1.0 MB"
    assert bytes_to_human_readable(5 * 1024**3) == "5.0 GB"


def test_bytes_to_human_readable_large():
    # 1.5 TB in bytes should format as 1.5 TB
    size = int(1.5 * (1024**4))
    assert bytes_to_human_readable(size) == "1.5 TB"
