This is a testing file for the trackmate branch and for the trackmate python class.

The following Fiji script needs a `.jar` of the trackmate branch to be installed into Fiji already.

You can open the a blobs image (`CTRL+SHIFT+B`) and then run the following script: 

```python
from imcflibs.imagej import trackmate
from ij import IJ

imp = IJ.getImage()
# Detector
settings = trackmate.log_detector(imp, 5, 1, 0)
# settings = trackmate.cellpose_detector(imp, "S:\cellpose_env", "NUCLEI", 23.0, 1, 0) # WORKS, tested
# settings = trackmate.stardist_detector(imp, 1) # WORKS, tested 

# Manual tracker addition, run_trackmate does this otherwise
# settings = trackmate.sparseLAP_tracker(settings)

# Spot and track filtering
# settings = trackmate.spot_filtering(settings, None, 1.0, None, None)
# settings = trackmate.track_filtering(settings, 15.0, 15.0, 3, 1, 1)

res_img = trackmate.run_trackmate(imp, settings)
res_img.show()

```