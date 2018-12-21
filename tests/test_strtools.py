#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os

from imcflibs.strtools import _is_string_like
from imcflibs.strtools import filename
from imcflibs.strtools import flatten
from imcflibs.strtools import strip_prefix

__author__ = "Niko Ehrenfeuchter"
__copyright__ = "Niko Ehrenfeuchter"
__license__ = "gpl3"


def test__is_string_like():
    assert _is_string_like('foo') == True
    assert _is_string_like(12345) == False


def test_filename_from_string():
    assert filename('test_file_name') == 'test_file_name'


def test_filename_from_handle(tmpdir):
    path = str(tmpdir)
    fhandle = tmpdir.join('foo.txt')
    assert filename(fhandle) == os.path.join(path, 'foo.txt')


def test_flatten():
    assert flatten(('foo', 'bar')) == 'foobar'


def test_strip_prefix():
    assert strip_prefix('foobar', 'foo') == 'bar'
    assert strip_prefix('foobar', 'bar') == 'foobar'