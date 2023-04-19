"""Convenience wrappers around CLIJ and GPU accelerated functions."""

from ij.plugin import Duplicator, RGBStackMerge  # pylint: disable-msg=import-error


def erode_labels(clij2_instance, label_image, erosion_radius, channel=None):
    """Erode labels using GPU acceleration.

    Parameters
    ----------
    clij2_instance : net.haesleinhuepf.clij.CLIJ
        Instance of CLIJ to communicate with the GPU.
    label_image : ij.ImagePlus
        Label image to be eroded.
    erosion_radius : int
        Radius for erosion.
    channel : int, optional
        Specific channel to apply erosion.

    Returns
    -------
    ij.ImagePlus
        Label image with eroded labels.
    """

    list_of_images = []
    channel_list = [channel] if channel else range(1, label_image.getNChannels() + 1)

    for channel in channel_list:
        current_channel = Duplicator().run(
            label_image,
            channel,
            channel,
            1,
            label_image.getNSlices(),
            1,
            label_image.getNFrames(),
        )

        # clij2 = CLIJ2.getInstance()
        src = clij2_instance.push(current_channel)
        dst = clij2_instance.create(src)
        mask = clij2_instance.create(src)

        clij2_instance.erodeLabels(src, dst, erosion_radius, False)
        clij2_instance.mask(src, dst, mask)

        list_of_images.append(clij2_instance.pull(mask))

    if len(list_of_images) > 1:
        return RGBStackMerge().mergeChannels(list_of_images, False)
    else:
        return list_of_images[0]


def dilate_labels(clij2_instance, label_image, dilation_radius, channel=None):
    """Dilate labels using GPU acceleration.

    Parameters
    ----------
    clij2_instance : net.haesleinhuepf.clij.CLIJ
        Instance of CLIJ to communicate with the GPU.
    label_image : ij.ImagePlus
        Label Image to be dilated.
    erosion_radius : int
        Radius for dilation.
    channel : int, optional
        Specific channel to apply dilation.

    Returns
    -------
    ij.ImagePlus
        Label image with dilated labels.
    """

    list_of_images = []
    channel_list = [channel] if channel else range(1, label_image.getNChannels() + 1)

    for channel in channel_list:
        print(channel)

        current_channel = Duplicator().run(
            label_image,
            channel,
            channel,
            1,
            label_image.getNSlices(),
            1,
            label_image.getNFrames(),
        )

        # clij2 = CLIJ2.getInstance()
        src = clij2_instance.push(current_channel)
        dst = clij2_instance.create(src)
        mask = clij2_instance.create(src)

        clij2_instance.dilateLabels(src, dst, dilation_radius)
        # clij2_instance.mask(src, dst, mask) # Seems that for dilation no masking is needed ?

        list_of_images.append(clij2_instance.pull(dst))
        # clij2_instance.pull(mask).show()

        clij2_instance.clear()

    if len(list_of_images) > 1:
        return RGBStackMerge().mergeChannels(list_of_images, False)
    else:
        return list_of_images[0]


def merge_labels(clij2_instance, label_image, channel=None):
    """Merge touching labels using GPU acceleration.

    Parameters
    ----------
    clij2_instance : net.haesleinhuepf.clij.CLIJ
        Instance of CLIJ to communicate with the GPU.
    label_image : ij.ImagePlus
        Label image with touching labels.
    channel : int, optional
        Specific channel to apply label merging.

    Returns
    -------
    ij.ImagePlus
        New ImagePlus with merged labels.
    """

    list_of_images = []

    if channel is None:
        channel_list = range(1, label_image.getNChannels() + 1)
    else:
        channel_list = [channel]

    for channel in channel_list:
        current_channel = Duplicator().run(
            label_image,
            channel,
            channel,
            1,
            label_image.getNSlices(),
            1,
            label_image.getNFrames(),
        )

        src = clij2_instance.push(current_channel)
        dst = clij2_instance.create(src)

        clij2_instance.mergeTouchingLabels(src, dst)
        list_of_images.append(clij2_instance.pull(dst))

        clij2_instance.clear()

    if len(list_of_images) > 1:
        return RGBStackMerge().mergeChannels(list_of_images, False)

    return list_of_images[0]
