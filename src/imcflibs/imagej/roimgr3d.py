from ij import IJ
from mcib3d.geom import Objects3DPopulation
from mcib3d.image3d import ImageHandler, ImageLabeller


def binary_to_label(imp, title, min_thresh=1, min_vol=None, max_vol=None):
    """Segment a binary image to get a label image (2D/3D).

    Works on: 2D and 3D binary data.

    Parameters
    ----------
    imp : ImagePlus
        Binary 3D stack
    title : str
        Title of the new image
    min_thresh : int, optional
        Threshold to do segmentation, also allows for label filtering by default 1
    min_vol : float, optional
        Volume under which to filter objects, by default None
    max_vol : float, optional
        Volume above which to filter objects, by default None

    Returns
    -------
    ImagePlus
        Segmented 3D labelled ImagePlus
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


def redraw_stack_from_Objects3DPopulation(imp, pop):
    """Make an ImagePlus from a Objects3DPopulation

    Parameters
    ----------
    imp : ImagePlus
        Original ImagePlus to get info about size
    pop : Objects3DPopulation
        Population to use to draw the new stack

    Returns
    -------
    ImagePlus
        Newly created ImagePlus from the population
    """
    dim = imp.getDimensions()
    new_imp = IJ.createImage(
        "Filtered labelled stack",
        "16-bit black",
        dim[0],
        dim[1],
        1,
        dim[3],
        dim[4],
    )
    new_imp.setCalibration(imp.getCalibration())
    new_img = ImageHandler.wrap(new_imp)
    pop.drawPopulation(new_img)
    return new_img.getImagePlus()


def pop_from_ImagePlus(imp):
    """Get the Objects3DPopulation from an ImagePlus

    Parameters
    ----------
    imp : ImagePlus
        Labelled stack to use to get population

    Returns
    -------
    Objects3DPopulation
        Population from the image
    """
    img = ImageHandler.wrap(imp)
    return Objects3DPopulation(img)
