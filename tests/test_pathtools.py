"""Tests for `imcflibs.pathtools`."""
# -*- coding: utf-8 -*-

import os

from imcflibs.pathtools import (
    derive_out_dir,
    gen_name_from_orig,
    image_basename,
    jython_fiji_exists,
    listdir_matching,
    parse_path,
)


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


def test_derive_out_dir():
    """Test derive_out_dir() using various parameter combinations."""
    assert derive_out_dir("/foo", "-") == "/foo"
    assert derive_out_dir("/foo", "none") == "/foo"
    assert derive_out_dir("/foo", "NONE") == "/foo"
    assert derive_out_dir("/foo", "/bar") == "/bar"


def test_listdir_matching_various(tmpdir):
    """Test non-recursive, recursive, fullpath, regex and sorting behaviour."""
    base = tmpdir.mkdir("base")

    # create mixed files
    base.join("a.TIF").write("x")
    base.join("b.tif").write("x")
    base.join("c.png").write("x")

    # non-recursive, suffix match (case-insensitive)
    res = listdir_matching(str(base), ".tif")
    assert set(res) == {"a.TIF", "b.tif"}

    # fullpath returns absolute paths
    res_full = listdir_matching(str(base), ".tif", fullpath=True)
    assert all(os.path.isabs(x) for x in res_full)

    # recursive with relative paths
    sub = base.mkdir("sub")
    sub.join("s.TIF").write("x")
    res_rec = listdir_matching(str(base), ".tif", recursive=True)
    # should include the file from subdir as a relative path
    assert "sub/" in "/".join(res_rec) or any(p.startswith("sub/") for p in res_rec)

    # regex matching
    res_regex = listdir_matching(str(base), r".*\.tif$", regex=True)
    assert set(res_regex) >= {"a.TIF", "b.tif"}

    # sorting: create names that sort differently lexicographically
    base.join("img2.tif").write("x")
    base.join("img10.tif").write("x")
    base.join("img1.tif").write("x")
    res_sorted = listdir_matching(str(base), ".tif", sort=True)
    # expected alphanumeric order
    assert res_sorted.index("img1.tif") < res_sorted.index("img2.tif")
    assert res_sorted.index("img2.tif") < res_sorted.index("img10.tif")


def test_listdir_matching_invalid_regex(tmpdir):
    """Invalid regular expressions should result in an empty list."""
    base = tmpdir.mkdir("base_invalid_regex")
    base.join("a.tif").write("x")

    # invalid regex should not raise but simply return an empty list
    res = listdir_matching(str(base), "([", regex=True)
    assert res == []


def test_listdir_matching_recursive_regex_fullpath(tmpdir):
    """Recursive search with regex and fullpath should return absolute paths."""
    base = tmpdir.mkdir("base_recursive")
    sub = base.mkdir("subdir")
    sub.join("s.tif").write("x")

    # recursive + regex + fullpath should return absolute path including subdir
    res = listdir_matching(
        str(base), r".*\.tif$", regex=True, recursive=True, fullpath=True
    )
    assert any(os.path.isabs(x) for x in res)
    expected = os.path.join(str(sub), "s.tif")
    assert expected in res
