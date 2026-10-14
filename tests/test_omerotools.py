"""Tests for the imcflibs.imagej.omerotools module."""

import pytest

from imcflibs.imagej.omerotools import (
    upload_image_to_omero,
)

def test_upload_image_to_omero():
    """Test `upload_image_to_omero()`.

    Tests only the case for non-existing files.
    """
    path = "/usr/random/path/questionable/file.tiff"
    with pytest.raises(FileNotFoundError, match="Could not find file*"):
        upload_image_to_omero(None, path, None)
