# Prerequisites before running this script in Fiji:
#
# - Open the blobs image, e.g. using Ctrl + Shift + B.
# - Drag and drop this script and run it in Fiji.
#
# Expected result: a label image named "LblImg_blobs.gif" opens next to the raw
# blobs.gif with many segmented spots (LoG detector). With the Cellpose detector
# the segmented blobs should be quite accurate; the LoG detector finds many spots
# across the image.

from imcflibs.imagej import trackmate
from ij import IJ

imp = IJ.getImage()

# Select the trackmate LoG detector:
settings = trackmate.log_detector(imp, 5, 1, 0)

# Alternatively, use the Cellpose or StarDist detector:
# settings = trackmate.cellpose_detector(imp, "S:\cellpose_env", "NUCLEI", 23.0, 1, 0)
# settings = trackmate.stardist_detector(imp, 1)

# Manual tracker addition, run_trackmate does this otherwise:
# settings = trackmate.sparseLAP_tracker(settings)

# Spot and track filtering:
# settings = trackmate.spot_filtering(settings, None, 1.0, None, None)
# settings = trackmate.track_filtering(settings, 15.0, 15.0, 3, 1, 1)

res_img = trackmate.run_trackmate(imp, settings)
res_img.show()
