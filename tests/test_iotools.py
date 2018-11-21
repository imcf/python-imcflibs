#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import zipfile

from os.path import join

from imcflibs.iotools import filehandle
from imcflibs.iotools import readtxt

__author__ = "Niko Ehrenfeuchter"
__copyright__ = "Niko Ehrenfeuchter"
__license__ = "gpl3"


def test_filehandle(tmpdir):
    tmpfile = tmpdir.join('testfile')
    tmpname = str(tmpfile)
    tmphandle = open(str(tmpfile), 'w')
    print(type(tmphandle))
    assert type(tmpname) is str
    assert type(tmphandle) is file
    assert type(filehandle(tmpname)) is file
    assert type(filehandle(tmphandle, 'w')) is file


def test_readtxt(tmpdir):
    content = [
        u'lorem\n',
        u'ipsum\n',
        u'and some more\n',
        u'dummy text\n',
    ]
    fh = tmpdir.mkdir("readtxt").join("content.txt")
    fh.write(u''.join(content))
    print(fh.basename)
    print(fh.dirname)
    with zipfile.ZipFile(join(fh.dirname, 'archive.zip'), 'w') as zf:
        zf.write(str(fh), arcname='content.txt')
        print("wrote [%s] into [%s]" % (str(fh), zf.filename))
    
    print(content)
    fromfile = readtxt(str(fh))
    print(fromfile)
    assert fromfile == content

    fromfile_flat = readtxt(str(fh), flat=True)
    assert fromfile_flat == ''.join(content)

    print(join(fh.dirname, 'archive.zip'))
    fromzip = readtxt('content.txt', join(fh.dirname, 'archive.zip'))
    print(fromzip)
    assert fromzip == content

    fromzip_flat = readtxt('content.txt', join(fh.dirname, 'archive.zip'), flat=True)
    assert fromzip_flat == ''.join(content)
