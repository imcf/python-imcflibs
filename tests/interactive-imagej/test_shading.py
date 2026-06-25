# Prerequisites before running this script in Fiji:
#
# - Open an image to test on (e.g. Shaded-blobs.png) in Fiji before running.
# - Drag this script into Fiji and run it.
#
# Expected result: a new image titled "Result of blobs.gif" opens alongside
# the original, showing a flatfield corrected version of the raw blobs.gif.

from imcflibs.imagej import shading
import ij
from ij import IJ

imp = IJ.getImage()

# Any other method in class shading also works
imcf_shading = shading.simple_flatfield_correction(imp)
imcf_shading.show()
