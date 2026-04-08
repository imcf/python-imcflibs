"""Tests for `imcflibs.imagej.misc` utility functions."""

import logging

import imcflibs.imagej.misc

from imcflibs.imagej.misc import bytes_to_human_readable
from imcflibs.imagej.misc import save_script_parameters


PASSWORD_ITEMS = ["OMERO_PASSWD"]


class ModuleItem:
    """Mock for the org.scijava.module.ModuleItem interface."""

    def __init__(self, input_name):
        """ModuleItem constructor.

        Parameters
        ----------
        input_name : str
            FIXME: describe (see the ScriptModule class)
        """
        self.input_name = input_name

    def getName(self):
        """Getter method for the "input_name" attribute.

        Returns
        -------
        str
        """
        return self.input_name


class ScriptInfo:
    """Mock for the org.scijava.script.ScriptInfo class."""

    def __init__(self, input_names):
        """ScriptInfo constructor.

        Parameters
        ----------
        input_names : list(str)
            FIXME: describe (see the ScriptModule class)
        """
        self.input_names = [ModuleItem(x) for x in input_names]

    def inputs(self):
        """Get the list of input-objects.

        Returns
        -------
        list(ModuleItem)
        """
        return self.input_names


class ScriptModule:
    """Mock for the org.scijava.script.ScriptModule class."""

    def __init__(self, input_names, inputs):
        """ScriptModule constructor.

        Parameters
        ----------
        input_names : list(str)
            The list of input names. FIXME: explain better.
        inputs : dict
            A dict having the `input_names` as keys. Values are representing the
            content of the respective script parameter.
        """
        self.info = ScriptInfo(input_names)
        self.inputs = inputs

    def getInfo(self):
        """Getter method for the "info" attribute.

        Returns
        -------
        ScriptInfo
        """
        return self.info

    def getInputs(self):
        """Getter method for the "inputs" attribute.

        Returns
        -------
        dict
        """
        return self.inputs


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
