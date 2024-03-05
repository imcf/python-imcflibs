#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from imcflibs.pathtools import parse_path
from imcflibs.pathtools import jython_fiji_exists
from imcflibs.pathtools import image_basename

__author__ = "Niko Ehrenfeuchter"
__copyright__ = "Niko Ehrenfeuchter"
__license__ = "gpl3"


def test_parse_path():
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


def test_parse_path_windows():
    path = r"C:\foo\bar"
    parsed = parse_path(path)

    assert parsed["orig"] == path
    assert parsed["full"] == r"C:/foo/bar"
    assert parsed["fname"] == "bar"
    assert parsed["dname"] == "foo"


def test_jython_fiji_exists(tmpdir):
    assert jython_fiji_exists(str(tmpdir)) == True


def test_image_basename():
    assert image_basename("/path/to/image_file_01.png") == "image_file_01"
    assert image_basename("more-complex-stack.ome.tif") == "more-complex-stack"
    assert image_basename("/tmp/FoObAr.OMe.tIf") == "FoObAr"
