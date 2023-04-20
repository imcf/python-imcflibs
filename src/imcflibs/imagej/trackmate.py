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
    quality_thresh=None,
    intensity_thresh=None,
    circularity_thresh=None,
    area_thresh=None,
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
