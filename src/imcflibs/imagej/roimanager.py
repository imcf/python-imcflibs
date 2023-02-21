from ij.plugin.frame import RoiManager
from ij.plugin import RoiEnlarger, RoiScaler


def instantiate_roimanager():
    """instantiates the IJ-RoiManager

    Returns
    -------
    IJ-RoiManager
        a reference of the IJ-RoiManager
    """
    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()
    return rm


def clear_ij_roi_manager(rm):
    """delete all ROIs from the RoiManager

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    """
    rm.runCommand("reset")


def count_all_rois(rm):
    """count the number of ROIS in the Roi manager

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager

    Returns
    -------
    int
        the number of rois in the IJ-RoiManager
    """
    number_of_rois = rm.getCount()

    return number_of_rois


def save_rois(rm, target, selected_rois=None):
    """save selected ROIs in the RoiManager as zip to target path

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    target : string
        the path in to store the ROIs. e.g. /my-images/resulting_rois_subset.zip
    selected_rois : array
        selected ROIs in the RoiManager to save
    """
    if selected_rois is not None:
        rm.runCommand("Deselect")
        rm.setSelectedIndexes(selected_rois)
        rm.runCommand("save selected", target)
        rm.runCommand("Deselect")
    else:
        rm.runCommand("Save", target)


def show_all_rois_on_image(rm, imp):
    """shows all ROIs in the ROiManager on imp

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    imp : ImagePlus
        the imp on which to show the ROIs
    """
    rm.runCommand(imp, "Show All")


def rename_rois(rm, string):
    """enumerate and rename all ROIs to include a custom string

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    string : str
        _description_
    """
    number_of_rois = rm.getCount()
    for roi in range(number_of_rois):
        rm.rename(roi, string + str(roi + 1))

    rm.runCommand("UseNames", "true")


def rename_rois_by_number(rm):
    """rename all ROIs in the RoiManager according to their number

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    """
    number_of_rois = rm.getCount()
    for roi in range(number_of_rois):
        rm.rename(roi, str(roi + 1))


def change_roi_color(rm, color, selected_rois=None):
    """change the color of selected / all ROIs in the RoiManager

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    color : string
        the desired color. e.g. "green", "red", "yellow", "magenta" ...
    selected_rois : array
        ROIs in the RoiManager to change
    """
    if selected_rois is not None:
        rm.runCommand("Deselect")
        rm.setSelectedIndexes(selected_rois)
        rm.runCommand("Set Color", color)
        rm.runCommand("Deselect")
    else:
        number_of_rois = rm.getCount()
        for roi in range(number_of_rois):
            rm.select(roi)
            rm.runCommand("Set Color", color)


def measure_in_all_rois(imp, channel, rm):
    """measures in all ROIS on a given channel of imp all parameters that are set in IJ "Set Measurements"

    Parameters
    ----------
    imp : ImagePlus
        the imp to measure on
    channel : integer
        the channel to measure in. starts at 1.
    rm : RoiManager
        a reference of the IJ-RoiManager
    """
    imp.setC(channel)
    rm.runCommand(imp, "Deselect")
    rm.runCommand(imp, "Measure")


def open_rois_from_zip(rm, path):
    """open RoiManager ROIs from zip and adds them to the RoiManager

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    path : string
        path to the Roi zip file
    """
    rm.runCommand("Open", path)


def enlarge_all_rois(amount_in_um, rm, pixel_size_in_um):
    """enlarges all ROIs in the RoiManager by x scaled units

    Parameters
    ----------
    amount_in_um : float
        the value by which to enlarge in scaled units, e.g 3.5
    rm : RoiManager
        a reference of the IJ-RoiManager
    pixel_size_in_um : float
        the pixel size, e.g. 0.65 px/um
    """
    amount_px = amount_in_um / pixel_size_in_um
    all_rois = rm.getRoisAsArray()
    rm.reset()
    for roi in all_rois:
        enlarged_roi = RoiEnlarger.enlarge(roi, amount_px)
        rm.addRoi(enlarged_roi)


def scale_all_rois(rm, scaling_factor):
    """inflate or shrink all ROIs in the RoiManager

    Parameters
    ----------
    rm : RoiManager
        a reference of the IJ-RoiManager
    scaling_factor : float
        the scaling factor by which to inflate (if > 1) or shrink (if < 1 )
    """
    all_rois = rm.getRoisAsArray()
    rm.reset()
    for roi in all_rois:
        scaled_roi = RoiScaler.scale(roi, scaling_factor, scaling_factor, True)
        rm.addRoi(scaled_roi)


def select_rois_above_min_intensity(imp, channel, rm, min_intensity):
    """For all ROIs in the RoiManager, select ROIs based on intensity measurement in given channel of imp.
    See https://imagej.nih.gov/ij/developer/api/ij/process/ImageStatistics.html

    Parameters
    ----------
    imp : ImagePlus
        the imp on which to measure
    channel : integer
        the channel on which to measure. starts at 1
    rm : RoiManager
        a reference of the IJ-RoiManager
    min_intensity : integer
        the selection criterion (here: intensity threshold)

    Returns
    -------
    array
        a selection of ROIs which passed the selection criterion (are above the threshold)
    """
    imp.setC(channel)
    all_rois = rm.getRoisAsArray()
    selected_rois = []
    for i, roi in enumerate(all_rois):
        imp.setRoi(roi)
        stats = imp.getStatistics()
        if stats.max > min_intensity:
            selected_rois.append(i)

    return selected_rois


def extract_color_of_all_rois(rm):
    """get the RGB color of ROIs in the RoiManager and match it to the colors name string

    Parameters
    ----------
    rm : RoiManager
        the IJ-RoiManager

    Returns
    -------
    array
        an array containing the corresponding color name string for each roi in the ROiManager
    """
    rgb_color_lookup = {
        -65536: "red",
        -65281: "magenta",
        -16711936: "green",
        -256: "yellow",
        -1: "white",
        -16776961: "blue",
        -16777216: "black",
        -14336: "orange",
        -16711681: "cyan",
    }

    all_rois = rm.getRoisAsArray()
    roi_colors = []
    for roi in all_rois:
        if roi.getStrokeColor() == None:
            roi_colors.append(rgb_color_lookup[roi.getColor().getRGB()])
        else:
            roi_colors.append(rgb_color_lookup[roi.getStrokeColor().getRGB()])

    return roi_colors


def put_rois_to_roimanager(
    roi_array, roi_manager, keep_rois_name, prefix, bbox=None, z_slice=None, group=None
):
    """Puts all ROIs from a list to the Roi Manager

    Parameters
    ----------
    roi_array : list(roi)
        List of ROIs to put in RM
    roi_manager : RoiManager
        ROIManager in which to put the ROIs
    keep_rois_name : bool
        If true, will keep the name of the Roi or will change it to its index
    prefix : str
        Prefix to put in front of the name of the Roi
    bbox : roi, optional
        Use this Roi's bounding box to shift the Roi array, by default None
    z_slice : int, optional
        If exists, will also shift the Roi in Z, by default None
    group : int, optional
        If exists, will put the Roi into a Roi group, by default None
    """
    # roi_manager.reset()
    for index, roi in enumerate(roi_array):
        if not keep_rois_name:
            roi.setName(prefix + "-" + str(index))
        else:
            roi.setName(prefix + "-" + roi.getName())
        if bbox is not None:
            roi = shift_roi_by_bounding_box(roi, bbox, z_slice)
        if group is not None:
            roi.setGroup(group)
        roi_manager.addRoi(roi)


def shift_roi_by_bounding_box(roi, bbox, z_slice=None):
    """Move a Roi based on a bounding box

    Parameters
    ----------
    roi  : Roi
        Current Roi
    bbox : Roi
        Use this Roi's bounding box to shift the Roi array
    z_slice : int, optional
        If exists, will also shift the Roi in Z, by default None
    """
    # roi_manager.reset()
    roi.setLocation(bbox.x + roi.getBounds().x, bbox.y + roi.getBounds().y)
    if z_slice is not None:
        roi.setPosition(roi.getPosition() + z_slice)
    return roi
