import logging

from imcflibs import pathtools
from imcflibs.imagej import bdv

def set_default_values(project_filename, file_path):
    """Set the default values for dataset definitions.

    Parameters
    ----------
    project_filename : str
        Name of the project
    file_path : pathlib.Path
        Path to a temporary folder

    Returns
    ----------
    str
        Start of the options for dataset definitions.
    """
       # Additional settings
    file_info = pathtools.parse_path(file_path)

    options = (
        "define_dataset=[Automatic Loader (Bioformats based)] "
        + "project_filename=["
        + project_filename
        + ".xml"
        + "] "
        + "path=["
        + file_info["path"]
        + "] "
        + "exclude=10 "
        + "move_tiles_to_grid_(per_angle)?=[Do not move Tiles to Grid (use Metadata if available)] "
    )

    return options

def test_define_dataset_auto_tile(tmp_path, caplog):
    """Test method for tiles."""

    caplog.set_level(logging.WARNING)
    caplog.clear()

    project_filename = "proj_name"
    file_path = tmp_path
    file_info = pathtools.parse_path(file_path)

    result_folder = pathtools.join2(file_info["path"], project_filename)
    dataset_save_path = pathtools.join2(result_folder, project_filename)

    # Default settings

    bf_series_type = "Tiles"

    cmd = "Define dataset ..."

    options = set_default_values(project_filename, file_path)

    options = (
        options
        + "how_to_load_images=["
        + "Re-save as multiresolution HDF5"
        + "] "
        + "dataset_save_path=["
        + dataset_save_path
        + "] "
        + "check_stack_sizes "
        + "split_hdf5 "
        + "timepoints_per_partition=1 "
        + "setups_per_partition=0 "
        + "use_deflate_compression "
    )

    final_call = "IJ.run(cmd=[%s], params=[%s])" % (cmd, options)

    bdv.define_dataset_auto(project_filename, file_path, bf_series_type)
    assert final_call == caplog.messages[0]


def test_define_dataset_auto_angle(tmp_path, caplog):
    """Test method for tiles."""

    caplog.set_level(logging.WARNING)
    caplog.clear()

    project_filename = "proj_name"
    file_path = tmp_path
    file_info = pathtools.parse_path(file_path)

    result_folder = pathtools.join2(file_info["path"], project_filename)
    dataset_save_path = pathtools.join2(result_folder, project_filename)

    # Default settings

    bf_series_type = "Angles"
    cmd = "Define Multi-View Dataset"

    options = set_default_values(project_filename, file_path)


    options = (
        options
        + "how_to_load_images=["
        + "Re-save as multiresolution HDF5"
        + "] "
        + "dataset_save_path=["
        + dataset_save_path
        + "] "
        + "check_stack_sizes "
        + "apply_angle_rotation "
        + "split_hdf5 "
        + "timepoints_per_partition=1 "
        + "setups_per_partition=0 "
        + "use_deflate_compression "
    )

    final_call = "IJ.run(cmd=[%s], params=[%s])" % (cmd, options)

    bdv.define_dataset_auto(project_filename, file_path, bf_series_type)
    assert final_call == caplog.messages[0]