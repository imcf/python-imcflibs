import pytest

from imcflibs.imagej.bdv import ProcessingOptions


def test_defaults():
    """Test the default options by calling all fomatters on a "raw" object."""
    acitt_options = (
        "process_angle=[All angles] "
        "process_channel=[All channels] "
        "process_illumination=[All illuminations] "
        "process_tile=[All tiles] "
        "process_timepoint=[All Timepoints] "
    )
    acitt_selectors = " "
    how_to_treat = (
        "how_to_treat_angles=[treat individually] "
        "how_to_treat_channels=group "
        "how_to_treat_illuminations=group "
        "how_to_treat_tiles=group "
        "how_to_treat_timepoints=group "
    )
    use_acitt = (
        "channels=[Average Channels] "
        "illuminations=[Average Illuminations] "
        "tiles=[Average Tiles] "
        "timepoints=[Average Timepoints] "
    )

    proc_opts = ProcessingOptions()

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_how_to_treat() == how_to_treat
    assert proc_opts.fmt_use_acitt() == use_acitt

