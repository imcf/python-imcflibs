# Testing the `imcflibs.imagej.trackmate` module

Instructions for *interactive* testing (i.e. manually running a script in Fiji's
*Script Editor*) of the `imcflibs.imagej.trackmate` module.

## Testing instructions

1. An updated `python-imcflibs.jar` containing the changes to be tested has to
   be installed into Fiji already.
1. Next, open the blobs image, e.g. using `Ctrl` + `Shift` + `B`.
1. Then, launch the *Script Editor* using `Ctrl` + `Shift` + `N`, paste the
   following script and finally run it:

```Python
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
```

## Expected behavior / results

FIXME!!
