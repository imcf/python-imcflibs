import pytest

from imcflibs.imagej.bdv import ProcessingOptions


def test__process_c1c2_treat_tc_ti():

    acitt_options = (
        "process_angle=[All angles] "
        "process_channel=[Multiple channels (Select from List)] "
        "process_illumination=[All illuminations] "
        "process_tile=[All tiles] "
        "process_timepoint=[All Timepoints] "
    )

    acitt_selectors = "channel_1 channel_2"
    how_to_treat = (
        "how_to_treat_angles=[treat individually] "
        "how_to_treat_channels=group "
        "how_to_treat_illuminations=group "
        "how_to_treat_tiles=compare "
        "how_to_treat_timepoints=[treat individually] "
    )
    use_acitt = "channels=[Average Channels] illuminations=[Average Illuminations] "

    proc_opts = ProcessingOptions()
    proc_opts.process_channel([1, 2])
    proc_opts.treat_timepoints("[treat individually]")

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_use_acitt() == use_acitt
    assert proc_opts.fmt_how_to_treat() == how_to_treat
