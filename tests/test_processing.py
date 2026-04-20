"""Tests for the imcflibs.imagej.processing module."""

from imcflibs.imagej.processing import (
    filter_options,
    rolling_ball_options,
    threshold_options,
)


def test_rolling_ball_options():
    """Test the rolling_ball_options function."""

    options = rolling_ball_options(42.23)
    assert options == "rolling=42.23"


def test_rolling_ball_options_with_flags():
    """Test `rolling_ball_options()` string concatenation with all flags."""

    options = rolling_ball_options(
        12,
        light_background=True,
        sliding=True,
        disable_smoothing=True,
        do_3d=True,
    )
    assert options == "rolling=12 light sliding disable stack"


def test_filter_options():
    """Test `filter_options()` string concatenation."""

    command, options = filter_options("Mean", 5, do_3d=True)
    assert command == "Mean 3D..."
    assert options == "radius=5 stack"


def test_filter_options_gaussian_blur():
    """Test `filter_options()` with the Gaussian Blur branch."""

    command, options = filter_options("Gaussian Blur", 5)
    assert command == "Gaussian Blur..."
    assert options == "sigma=5 stack"


def test_threshold_options():
    """Test `threshold_options()` string concatenation."""

    auto_threshold, convert_to_binary = threshold_options("Otsu", do_3d=True)
    assert auto_threshold == "Otsu dark stack"
    assert convert_to_binary == "method=Otsu background=Dark black"


def test_threshold_options_without_stack():
    """Test `threshold_options()` when 3D stacking is disabled."""

    auto_threshold, convert_to_binary = threshold_options("Otsu", do_3d=False)
    assert auto_threshold == ""
    assert convert_to_binary == "method=Otsu background=Dark black"
