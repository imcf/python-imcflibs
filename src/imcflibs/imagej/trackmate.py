import sys

from fiji.plugin.trackmate import Logger, Model, SelectionModel, Settings, TrackMate
from fiji.plugin.trackmate.action import LabelImgExporter
from fiji.plugin.trackmate.cellpose import CellposeDetectorFactory
from fiji.plugin.trackmate.cellpose.CellposeSettings import PretrainedModel
from fiji.plugin.trackmate.features import FeatureFilter
from fiji.plugin.trackmate.tracking.jaqaman import LAPUtils, SparseLAPTrackerFactory
from java.lang import Double


def run_tm(
    implus,
    detector_type,
    channel_number,
def cellpose_detector(
    imageplus,
    cellpose_env_path,
    model_to_use,
    obj_diameter,
    target_chnl,
    optional_chnl=None,
    use_gpu=True,
    simplify_contours=True,
):
    """Create a dictionary with all settings for TrackMate using Cellpose.

    Parameters
    ----------
    imageplus : ij.ImagePlus
        ImagePlus on which to apply the detector.
    cellpose_env_path : str
        Path to the Cellpose environment.
    model_to_use : str
        Name of the model to use for the segmentation (CYTO, NUCLEI, CYTO2).
    obj_diameter : float
        Diameter of the objects to detect in the image.
        This will be calibrated to the unit used in the image.
    target_chnl : int
        Index of the channel to use for segmentation.
    optional_chnl : int, optional
        Index of the secondary channel to use for segmentation, by default None.
    use_gpu : bool, optional
        Boolean for GPU usage, by default True.
    simplify_contours : bool, optional
        Boolean for simplifying the contours, by default True.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """
    settings = Settings(imageplus)

    settings.detectorFactory = CellposeDetectorFactory()
    settings.detectorSettings["TARGET_CHANNEL"] = target_chnl
    if optional_chnl:
        settings.detectorSettings["OPTIONAL_CHANNEL_2"] = optional_chnl
    settings.detectorSettings["CELLPOSE_PYTHON_FILEPATH"] = pathtools.join2(
        cellpose_env_path, "python.exe"
    )
    settings.detectorSettings["CELLPOSE_MODEL_FILEPATH"] = os.path.join(
        os.environ["USERPROFILE"], ".cellpose", "models"
    )
    settings.detectorSettings["CELLPOSE_MODEL"] = model_to_use
    settings.detectorSettings["CELL_DIAMETER"] = obj_diameter
    settings.detectorSettings["USE_GPU"] = use_gpu
    settings.detectorSettings["SIMPLIFY_CONTOURS"] = simplify_contours

    return settings


def stardist_detector(imageplus, target_chnl):
    """Create a dictionary with all settings for TrackMate using StarDist.

    Parameters
    ----------
    imageplus : ij.ImagePlus
        Image on which to do the segmentation.
    target_chnl : int
        Index of the channel on which to do the segmentation.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """

    settings = Settings(imageplus)
    settings.detectorFactory = StarDistDetectorFactory()
    settings.detectorSettings["TARGET_CHANNEL"] = target_chnl

    return settings


def log_detector(
    imageplus,
    radius,
    target_chnl,
    quality_threshold=0.0,
    median_filtering=True,
    subpix_localization=True,
):
    """Create a dictionary with all settings for TrackMate using the LogDetector.

    Parameters
    ----------
    imageplus : ij.ImagePlus
        Image on which to do the segmentation.
    radius : float
        Radius of the objects to detect.
    target_chnl : int
        Index of the channel on which to do the segmentation.
    quality_threshold : int, optional
        Threshold to use for excluding the spots by quality, by default 0.
    median_filtering : bool, optional
        Boolean to do median filtering, by default True.
    subpix_localization : bool, optional
        Boolean to do subpixel localization, by default True.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """

    settings = Settings(imageplus)
    settings.detectorFactory = LogDetectorFactory()

    settings.detectorSettings["RADIUS"] = Double(radius)
    settings.detectorSettings["TARGET_CHANNEL"] = target_chnl
    settings.detectorSettings["THRESHOLD"] = Double(quality_threshold)
    settings.detectorSettings["DO_MEDIAN_FILTERING"] = median_filtering
    settings.detectorSettings["DO_SUBPIXEL_LOCALIZATION"] = subpix_localization

    return settings

def spot_filtering(
    settings,
    quality_thresh=None,
    area_thresh=None,
    circularity_thresh=None,
    intensity_dict_thresh=None,
):
    """Add spot filtering for different features to the settings dictionary.

    Parameters
    ----------
    settings : fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    quality_thresh : float, optional
        Threshold to use for quality filtering of the spots, by default None.
        If the threshold is positive, will exclude everything below the value.
        If the threshold is negative, will exclude everything above the value.
    area_thresh : float, optional
        Threshold to use for area filtering of the spots, by default None.
        If the threshold is positive, will exclude everything below the value.
        If the threshold is negative, will exclude everything above the value.
    circularity_thresh : float, optional
        Threshold to use for circularity filtering of the spots, by default None.
        If the threshold is positive, will exclude everything below the value.
        If the threshold is negative, will exclude everything above the value.
    intensity_dict_thresh : dict, optional
        Threshold to use for intensity filtering of the spots, by default None.
        Dictionary needs to contain the channel index as key and the filter as value.
        If the threshold is positive, will exclude everything below the value.
        If the threshold is negative, will exclude everything above the value.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """

    settings.initialSpotFilterValue = -1.0
    settings.addAllAnalyzers()

    # Here 'true' takes everything ABOVE the mean_int value
    if quality_thresh:
        filter_spot = FeatureFilter("QUALITY", Double(abs(quality_thresh)))
        settings.addSpotFilter(filter_spot)
    if area_thresh:
        filter_spot = FeatureFilter("AREA", Double(abs(area_thresh)), area_thresh >= 0)
        settings.addSpotFilter(filter_spot)
    if circularity_thresh:
        filter_spot = FeatureFilter(
            "CIRCULARITY", Double(abs(circularity_thresh)), circularity_thresh >= 0
        )
        settings.addSpotFilter(filter_spot)
    if intensity_dict_thresh:
        for key, value in intensity_dict_thresh.items():
            filter_spot = FeatureFilter(
                "MEAN_INTENSITY_CH" + str(key), abs(value), value >= 0
            )
            settings.addSpotFilter(filter_spot)

    return settings
    crop_roi=None,
):
    # sourcery skip: merge-else-if-into-elif, swap-if-else-branches
    """Function to run TrackMate on open data. Has some specific input

    Parameters
    ----------
    implus : ImagePlus
        ImagePlus on which to run image
    detector_type : str
        Detector type to use
    channel_number : int
        Number of the channel of interest
    quality_thresh : float, optional
        Value to enter as threshold in the filters, by default None
    intensity_thresh : float, optional
        Value to enter as threshold in the filters, by default None
    circularity_thresh : float, optional
        Value to enter as threshold in the filters, by default None
    area_thresh : float, optional
        Value to enter as threshold in the filters, by default None
    crop_roi : ij.gui.Roi, optional
        ROI to crop on the image, by default None
    """

    dims = implus.getDimensions()
    cal = implus.getCalibration()

    if implus.getNSlices() > 1:
        implus.setDimensions(dims[2], dims[4], dims[3])

    if crop_roi is not None:
        implus.setRoi(crop_roi)

    model = Model()

    model.setLogger(Logger.IJTOOLBAR_LOGGER)

    settings = Settings(implus)

    set_detector(detector_type, channel_number, settings)
    # settings.detectorFactory = CellposeDetectorFactory()

    # settings.detectorSettings["TARGET_CHANNEL"] = nuclei_chnl
    # settings.detectorSettings["OPTIONAL_CHANNEL_2"] = 0
    # settings.detectorSettings["CELLPOSE_PYTHON_FILEPATH"] = os.path.join(
    #     cellpose_env, "python.exe"
    # )
    # settings.detectorSettings["CELLPOSE_MODEL_FILEPATH"] = os.path.join(
    #     os.environ["USERPROFILE"], ".cellpose", "models"
    # )
    # settings.detectorSettings["CELLPOSE_MODEL"] = PretrainedModel.CYTO2
    # settings.detectorSettings["CELL_DIAMETER"] = 11.0
    # settings.detectorSettings["USE_GPU"] = True
    # settings.detectorSettings["SIMPLIFY_CONTOURS"] = True

    # settings.addAllAnalyzers()
    # spotAnalyzerProvider = SpotAnalyzerProvider(1)
    # spotMorphologyProvider = SpotMorphologyAnalyzerProvider(1)

    # #settings.initialSpotFilterValue=quality_thresh

    # # Add the filter on mean intensity
    # # Here 'true' takes everything ABOVE the mean_int value
    if quality_thresh:
        filter1 = FeatureFilter("QUALITY", Double(quality_thresh), True)
        settings.addSpotFilter(filter1)
    if intensity_thresh:
        filter2 = FeatureFilter(
            "MEAN_INTENSITY_CH" + str(channel_number), Double(intensity_thresh), True
        )
        settings.addSpotFilter(filter2)
    if circularity_thresh:
        filter3 = FeatureFilter("CIRCULARITY", Double(circularity_thresh), True)
        settings.addSpotFilter(filter3)
    if area_thresh:
        filter4 = FeatureFilter("AREA", Double(area_thresh), False)
        settings.addSpotFilter(filter4)

    # Configure tracker
    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
    # settings.addTrackAnalyzer(TrackDurationAnalyzer())
    settings.trackerSettings["LINKING_MAX_DISTANCE"] = 15.0
    settings.trackerSettings["GAP_CLOSING_MAX_DISTANCE"] = 15.0
    settings.trackerSettings["MAX_FRAME_GAP"] = 3
    settings.initialSpotFilterValue = -1.0

    trackmate = TrackMate(model, settings)
    trackmate.computeSpotFeatures(True)
    trackmate.computeTrackFeatures(True)

    ok = trackmate.checkInput()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))
        return

    ok = trackmate.process()
    if not ok:
        if "[SparseLAPTracker] The spot collection is empty." in str(
            trackmate.getErrorMessage()
        ):
            return IJ.createImage(
                "Untitled",
                "8-bit black",
                implus.getWidth(),
                implus.getHeight(),
                implus.getNFrames(),
            )
        else:
            sys.exit(str(trackmate.getErrorMessage()))
            return

    sm = SelectionModel(model)

    exportSpotsAsDots = False
    exportTracksOnly = False
    # implus2.close()
    result = LabelImgExporter.createLabelImagePlus(
        trackmate, exportSpotsAsDots, exportTracksOnly, False
    )
    result.setDimensions(dims[2], dims[3], dims[4])
    implus.setDimensions(dims[2], dims[3], dims[4])
    return result
