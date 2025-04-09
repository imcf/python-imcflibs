### ----------------------

 The following code block is a `python` script to be used in a Fiji with the shading branch's .jar already pasted into ./jars in the Fiji installation

 Recommended is to import an image you wish to test on (Shaded-blobs.png e.g) and then drag this script into Fiji and run it.
 If a resulting image pops up (while using flatfield method), everything works finely.
### ----------------------

```python
from imcflibs.imagej import shading
# import imcflibs.imagej
import ij
from ij import IJ

imp = IJ.getImage()
imcf_shading = shading.simple_flatfield_correction(imp)
# Or any other method in class shading
imcf_shading.show()