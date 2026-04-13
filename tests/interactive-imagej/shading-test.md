# Test shading function

 The following code block is a `python` script to be used in a Fiji with the shading branch's .jar already pasted into `./jars` in the Fiji installation

 Recommended is to import an image you wish to test on (`Shaded-blobs.png` e.g) and then drag this script into Fiji and run it, or make a new one and choose language Python, and paste the following block.

```python
from imcflibs.imagej import shading
import ij
from ij import IJ

imp = IJ.getImage()

# Any other method in class shading also works
imcf_shading = shading.simple_flatfield_correction(imp)
imcf_shading.show()
```

## Expected behavior / results

- A new image titled "Result of blobs.gif", which is a flatfield corrected image of the raw `blobs.gif` should open alongside the original.
