"""Tests for `imcflibs.strtools`."""
# -*- coding: utf-8 -*-

import pytest
import os

from imcflibs.strtools import _is_string_like
from imcflibs.strtools import filename
from imcflibs.strtools import flatten
from imcflibs.strtools import strip_prefix


def test__is_string_like():
    """Test `_is_string_like()`."""
    assert _is_string_like("foo") == True
    assert _is_string_like(12345) == False


def test_filename_from_string():
    """Test `filename()` using a string."""
    assert filename("test_file_name") == "test_file_name"


def test_filename_from_handle(tmpdir):
    """Test `filename()` using a file handle."""
    path = str(tmpdir)
    fhandle = tmpdir.join("foo.txt")
    assert filename(fhandle) == os.path.join(path, "foo.txt")


def test_flatten():
    """Test `flatten()` using a tuple."""
    assert flatten(("foo", "bar")) == "foobar"


def test_strip_prefix():
    """Test `strip_prefix()`."""
    assert strip_prefix("foobar", "foo") == "bar"
    assert strip_prefix("foobar", "bar") == "foobar"
