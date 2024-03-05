#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import zipfile

from os.path import join

import io

from imcflibs.iotools import filehandle
from imcflibs.iotools import readtxt

try:
    # Python 2: "file" is built-in
    file_types = file, io.IOBase
except NameError:
    # Python 3: "file" fully replaced with IOBase
    file_types = (io.IOBase,)


__author__ = "Niko Ehrenfeuchter"
__copyright__ = "Niko Ehrenfeuchter"
__license__ = "gpl3"


def test_filehandle(tmpdir):
    tmpfile = tmpdir.join("testfile")
    tmpname = str(tmpfile)
    # print(tmpname)
    tmphandle = open(str(tmpfile), "w")
    print(type(tmphandle))
    assert isinstance(tmpname, str)
    print("tmpname is str-like 🦋")
    assert isinstance(tmphandle, file_types)
    print("tmphandle is file/io-like 🦋")
    assert isinstance(filehandle(tmpname), file_types)
    print("filehandle(tmpname) is file/io-like 🦋")
    assert isinstance(filehandle(tmphandle, "w"), file_types)
    print("filehandle(tmphandle) is file/io-like 🦋")


def test_readtxt(tmpdir):
    content = [
        "lorem\n",
        "ipsum\n",
        "and some more\n",
        "dummy text\n",
    ]
    fh = tmpdir.mkdir("readtxt").join("content.txt")
    fh.write("".join(content))
    print(fh.basename)
    print(fh.dirname)
    with zipfile.ZipFile(join(fh.dirname, "archive.zip"), "w") as zf:
        zf.write(str(fh), arcname="content.txt")
        print("wrote [%s] into [%s]" % (str(fh), zf.filename))

    print(content)
    fromfile = readtxt(str(fh))
    print(fromfile)
    assert fromfile == content

    fromfile_flat = readtxt(str(fh), flat=True)
    assert fromfile_flat == "".join(content)

    print(join(fh.dirname, "archive.zip"))
    fromzip = readtxt("content.txt", join(fh.dirname, "archive.zip"))
    print(fromzip)
    assert fromzip == content

    fromzip_flat = readtxt("content.txt", join(fh.dirname, "archive.zip"), flat=True)
    assert fromzip_flat == "".join(content)
