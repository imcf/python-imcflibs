"""Tests for the imcflibs.imagej.omerotools module."""

import pytest

from imcflibs.imagej.omerotools import (
    extract_ids_from_string,
    parse_url,
    parse_url_string,
    upload_image_to_omero,
)

# Enusre Python 2.7 and 3.x compability
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def test_upload_image_to_omero():
    """Test `upload_image_to_omero()`.

    Tests only the case for non-existing files.
    """
    path = "/usr/random/path/questionable/file.tiff"
    with pytest.raises(FileNotFoundError, match=r"Could not find file"):
        upload_image_to_omero(None, path, None)


def test_extract_ids_from_string():
    """Test `extract_ids_from_string()`."""

    url_proj = "webclient/?show=project-25406"
    # Expect error with wrong omero_type
    with pytest.raises(ValueError, match=r"Unknown OMERO type"):
        extract_ids_from_string(url_proj, "unicorn")

    assert len(extract_ids_from_string(url_proj, "Project")) == 1
    assert len(extract_ids_from_string(url_proj, "Project-")) == 1
    assert len(extract_ids_from_string(url_proj, "Dataset")) == 0

    url_dataset = "webclient/?show=dataset-82753"
    assert len(extract_ids_from_string(url_dataset, "dataset")) == 1

    url_image = "webclient/?show=image-3598144"
    assert len(extract_ids_from_string(url_image, "image")) == 1

    url_multi_image = (
        "webclient/?show=image-3598144|image-3598145|image-3598146|image-3598147"
    )
    assert len(extract_ids_from_string(url_multi_image, "image-")) == 4
    assert len(extract_ids_from_string(url_multi_image, "Project")) == 0

    url_bad = "https://github.com/imcf/python-imcflibs"
    assert len(extract_ids_from_string(url_bad, "image")) == 0


def test_parse_url_string():
    """Test `parse_url_string()`."""
    url_proj = "webclient/?show=project-25406"
    omero_ids, omero_type = parse_url_string(url_proj)
    assert len(omero_ids) == 1
    assert omero_type == "project"
    assert "25406" in omero_ids

    url_dataset = "webclient/?show=dataset-82753"
    omero_ids, omero_type = parse_url_string(url_dataset)
    assert len(omero_ids) == 1
    assert omero_type == "dataset"
    assert "82753" in omero_ids

    url_image = "webclient/?show=image-3598144"
    omero_ids, omero_type = parse_url_string(url_image)
    assert len(omero_ids) == 1
    assert omero_type == "image"
    assert "3598144" in omero_ids

    url_multi_image = (
        "webclient/?show=image-3598144|image-3598145|image-3598146|image-3598147"
    )
    omero_ids, omero_type = parse_url_string(url_multi_image)
    assert len(omero_ids) == 4
    assert omero_type == "image"
    assert "3598144" in omero_ids
    assert "3598145" in omero_ids
    assert "3598146" in omero_ids
    assert "3598147" in omero_ids

    url_bad = "https://github.com/imcf/python-imcflibs"
    omero_ids, omero_type = parse_url_string(url_bad)
    assert len(omero_ids) == 0
    assert omero_type == ""


def test_parse_url():
    """Test `parse_url()`.

    Only tests the first part of the function
    (NotImplementedError on Project-URLs).
    Since the reset of the function depends on OMERO libraries.
    """
    url_empty = ""
    with pytest.raises(ValueError, match=r"No OMERO link or image ID prov"):
        parse_url(None, url_empty)

    url_proj = "webclient/?show=project-25406"
    with pytest.raises(
        NotImplementedError,
        match=r"Getting Image IDs from Project",
    ):
        parse_url(None, url_proj)
