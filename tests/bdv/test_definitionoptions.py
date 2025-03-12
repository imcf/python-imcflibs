import pytest
from imcflibs.imagej.bdv import DefinitionOptions


def test_defaults():
    """Test the default options by calling all formatters on a "raw" objects."""
    acitt_options = (
        "multiple_angles=[NO (one angle)] "
        "multiple_channels=[YES (all channels in one file)] "
        "multiple_illuminations_directions=[NO (one illumination direction)] "
        "multiple_tiles=[YES (one file per tile)] "
        "multiple_timepoints=[NO (one time-point)] "
    )

    def_opts = DefinitionOptions()

    assert def_opts.fmt_acitt_options() == acitt_options


def test__definition_option():
    """Test an example with wrong setting for definition option."""

    test_value = "Multiple"

    def_opts = DefinitionOptions()
    with pytest.raises(ValueError) as excinfo:
        def_opts.set_angle_definition(test_value)
    assert (
        str(excinfo.value) == "Value must be one of single, multi_multi or multi_single"
    )


def test__multiple_timepoints_files():
    """Test an example setting how to treat multiple time-points."""

    acitt_options = (
        "multiple_angles=[NO (one angle)] "
        "multiple_channels=[YES (all channels in one file)] "
        "multiple_illuminations_directions=[NO (one illumination direction)] "
        "multiple_tiles=[YES (one file per tile)] "
        "multiple_timepoints=[YES (one file per time-point)] "
    )

    def_opts = DefinitionOptions()
    def_opts.set_timepoint_definition("multi_multi")

    assert def_opts.fmt_acitt_options() == acitt_options


def test__multiple_channels_files_multiple_timepoints():
    """Test an example setting how to treat multiple channels and multiple time-points."""

    acitt_options = (
        "multiple_angles=[NO (one angle)] "
        "multiple_channels=[YES (one file per channel)] "
        "multiple_illuminations_directions=[NO (one illumination direction)] "
        "multiple_tiles=[YES (one file per tile)] "
        "multiple_timepoints=[YES (all time-points in one file)] "
    )

    def_opts = DefinitionOptions()
    def_opts.set_channel_definition("multi_multi")
    def_opts.set_timepoint_definition("multi_single")

    assert def_opts.fmt_acitt_options() == acitt_options


def test_single_tile_multiple_angles_files():
    """Test an example setting how to treat single tile and multiple angle
    files"""

    acitt_options = (
        "multiple_angles=[YES (one file per angle)] "
        "multiple_channels=[YES (all channels in one file)] "
        "multiple_illuminations_directions=[NO (one illumination direction)] "
        "multiple_tiles=[NO (one tile)] "
        "multiple_timepoints=[NO (one time-point)] "
    )

    def_opts = DefinitionOptions()
    def_opts.set_angle_definition("multi_multi")
    def_opts.set_tile_definition("single")

    assert def_opts.fmt_acitt_options() == acitt_options
