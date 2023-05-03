"""Functions to work with the RoiManager."""

from ij.plugin import RoiEnlarger, RoiScaler  # pylint: disable-msg=import-error
from ij.plugin.frame import RoiManager  # pylint: disable-msg=import-error


def get_roimanager():
    """Instantiate or get the IJ-RoiManager instance.

    Use to either get the current instance of the IJ RoiManager or instantiate
    it if it does not yet exist.

    Returns
    -------
    ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    """
    rm = RoiManager.getInstance()
    if not rm:
        rm = RoiManager()
    return rm


def clear_ij_roi_manager(rm):
    """Delete all ROIs from the RoiManager.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    """
    rm.runCommand("reset")


def count_all_rois(rm):
    """Count the number of ROIS in the RoiManager.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.

    Returns
    -------
    int
        The number of ROIs in the RoiManager.
    """
    number_of_rois = rm.getCount()

    return number_of_rois


def save_rois_to_zip(rm, target, selected_rois=None):
    """Save selected ROIs in the RoiManager as zip to the target path.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    target : string
        The path to store the ROIs, e.g. /my-images/resulting_rois_subset.zip
    selected_rois : list
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
    """Show all ROIs in the ROiManager on the given ImagePlus.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    imp : ij.ImagePlus
        The imp on which to show the ROIs.
    """
    rm.runCommand(imp, "Show All")


def rename_rois(rm, string):
    """Rename all ROIs to include the given string as a prefix.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    string : str
        The string to prefix the ROIs with.
    """
    number_of_rois = rm.getCount()
    for roi in range(number_of_rois):
        rm.rename(roi, string + str(roi + 1))

    rm.runCommand("UseNames", "true")


def rename_rois_by_number(rm):
    """Rename all ROIs in the RoiManager according to their index number.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    """
    number_of_rois = rm.getCount()
    for roi in range(number_of_rois):
        rm.rename(roi, str(roi + 1))


def change_roi_color(rm, color, selected_rois=None):
    """Change the color of selected / all ROIs in the RoiManager.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    color : string
        The desired color. e.g. "green", "red", "yellow", "magenta" ...
    selected_rois : list, optional
        ROIs in the RoiManager that should be changed. By default None which
        will result in all ROIs to be changed.
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
    """Perform all configured measurements in one channel of the given image.

    The choice of measured parameters is done through ImageJ's "Set
    Measurements" command.

    Parameters
    ----------
    imp : ij.ImagePlus
        The imp to measure on.
    channel : integer
        The channel to measure in (starting at 1).
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    """
    imp.setC(channel)
    rm.runCommand(imp, "Deselect")
    rm.runCommand(imp, "Measure")


def load_rois_from_zip(rm, path):
    """Load ROIs from the given zip file and add them to the RoiManager.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    path : string
        Path to the ROI zip file.
    """
    rm.runCommand("Open", path)


def enlarge_all_rois(amount_in_um, rm, pixel_size_in_um):
    """Enlarge all ROIs in the RoiManager by x scaled units.

    Parameters
    ----------
    amount_in_um : float
        The value by which to enlarge in scaled units, e.g 3.5.
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    pixel_size_in_um : float
        The pixel size, e.g. 0.65 px/um.
    """
    amount_px = amount_in_um / pixel_size_in_um
    all_rois = rm.getRoisAsArray()
    rm.reset()
    for roi in all_rois:
        enlarged_roi = RoiEnlarger.enlarge(roi, amount_px)
        rm.addRoi(enlarged_roi)


def scale_all_rois(rm, scaling_factor):
    """Inflate or shrink all ROIs in the RoiManager.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    scaling_factor : float
        The scaling factor by which to inflate (if > 1) or shrink (if < 1 ).
    """
    all_rois = rm.getRoisAsArray()
    rm.reset()
    for roi in all_rois:
        scaled_roi = RoiScaler.scale(roi, scaling_factor, scaling_factor, True)
        rm.addRoi(scaled_roi)


def select_rois_above_min_intensity(imp, channel, rm, min_intensity):
    """Select ROIs based on their intensity in a given channel of the image.

    See https://imagej.nih.gov/ij/developer/api/ij/process/ImageStatistics.html

    Parameters
    ----------
    imp : ij.ImagePlus
        The imp on which to measure.
    channel : integer
        The channel to measure in (starting at 1).
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.
    min_intensity : integer
        The selection criterion (lower intensity threshold).

    Returns
    -------
    list(int)
        A list of ROI index numbers fulfilling the selection criterion
        (intensity is above the threshold).
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
    """Get the color names of the ROIs in the RoiManager.

    Iterates over all ROIs and gets either their "Stroke Color" (if present) or
    their "Color" property.

    Parameters
    ----------
    rm : ij.plugin.frame.RoiManager
        A reference of the IJ-RoiManager.

    Returns
    -------
    list
        A list containing the corresponding color name strings for each ROI.
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
        stroke_color = roi.getStrokeColor()
        if stroke_color:
            roi_colors.append(rgb_color_lookup[stroke_color.getRGB()])
        else:
            roi_colors.append(rgb_color_lookup[roi.getColor().getRGB()])

    return roi_colors


def add_rois_to_roimanager(
    roi_array, roi_manager, keep_rois_name, prefix, bbox=None, z_slice=None, group=None
):
    """Add all ROIs from a list to the RoiManager.

    Parameters
    ----------
    roi_array : list(ij.gui.Roi)
        List of ROIs to put in RM.
    roi_manager : ij.plugin.frame.RoiManager
        ROIManager in which to put the ROIs.
    keep_rois_name : bool
        If true, will keep the name of the ROI. Otherwise the ROI will be
        renamed using its index number.
    prefix : str
        String to prefix the name of the ROI with.
    bbox : java.awt.Rectangle, optional
        Use this bounding box to shift the ROI list, by default None.
    z_slice : int, optional
        Shift the ROI also in Z, by default None (=no shifting).
    group : int, optional
        Put the ROI into the given ROI group, by default None.
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
    """Move a ROI based on a bounding box.

    Translate one ROI based on another ROI's bounding box.

    Parameters
    ----------
    roi : ij.gui.Roi
        The ROI to be moved.
    bbox : java.awt.Rectangle
        The bounding box by which the ROI should be shifted, e.g. retrieved by
        calling `OtherRoi.getBounds()` on a ROI object.
    z_slice : int, optional
        Shift the ROI also in Z, by default None (=no shifting).
    """
    # roi_manager.reset()
    roi.setLocation(bbox.x + roi.getBounds().x, bbox.y + roi.getBounds().y)
    if z_slice is not None:
        roi.setPosition(roi.getPosition() + z_slice)
    return roi
