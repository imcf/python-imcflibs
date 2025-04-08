Following is a testing script for the retrieval of metadata methods in imcflibs.imagej.bioformats.

Copy the following code to a Fiji that has the release `python-imcflibs-1.5.0.jar` in the /jars directory.

Add the source folder and the names of the files under the corresponding lines, and run the script. If the metadata is printed in Fiji output, the methods are working as intended

```
# @ File (label="IMCF testdata location", style="directory") IMCF_TESTDATA

import os
from imcflibs.pathtools import join2
from imcflibs.imagej import bioformats
from ij import IJ

# Testing for the metadata retrieval through Bioformats

# Add directory path here that contains the files you wish to test for

file_path_1 = join2(IMCF_TESTDATA, "bioformats/DON_25922_20250201_25922_2_01.vsi")
file_path_2 = join2(IMCF_TESTDATA, "bioformats/DON_25922_20250201_25922_2_02.vsi")
file_path_3 = join2(IMCF_TESTDATA, "bioformats/DON_25922_20250201_25922_2_03.vsi")

metadata = bioformats.get_metadata_from_file(file_path_1)
print(metadata.unit_width)
print(metadata.unit)
print(metadata.channel_count)

# Stage metadata and coordinates test for a list of vsi files
fnames = [file_path_1, file_path_2, file_path_3]

metadata_stage = bioformats.get_stage_coords(fnames)

print(metadata_stage.image_calibration)
print(metadata_stage.stage_coordinates_x)
print(metadata_stage.stage_coordinates_y)
print(metadata_stage.stage_coordinates_z)
```