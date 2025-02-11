from ij import IJ
from mcib3d.geom import Objects3DPopulation
from mcib3d.image3d import ImageHandler, ImageLabeller


def population3d_to_imgplus(imp, population):
    """Make an ImagePlus from an Objects3DPopulation (2D/3D).

    Works on: 2D and 3D.

    Parameters
    ----------
    imp : ij.ImagePlus
        Original ImagePlus to derive the size of the resulting ImagePlus.
    population : mcib3d.geom.Objects3DPopulation
        Population of 3D objects used to generate the new ImagePlus.

    Returns
    -------
    ij.ImagePlus
        A newly created ImagePlus representing the labeled population.
    """
    dim = imp.getDimensions()

    # Create a new 16-bit image with the same size as the original image
    new_imp = IJ.createImage(
        "Filtered labeled stack",
        "16-bit black",
        dim[0],
        dim[1],
        1,
        dim[3],
        dim[4],
    )
    new_imp.setCalibration(imp.getCalibration())

    # Wrap the new image in an ImageHandler and draw the population
    new_img = ImageHandler.wrap(new_imp)
    population.drawPopulation(new_img)

    return new_img.getImagePlus()


def imgplus_to_population3d(imp):
    """Get an Objects3DPopulation from an ImagePlus (2D/3D).

    Works on: 2D and 3D.

    Parameters
    ----------
    imp : ij.ImagePlus
        Labeled 2D image or 3D stack used to get the population.

    Returns
    -------
    mcib3d.geom.Objects3DPopulation
        The extracted population from the image.
    """
    img = ImageHandler.wrap(imp)
    return Objects3DPopulation(img)


def segment_3d_image(imp, title=None, min_thresh=1, min_vol=None, max_vol=None):
    """Segment a 3D binary image to get a labelled stack.

    Parameters
    ----------
    imp : ij.ImagePlus
        A binary 3D stack for segmentation.
    title : str, optional
        Title of the new image. Defaults to None.
    min_thresh : int, optional
        Threshold to do segmentation, also allows for label filtering. Since the
        segmentation is happening on a binary stack, values are either 0 or 255,
        so using 0 allows to discard only the background.  Defaults to 1.
    min_vol : int, optional
        Minimum volume (in voxels) under which objects get filtered.
        Defaults to None.
    max_vol : int, optional
        Maximum volume (in voxels) above which objects get filtered.
        Defaults to None.

    Returns
    -------
    ij.ImagePlus
        A labelled 3D ImagePlus.
    """
    cal = imp.getCalibration()

    # Wrap through ImageHandler and apply thresholding
    img = ImageHandler.wrap(imp)
    img = img.threshold(min_thresh, False, False)

    labeler = ImageLabeller()
    if min_vol:
        labeler.setMinSizeCalibrated(min_vol, img)
    if max_vol:
        labeler.setMaxSizeCalibrated(max_vol, img)

    # Generate labelled segmentation
    seg = labeler.getLabels(img)
    seg.setScale(cal.pixelWidth, cal.pixelDepth, cal.getUnits())
    if title:
        seg.setTitle(title)

    return seg.getImagePlus()


def get_objects_within_intensity(obj_pop, imp, min_intensity, max_intensity):
    """Filter a population for objects within the given intensity range.

    Parameters
    ----------
    obj_pop : mcib3d.geom.Objects3DPopulation
        A population of 3D objects.
    imp : ij.ImagePlus
        An ImagePlus on which the population is based.
    min_intensity : float
        Minimum mean intensity threshold for filtering objects.
    max_intensity : float
        Maximum mean intensity threshold for filtering objects.

    Returns
    -------
    Objects3DPopulation
        New population with the objects filtered by intensity.
    """
    objects_within_intensity = []

    # Iterate over all objects in the population
    for i in range(0, obj_pop.getNbObjects()):
        obj = obj_pop.getObject(i)
        # Calculate the mean intensity of the object
        mean_intensity = obj.getPixMeanValue(ImageHandler.wrap(imp))
        # Check if the object is within the specified intensity range
        if mean_intensity >= min_intensity and mean_intensity < max_intensity:
            objects_within_intensity.append(obj)

    # Return the new population with the filtered objects
    return Objects3DPopulation(objects_within_intensity)
