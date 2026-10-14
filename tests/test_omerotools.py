"""Tests for the imcflibs.imagej.omerotools module."""

import pytest

from imcflibs.imagej.omerotools import (
    extract_ids_from_string,
    upload_image_to_omero,
)

def test_upload_image_to_omero():
    """Test `upload_image_to_omero()`.

    Tests only the case for non-existing files.
    """
    path = "/usr/random/path/questionable/file.tiff"
    with pytest.raises(FileNotFoundError, match="Could not find file*"):
        upload_image_to_omero(None, path, None)


def test_extract_ids_from_string():
    """Test `extract_ids_from_string()`."""

    url_proj = "webclient/?show=project-25406"
    # Expect error with wrong omero_type
    with pytest.raises(ValueError, match="Unknown OMERO type*"):
        extract_ids_from_string(url_proj, "unicorn")

    assert len(extract_ids_from_string(url_proj, "Project")) == 1
    assert len(extract_ids_from_string(url_proj, "Project-")) == 1
    assert len(extract_ids_from_string(url_proj, "Dataset")) == 0

    url_dataset = "webclient/?show=dataset-82753"
    assert len(extract_ids_from_string(url_dataset, "dataset")) == 1

    url_image = "webclient/?show=image-3598144"
    assert len(extract_ids_from_string(url_image, "image")) == 1

    url_multi_image = "webclient/?show=image-3598144|image-3598145|image-3598146|image-3598147"
    assert len(extract_ids_from_string(url_multi_image, "image-")) == 4
    assert len(extract_ids_from_string(url_multi_image, "Project")) == 0

    url_bad = "https://github.com/imcf/python-imcflibs"
    assert len(extract_ids_from_string(url_bad, "image")) == 0
