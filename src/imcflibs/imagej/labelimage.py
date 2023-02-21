"""Functions to work with ImageJ label images."""

# pylint: disable-msg=import-error

from ij import IJ, ImagePlus, Prefs
from ij.plugin import Duplicator, ImageCalculator
from ij.process import FloatProcessor, ImageProcessor
from ij.plugin.filter import ThresholdToSelection


def label_image_to_roi_list(label_image, low_thresh=None):
    """Converts a label image to a list of ROIs

    Parameters
    ----------
    label_image : ImagePlus
        Label image to convert
    low_thresh : int, optional
        Value under which the labels should be discarded, by default None

    Returns
    -------
    roi_list : list(roi)  FIXME: what's the exact "roi" type?
        List of all the ROIs converted from the label image
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
    """Relate label images, giving same label to objects being together

    /!\ Won't work with touching labels

    Parameters
    ----------
    label_image_ref : ImagePlus
        Reference to use for the labels
    label_image_to_relate : ImagePlus
        Image to change for the labels

    Returns
    -------
    ImagePlus
        New ImagePlus with modified labels matching the reference
    """

    imp_dup = label_image_to_relate.duplicate()
    IJ.setRawThreshold(imp_dup, 1, 65535)
    Prefs.blackBackground = True
    IJ.run(imp_dup, "Convert to Mask", "")
    IJ.run(imp_dup, "Divide...", "value=255")
    return ImageCalculator.run(label_image_ref, imp_dup, "Multimage_processorly create")
