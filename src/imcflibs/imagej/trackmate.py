import os
import sys

from fiji.plugin.trackmate import Logger, Model, SelectionModel, Settings, TrackMate
from fiji.plugin.trackmate.action import LabelImgExporter
from fiji.plugin.trackmate.cellpose import CellposeDetectorFactory
from fiji.plugin.trackmate.cellpose.CellposeSettings import PretrainedModel
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.features import FeatureFilter
from fiji.plugin.trackmate.stardist import StarDistDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import LAPUtils, SparseLAPTrackerFactory

from ij import IJ

from java.lang import Double

from .. import pathtools


def cellpose_detector(
    imageplus,
    cellpose_env_path,
    model_to_use,
    obj_diameter,
    target_channel,
    optional_channel=0,
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
    target_channel : int
        Index of the channel to use for segmentation.
    optional_channel : int, optional
        Index of the secondary channel to use for segmentation, by default 0.
    use_gpu : bool, optional
        Boolean for GPU usage, by default True.
    simplify_contours : bool, optional
        Boolean for simplifying the contours, by default True.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.

    Example
    -------
    >>> settings = cellpose_detector(
    ...    imageplus=imp,
    ...    cellpose_env_path="D:/CondaEnvs/cellpose",
    ...    model_to_use="NUCLEI",
    ...    obj_diameter=23.0,
    ...    target_channel=1,
    ...    optional_channel=0
    ... )
    """
    settings = Settings(imageplus)

    settings.detectorFactory = CellposeDetectorFactory()
    settings.detectorSettings["TARGET_CHANNEL"] = target_channel
    # set optional channel to 0, will be overwritten if needed:
    settings.detectorSettings["OPTIONAL_CHANNEL_2"] = optional_channel

    settings.detectorSettings["CELLPOSE_PYTHON_FILEPATH"] = pathtools.join2(
        cellpose_env_path, "python.exe"
    )
    settings.detectorSettings["CELLPOSE_MODEL_FILEPATH"] = os.path.join(
        os.environ["USERPROFILE"], ".cellpose", "models"
    )
    input_to_model = {
        "nuclei": PretrainedModel.NUCLEI,
        "cyto": PretrainedModel.CYTO,
        "cyto2": PretrainedModel.CYTO2,
    }
    if model_to_use.lower() in input_to_model:
        selected_model = input_to_model[model_to_use.lower()]
    else:
        print("Selected Model Does Not Exist")
        return

    settings.detectorSettings["CELLPOSE_MODEL"] = selected_model
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
    target_channel,
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
    target_channel : int
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
    settings.detectorSettings["TARGET_CHANNEL"] = target_channel
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
        Threshold to use for area filtering of the spots, keep None with LoG Detector -
        by default also None.
        If the threshold is positive, will exclude everything below the value.
        If the threshold is negative, will exclude everything above the value.
    circularity_thresh : float, optional
        Threshold to use for circularity thresholding (needs to be between 0 and 1, keep None with LoG Detector)
        - by default None.
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
        filter_spot = FeatureFilter(
            "QUALITY",
            Double(abs(quality_thresh)),
            quality_thresh >= 0,
        )
        settings.addSpotFilter(filter_spot)
    if area_thresh:  # Keep none for log detector
        filter_spot = FeatureFilter("AREA", Double(abs(area_thresh)), area_thresh >= 0)
        settings.addSpotFilter(filter_spot)
    if circularity_thresh:  # has to be between 0 and 1, keep none for log detector
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


def sparse_lap_tracker(settings):
    """Create a sparse LAP tracker with default settings.

    Parameters
    ----------
    settings : fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """

    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()

    return settings


def track_filtering(
    settings,
    link_max_dist=15.0,
    gap_closing_dist=15.0,
    max_frame_gap=3,
    track_splitting_max_dist=None,
    track_merging_max_distance=None,
):
    """Add track filtering for different features to the settings dictionary.

    Parameters
    ----------
    settings : fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    link_max_dist : float, optional
        Maximal displacement of the spots, by default 0.5.
    gap_closing_dist : float, optional
        Maximal distance for gap closing, by default 0.5.
    max_frame_gap : int, optional
        Maximal frame interval between spots to be bridged, by default 2.
    track_splitting_max_dist : int, optional
        Maximal frame interval for splitting tracks, by default None.
    track_merging_max_distance : int, optional
        Maximal frame interval for merging tracks , by default None.

    Returns
    -------
    fiji.plugin.trackmate.Settings
        Dictionary containing all the settings to use for TrackMate.
    """
    # NOTE: `link_max_dist` and `gap_closing_dist` must be double!
    settings.trackerSettings["LINKING_MAX_DISTANCE"] = link_max_dist
    settings.trackerSettings["GAP_CLOSING_MAX_DISTANCE"] = gap_closing_dist
    settings.trackerSettings["MAX_FRAME_GAP"] = max_frame_gap
    if track_splitting_max_dist:
        settings.trackerSettings["ALLOW_TRACK_SPLITTING"] = True
        settings.trackerSettings["SPLITTING_MAX_DISTANCE"] = track_splitting_max_dist
    if track_merging_max_distance:
        settings.trackerSettings["ALLOW_TRACK_MERGING"] = True
        settings.trackerSettings["MERGING_MAX_DISTANCE"] = track_merging_max_distance

    return settings


def run_trackmate(
    implus,
    settings,
    crop_roi=None,
):
    # sourcery skip: merge-else-if-into-elif, swap-if-else-branches
    """Function to run TrackMate on already opened data.

    Parameters
    ----------
    implus : ij.ImagePlus
        ImagePlus image on which to run Trackmate.
    settings : fiji.plugin.trackmate.Settings
        Settings to use for TrackMate, see detector methods for different settings.
    crop_roi : ij.gui.Roi, optional
        ROI to crop on the image, by default None.

    Returns
    -------
    ij.ImagePlus
        Labeled image with all the objects belonging to the same tracks having
        the same label.
    """

    dims = implus.getDimensions()
    cal = implus.getCalibration()

    if implus.getNSlices() > 1:
        implus.setDimensions(dims[2], dims[4], dims[3])

    if crop_roi is not None:
        implus.setRoi(crop_roi)

    model = Model()

    model.setLogger(Logger.IJTOOLBAR_LOGGER)

    # Configure tracker
    # settings.addTrackAnalyzer(TrackDurationAnalyzer())
    settings.initialSpotFilterValue = -1.0

    trackmate = TrackMate(model, settings)
    trackmate.computeSpotFeatures(True)
    trackmate.computeTrackFeatures(True)

    if not settings.trackerFactory:
        # Create a Sparse LAP Tracker if no Tracker has been created
        settings = sparseLAP_tracker(settings)

    ok = trackmate.checkInput()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))

    ok = trackmate.process()
    if not ok:
        if "[SparseLAPTracker] The spot collection is empty." in str(
            trackmate.getErrorMessage()
        ):
            new_imp = IJ.createImage(
                "Untitled",
                str(implus.getBitDepth()) + "-bit black",
                implus.getWidth(),
                implus.getHeight(),
                implus.getNFrames(),
            )
            new_imp.setCalibration(cal)

            return new_imp

        else:
            sys.exit(str(trackmate.getErrorMessage()))

    SelectionModel(model)

    exportSpotsAsDots = False
    exportTracksOnly = False
    # implus2.close()
    label_imp = LabelImgExporter.createLabelImagePlus(
        trackmate, exportSpotsAsDots, exportTracksOnly, False
    )
    label_imp.setCalibration(cal)
    label_imp.setDimensions(dims[2], dims[3], dims[4])
    implus.setDimensions(dims[2], dims[3], dims[4])

    return label_imp
