"""Tests for `imcflibs.pathtools`."""
# -*- coding: utf-8 -*-

from imcflibs.pathtools import parse_path
from imcflibs.pathtools import jython_fiji_exists
from imcflibs.pathtools import image_basename
from imcflibs.pathtools import gen_name_from_orig


def test_parse_path():
    """Tests using regular POSIX-style paths."""
    path = "/tmp/foo/"
    path_to_dir = parse_path(path)
    path_to_file = parse_path(path + "file.ext")
    path_to_file_noext = parse_path(path + "file")

    assert path_to_file["orig"] == path + "file.ext"
    assert path_to_file["path"] == path
    assert path_to_file["dname"] == "foo"
    assert path_to_file["fname"] == "file.ext"
    assert path_to_file["ext"] == ".ext"

    assert path_to_file_noext["ext"] == ""
    assert path_to_file_noext["fname"] == "file"
    assert path_to_file_noext["dname"] == "foo"
    assert path_to_file_noext["path"] == path

    assert path_to_dir["path"] == path
    assert path_to_dir["fname"] == ""
    assert path_to_dir["dname"] == "foo"
    assert path_to_dir["ext"] == ""


def test_parse_path_with_prefix():
    """Test parse_path with a prefix parameter."""
    exp_full = "/FOO/BAR/tmp/foo/file.suffix"
    prefix = "/FOO/BAR/"
    path = "/tmp/foo/file.suffix"
    assert parse_path(path, prefix)["full"] == exp_full

    # test again without trailing / leading slashes:
    prefix = "/FOO/BAR"
    path = "tmp/foo/file.suffix"
    assert parse_path(path, prefix)["full"] == exp_full


def test_parse_path_windows():
    """Test using a Windows-style path."""
    path = r"C:\Foo\Bar"
    parsed = parse_path(path)

    assert parsed["orig"] == path
    assert parsed["full"] == "C:/Foo/Bar"
    assert parsed["fname"] == "Bar"
    assert parsed["dname"] == "Foo"


def test_parse_path_windows_newline_tab():
    """Test a Windows path with newline and tab sequences as raw string."""
    path = r"C:\Temp\new\file.ext"
    parsed = parse_path(path)

    assert parsed == {
        "dname": "new",
        "ext": ".ext",
        "fname": "file.ext",
        "full": "C:/Temp/new/file.ext",
        "basename": "file",
        "orig": "C:\\Temp\\new\\file.ext",
        "parent": "C:/Temp",
        "path": "C:/Temp/new/",
    }


def test_parse_path_windows_nonraw():
    r"""Test non-raw string containing newline `\n` and tab `\t` sequences.

    As `parse_path()` cannot work on non-raw strings containing escape
    sequences, the parsed result will not be the expected one.
    """
    path = "C:\new_folder\test"
    parsed = parse_path(path)

    assert parsed["full"] != r"C:\new_folder\test"
    assert parsed["fname"] != "test"


def test_jython_fiji_exists(tmpdir):
    """Test the Jython/Fiji `os.path.exists()` workaround."""
    assert jython_fiji_exists(str(tmpdir)) == True


def test_image_basename():
    """Test basename extraction for various image file names."""
    assert image_basename("/path/to/image_file_01.png") == "image_file_01"
    assert image_basename("more-complex-stack.ome.tif") == "more-complex-stack"
    assert image_basename("/tmp/FoObAr.OMe.tIf") == "FoObAr"


def test_gen_name_from_orig():
    """Test assembling an output name from input, tag and suffix."""
    outpath = "/outpath"
    inpath = "/inpath/to/foobar.tif"
    tag = "-avg"
    suffix = ".h5"
    generated = gen_name_from_orig(outpath, inpath, tag, suffix)
    assert generated == "/outpath/foobar-avg.h5"

