"""Functions to work with ImageJ label images."""

from ij import IJ, ImagePlus, Prefs
from ij.plugin import Duplicator, ImageCalculator
from ij.plugin.filter import ImageProcessor, ThresholdToSelection
from ij.process import FloatProcessor, ImageProcessor
from inra.ijpb.label import LabelImages as li
from inra.ijpb.plugins import AnalyzeRegions
from mcib3d.image3d import ImageHandler, ImageLabeller


def label_image_to_roi_list(label_image, low_thresh=None):
    """Convert a label image to a list of ROIs.

    Parameters
    ----------
    label_image : ij.ImagePlus
        Label image to convert.
    low_thresh : int, optional
        Value under which the labels should be discarded, by default `None`.

    Returns
    -------
    roi_list : list(ij.gui.Roi)
        List of all the ROIs converted from the label image.
    """

    roi_list = []
    max_value = 0

    for slice in range(1, label_image.getNSlices() + 1):
        label_image_slice = Duplicator().run(label_image, 1, 1, slice, slice, 1, 1)

        image_processor = label_image_slice.getProcessor()
        pixels = image_processor.getFloatArray()

        existing_pixel_values = set()

        for x in range(0, image_processor.getWidth()):
            for y in range(0, image_processor.getHeight()):
                existing_pixel_values.add(pixels[x][y])

        # Converts data in case it's RGB image
        float_processor = FloatProcessor(
            image_processor.getWidth(), image_processor.getHeight()
        )
        float_processor.setFloatArray(pixels)
        img_float_copy = ImagePlus("FloatLabel", float_processor)

        # print(existing_pixel_values)
        for value in existing_pixel_values:
            if low_thresh is not None:
                if value < low_thresh:
                    continue
            elif value == 0:
                continue
            # print(value)
            float_processor.setThreshold(value, value, ImageProcessor.NO_LUT_UPDATE)
            roi = ThresholdToSelection.run(img_float_copy)
            roi.setName(str(value))
            roi.setPosition(slice)
            roi_list.append(roi)
            max_value = max(max_value, value)

    return roi_list, max_value


def relate_label_images(label_image_ref, label_image_to_relate):
    """Relate label images, giving the same label to objects belonging together.

    ❗ NOTE: Won't work with touching labels ❗

    FIXME: explain with an example what the function is doing!

    Parameters
    ----------
    label_image_ref : ij.ImagePlus
        Reference to use for the labels.
    label_image_to_relate : ij.ImagePlus
        Image to change for the labels.

    Returns
    -------
    ij.ImagePlus
        New ImagePlus with modified labels matching the reference.
    """

    imp_dup = label_image_to_relate.duplicate()
    IJ.setRawThreshold(imp_dup, 1, 65535)
    Prefs.blackBackground = True
    IJ.run(imp_dup, "Convert to Mask", "")
    IJ.run(imp_dup, "Divide...", "value=255")
    return ImageCalculator.run(label_image_ref, imp_dup, "Multimage_processorly create")


def filter_objects(label_image, table, string, min_val, max_val):
    """Filter labels based on specific min and max values.

    Parameters
    ----------
    label_image : ij.ImagePlus
        Label image on which to filter.
    table : ResultsTable
        ResultsTable containing all the measurements on which to filter.
    string : str
        Measurement name on which to filter, e.g. `Area`, `Mean Intensity` etc.
    min_val : float
        Minimum value to keep.
    max_val : float
        Maximum value to keep

    Returns
    -------
    ij.ImagePlus
        Label image containing only the remaining labels.
    """

    keep_label_id = []
    for row in range(table.size()):
        current_value = table.getValue(string, row)
        if current_value >= min_val and current_value <= max_val:
            keep_label_id.append(int(table.getLabel(row)))

    return li.keepLabels(label_image, keep_label_id)


def measure_objects_size_shape_2d(label_image):
    """Measure the shapes of the different labels.

    Parameters
    ----------
    label_image : ij.ImagePlus
        Label image on which to get the shapes.

    Returns
    -------
    ResultsTable
        ResultsTable with the shape measurements.
    """
    regions = AnalyzeRegions()
    return regions.process(label_image)


def binary_to_label(imp, title, min_thresh=1, min_vol=None, max_vol=None):
    """Segment a binary image to get a label image (2D/3D).

    Works on: 2D and 3D binary data.

    Parameters
    ----------
    imp : ImagePlus
        Binary 3D stack or 2D image.
    title : str
        Title of the new image.
    min_thresh : int, optional
        Threshold to do segmentation, also allows for label filtering, by
        default 1.
    min_vol : float, optional
        Volume under which to exclude objects, by default None.
    max_vol : float, optional
        Volume above which to exclude objects, by default None.

    Returns
    -------
    ImagePlus
        Segmented labeled ImagePlus.
    """
    cal = imp.getCalibration()
    img = ImageHandler.wrap(imp)
    img = img.threshold(min_thresh, False, False)

    labeler = ImageLabeller()
    if min_vol:
        labeler.setMinSize(min_vol)
    if max_vol:
        labeler.setMaxSize(max_vol)

    seg = labeler.getLabels(img)
    seg.setScale(cal.pixelWidth, cal.pixelDepth, cal.getUnits())
    seg.setTitle(title)

    return seg.getImagePlus()
