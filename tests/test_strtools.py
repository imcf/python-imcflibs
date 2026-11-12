"""Tests for `imcflibs.strtools`."""
# -*- coding: utf-8 -*-

import os

import pytest

from imcflibs.strtools import (
    _is_string_like,
    filename,
    flatten,
    strip_prefix,
    text_in_last_bracket_group,
)


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


def test_text_in_last_bracket_group_basic():
    """Test `text_in_last_bracket_group()` with a single bracket group."""
    assert text_in_last_bracket_group("foo[bar]baz") == "bar"


def test_text_in_last_bracket_group_multiple():
    """Test `text_in_last_bracket_group()` with multiple bracket groups."""
    assert text_in_last_bracket_group("foo[bar]baz[qux]") == "qux"


def test_text_in_last_bracket_group_nested():
    """Test `text_in_last_bracket_group()` with nested bracket groups."""
    assert text_in_last_bracket_group("foo[bar[baz]qux]") == "bar[baz]qux"


def test_text_in_last_bracket_group_empty():
    """Test `text_in_last_bracket_group()` with an empty bracket group."""
    assert text_in_last_bracket_group("foo[]bar") == ""


def test_text_in_last_bracket_group_no_brackets():
    """Test `text_in_last_bracket_group()` with no bracket groups."""
    assert text_in_last_bracket_group("foobar") is None


def test_text_in_last_bracket_group_empty_string():
    """Test `text_in_last_bracket_group()` with an empty string."""
    assert text_in_last_bracket_group("") is None


def test_text_in_last_bracket_group_only_brackets():
    """Test `text_in_last_bracket_group()` with only brackets."""
    assert text_in_last_bracket_group("[foo]") == "foo"


def test_text_in_last_bracket_group_deeply_nested():
    """Test `text_in_last_bracket_group()` with deeply nested brackets."""
    assert text_in_last_bracket_group("foo[bar[baz[qux]]]") == "bar[baz[qux]]"


def test_multi_series_files():
    """Test `text_in_last_bracket_group()` with multiple series files."""
    filename = "ChannelSD - DAPI 20x,SD - GFP 20x,SD - Cy3 20x,SD - Cy5 20x_Seq0002.nd2"
    input = "%s [%s (series 1)]" % (filename, filename)
    expected = "%s (series 1)" % filename
    assert text_in_last_bracket_group(input) == expected
