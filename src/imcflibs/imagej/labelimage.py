from ij import IJ, ImagePlus
from ij.plugin import Duplicator
from ij.process import FloatProcessor
from ij.plugin.filter import ThresholdToSelection, ImageProcessor

def label_image_to_roi_list(implus, low_thresh=None):
    """Converts a label image to a list of ROIs

    Parameters
    ----------
    implus : ImagePlus
        Label image to convert
    low_thresh : int
        Value under which the labels should be discarded

    Returns
    -------
    roi_list : ROI[]
        List of all the ROIs converted from the label image
    """
    roi_list = []
    max_value = 0

    for slice in range(1, implus.getNSlices() + 1):
        implus_slice = Duplicator().run(implus, 1, 1, slice, slice, 1, 1)

        ip = implus_slice.getProcessor()
        pixels = ip.getFloatArray()

        existing_pixel_values = set()

        for x in range(0,ip.getWidth()):
            for y in range(0,ip.getHeight()):
                existing_pixel_values.add(pixels[x][y])


        # Converts data in case it's RGB image
        fp = FloatProcessor(ip.getWidth(), ip.getHeight())
        fp.setFloatArray(pixels)
        img_float_copy = ImagePlus("FloatLabel", fp)

        # print(existing_pixel_values)
        for value in existing_pixel_values:
            if low_thresh is not None :
                if value < low_thresh:
                    continue
            elif value == 0:
                continue
            # print(value)
            fp.setThreshold(value, value, ImageProcessor.NO_LUT_UPDATE)
            roi = ThresholdToSelection.run(img_float_copy)
            roi.setName(str(value))
            roi.setPosition(slice)
            roi_list.append(roi)
            max_value = max(max_value, value)

    return roi_list, max_value

