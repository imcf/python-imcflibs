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
        Population to use to generate the new ImagePlus.

    Returns
    -------
    ImagePlus
        Newly created ImagePlus from the population.
    """
    dim = imp.getDimensions()
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
    new_img = ImageHandler.wrap(new_imp)
    population.drawPopulation(new_img)

    return new_img.getImagePlus()


def imgplus_to_population3d(imp):
    """Get an Objects3DPopulation from an ImagePlus (2D/3D).

    Works on: 2D and 3D.

    Parameters
    ----------
    imp : ij.ImagePlus
        Labeled 3D stack or 2D image to use to get population.

    Returns
    -------
    mcib3d.geom.Objects3DPopulation
        Population from the image.
    """
    img = ImageHandler.wrap(imp)
    return Objects3DPopulation(img)


def segment_3d_image(imp, title=None, min_thresh=1, min_vol=None, max_vol=None):
    """Segment a 3D binary image to get a labelled stack.

    Parameters
    ----------
    imp : ij.ImagePlus
        Binary 3D stack.
    title : str, optional
        Title of the new image.
    min_thresh : int, optional
        Threshold to do segmentation, also allows for label filtering, by default 1.
        Since the segmentation is happening on a binary stack, values are either 0 or 255
        so using 0 allows to discard only the background.
    min_vol : int, optional
        Volume (voxels) under which to filter objects, by default None.
    max_vol : int, optional
        Volume above which to filter objects, by default None.

    Returns
    -------
    ij.ImagePlus
        Segmented 3D labelled ImagePlus.
    """
    cal = imp.getCalibration()
    img = ImageHandler.wrap(imp)
    img = img.threshold(min_thresh, False, False)

    labeler = ImageLabeller()
    if min_vol:
        labeler.setMinSizeCalibrated(min_vol, img)
    if max_vol:
        labeler.setMaxSizeCalibrated(max_vol, img)

    seg = labeler.getLabels(img)
    seg.setScale(cal.pixelWidth, cal.pixelDepth, cal.getUnits())
    if title:
        seg.setTitle(title)

    return seg.getImagePlus()


def get_objects_within_intensity(obj_pop, imp, min_intensity, max_intensity):
    """Return a new population with the objects that have a mean intensity within
    the specified range.

    Parameters
    ----------
    obj_pop : Objects3DPopulation
        Population of 3D objects
    imp : ij.ImagePlus
        ImagePlus on which the population is based
    min_intensity : float
        Minimum mean intensity of the objects
    max_intensity : float
        Maximum mean intensity of the objects

    Returns
    -------
    Objects3DPopulation
        New population with the objects filtered by intensity
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
