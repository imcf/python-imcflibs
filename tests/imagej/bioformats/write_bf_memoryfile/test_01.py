# @ File (label="Select the python-imcf-libs testdata directory", style="directory") PYTHON_IMCFLIBS_TESTDATA


import os
from imcflibs.imagej import bioformats


parent_dir = str(PYTHON_IMCFLIBS_TESTDATA).replace("\\", "/")
filename = "10x_phmax.czi"
full_path = parent_dir + "/" + "10x_phmax.czi"
bfmemofilename = "." + filename + ".bfmemo"
os.chdir(parent_dir)  # DANGEROUS, relative paths and calling remove() below!
if os.path.isfile(bfmemofilename):
    print("bf memo file already existed and was removed")
    os.remove(bfmemofilename)

bioformats.write_bf_memoryfile(full_path)

if not os.path.isfile(bfmemofilename):
    print("Test FAILED. A bf memo file does not exist.")
else:
    print("Test passed. A bf memo file was created.")
