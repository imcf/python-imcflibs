"""Tests for the imcflibs.imagej.objects3d module."""

from imcflibs.imagej.objects3d import imgplus_to_population3d
from imcflibs.imagej.objects3d import maxima_finder_3d
from imcflibs.imagej.objects3d import population3d_to_imgplus
from imcflibs.imagej.objects3d import seeded_watershed
from imcflibs.imagej.objects3d import segment_3d_image


def test_mock_imports():
    """Test if the mock imports work fine."""
    assert True
