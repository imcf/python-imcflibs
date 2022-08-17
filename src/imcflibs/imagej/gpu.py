"""Convenience wrappers around CLIJ and GPU accelerated functions."""

from ij import IJ
from net.haesleinhuepf.clij2 import CLIJ2

def merge_labels_on_gpu(clij2_instance, label_image):
    """Merge touching labels using GPU acceleration

    Parameters
    ----------
    clij2_instance : clij2_instance
        Instance of CLIJ to communicate with GPU
    label_image : ImagePlus
        Label image with touching labels

    Returns
    -------
    ImagePlus
        New ImagePlus with merged labels
    """

    list_of_images = []

    for channel in range(label_image.getNChannels()):

        current_channel = Duplicator().run(label_image,
                                           channel + 1, channel + 1,
                                           1, label_image.getNSlices(),
                                           1, label_image.getNFrames())

        src = clij2_instance.push(current_channel)
        dst = clij2_instance.create(src)

        clij2_instance.mergeTouchingLabels(src, dst)
        list_of_images.append(clij2_instance.pull(dst))

        clij2_instance.clear()

    if len(list_of_images) > 1:
        return RGBStackMerge().mergeChannels(list_of_images, False)
    else :
        return list_of_images[0]

def erode_labels_on_gpu(clij2_instance, label_image, erosion_radius):
    """Erode labels using GPU acceleration

    Parameters
    ----------
    clij2_instance : clij2_instance
        Instance of CLIJ to communicate with GPU
    label_image : ImagePlus
        Label Image to erode
    erosion_radius : int
        Radius for erosion

    Returns
    -------
    ImagePlus
        Label image with eroded labels
    """

    #clij2 = CLIJ2.getInstance()
    src  = clij2_instance.push(label_image)
    dst  = clij2_instance.create(src)
    mask = clij2_instance.create(src)

    clij2_instance.erodeLabels(src, dst, erosion_radius, False)
    clij2_instance.mask(src, dst, mask)

    return clij2_instance.pull(mask)

def dilate_labels_on_gpu(clij2_instance, label_image, dilation_radius):
    """Dilate labels using GPU acceleration

    Parameters
    ----------
    clij2_instance : clij2_instance
        Instance of CLIJ to communicate with GPU
    label_image : ImagePlus
        Label Image to dilate
    erosion_radius : int
        Radius for dilation

    Returns
    -------
    ImagePlus
        Label image with dilated labels
    """

    #clij2 = CLIJ2.getInstance()
    src  = clij2_instance.push(label_image)
    dst  = clij2_instance.create(src)
    mask = clij2_instance.create(src)

    clij2_instance.dilateLabels(src, dst, dilation_radius)
    clij2_instance.mask(src, dst, mask)

    return clij2_instance.pull(mask)