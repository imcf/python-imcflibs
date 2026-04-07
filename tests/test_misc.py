"""Tests for `imcflibs.imagej.misc` utility functions."""

from imcflibs.imagej.misc import bytes_to_human_readable
from imcflibs.imagej.misc import save_script_parameters


class ModuleItem:
    """Mock for the org.scijava.module.ModuleItem interface."""

    def __init__(self, input_name):
        self.input_name = input_name

    def getName(self):
        return self.input_name


class ScriptInfo:
    """Mock for the org.scijava.script.ScriptInfo class."""

    def __init__(self, input_names):
        self.input_names = [ModuleItem(x) for x in input_names]

    def inputs(self):
        return self.input_names


class ScriptModule:
    """Mock for the org.scijava.script.ScriptModule class."""

    def __init__(self, input_names, inputs):
        self.info = ScriptInfo(input_names)
        self.inputs = inputs

    def getInfo(self):
        return self.info

    def getInputs(self):
        return self.inputs


# FIXME: probably better use monkeypatch instead of mocker for more flexibility
# in modifying the return value depending on the ScriptModule contents
def test_save_script_parameters(tmpdir, mocker):
    """Tests for imcflibs.imagej.misc.save_script_parameters."""
    base = tmpdir.mkdir("base")
    m_is_password_style = mocker.patch("imcflibs.imagej.misc._is_password_style")
    m_is_password_style.return_value = False

    script_module = ScriptModule(["AAA", "BBB"], {"AAA": "aaa", "BBB": "bbb"})
    script_globals = {"org.scijava.script.ScriptModule": script_module}
    save_script_parameters(script_globals, destination=base)
    with open(base / "script_parameters.txt", "r") as f:
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
