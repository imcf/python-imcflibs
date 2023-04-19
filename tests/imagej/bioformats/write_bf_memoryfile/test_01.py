# @ File (label="Select the python-imcf-libs testdata directory", style="directory") PYTHON_IMCFLIBS_TESTDATA


import os
from imcflibs.pathtools import parse_path
from imcflibs.imagej import bioformats


components = parse_path("systems/lsm700/beads/10x_phmax.czi", PYTHON_IMCFLIBS_TESTDATA)
full_path = components["full"]
bfmemofile = components["path"] + "." + components["fname"] + ".bfmemo"

if os.path.isfile(bfmemofile):
    print("BF memory file [%s] already exists, removing..." % bfmemofile)
    os.remove(bfmemofile)


bioformats.write_bf_memoryfile(full_path)


if not os.path.isfile(bfmemofile):
    print("Test FAILED: can't find BF memory file [%s]" % bfmemofile)
else:
    print("Test passed, BF memory file [%s] was created." % bfmemofile)
