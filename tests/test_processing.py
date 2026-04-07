"""Tests for the imcflibs.imagej.processing module."""

from imcflibs.imagej.processing import rolling_ball_options


def test_rolling_ball_options():
    """Test the rolling_ball_options function."""
    options = rolling_ball_options(42.23)
    assert options == "rolling=42.23"
