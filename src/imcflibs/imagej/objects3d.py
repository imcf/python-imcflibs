from ij import IJ
from mcib3d.geom import Objects3DPopulation
from mcib3d.image3d import ImageHandler


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
