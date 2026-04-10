"""Tests for `imcflibs.imagej.misc` utility functions."""

import logging

from org.scijava.script import ScriptInfo, ScriptModule

import imcflibs.imagej.misc

from imcflibs.imagej.misc import bytes_to_human_readable
from imcflibs.imagej.misc import save_script_parameters


PASSWORD_ITEMS = ["OMERO_PASSWD"]


def test_save_script_parameters_fail(caplog):
    """Tests save_script_parameters with an invalid script_globals object."""
    caplog.clear()

    save_script_parameters(script_globals=None, destination="")
    assert "ScriptModule inspection failed" in caplog.messages[0]


def test_save_script_parameters(tmp_path, monkeypatch, caplog):
    """Tests save_script_parameters."""
    caplog.set_level(logging.DEBUG)
    caplog.clear()

    base = tmp_path / "saved_parameters"
    base.mkdir()

    def _is_password_style(item):
        return item.getName() in PASSWORD_ITEMS

    monkeypatch.setattr(imcflibs.imagej.misc, "_is_password_style", _is_password_style)

    script_module = ScriptModule(
        input_names=["AAA", "BBB", "OMERO_PASSWD", "SJLOG", "NOT_THERE"],
        inputs={"AAA": "aaa", "BBB": "bbb", "OMERO_PASSWD": "ultra-secret"},
    )
    script_globals = {"org.scijava.script.ScriptModule": script_module}
    save_script_parameters(script_globals, destination=base)
    assert "Skipping parameter from skip-list" in caplog.text
    assert "Skipping password-style parameter" in caplog.text
    assert "Unable to fetch value for parameter: NOT_THERE" in caplog.text
    assert "Saved 2 parameters (skipped 1 password-style and 1 others)." in caplog.text
    assert "Saved 2 script parameters to" in caplog.text

    with open(str(base) + "/script_parameters.txt", "r") as f:
        contents = f.read()
    assert contents == "AAA: aaa\nBBB: bbb\n"


def test_bytes_to_human_readable_simple():
    """Ensure common sizes are formatted into human-readable strings."""
    assert bytes_to_human_readable(500) == "500.0 bytes"
    assert bytes_to_human_readable(2048) == "2.0 KB"
    assert bytes_to_human_readable(1024 * 1024) == "1.0 MB"
    assert bytes_to_human_readable(5 * 1024**3) == "5.0 GB"


def test_bytes_to_human_readable_large():
    """Verify formatting for large sizes such as terabytes."""
    # 1.5 TB in bytes should format as 1.5 TB
    size = int(1.5 * (1024**4))
    assert bytes_to_human_readable(size) == "1.5 TB"
