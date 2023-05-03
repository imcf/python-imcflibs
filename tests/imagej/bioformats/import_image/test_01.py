# @ File (label="Select the IMCF testdata directory", style="directory") IMCF_TESTDATA

import os
from imcflibs.pathtools import join2
from imcflibs.imagej import bioformats


testfile = join2(IMCF_TESTDATA, "systems/lsm700/beads/10x_phmax.czi")
print(testfile)

assert os.path.exists(testfile)

imps = bioformats.import_image(testfile)
assert len(imps) > 0
imp = imps[0]
imp.show()

print("Test completed, a new multi-channel stack should have opened. ")
