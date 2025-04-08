# Changelog 🧾

<!-- markdownlint-disable MD024 (no-duplicate-header) -->

## 1.5.0

As this is a major release, not all changes and functions are listed below. For
detailed information, please refer to the updated API documentation.

### Added

* `imcflibs.strtools.pad_number` to pad a number with leading zeros.
* `imcflibs.pathtools.create_directory` to create a new directory at the
  specified path if it does not exist (needed with python 2.7)
* Various additions to `imcflibs.imagej.misc`:
  * `imcflibs.imagej.misc.send_notification_email` to send email notifications
    upon completion of long-running scripts.
    * Sends a mail with job details, such as recipient, file name, execution
      time & an optional message.
    * To enable email notifications, the following preferences must be set in
      `~/.imagej/IJ_Prefs.txt`:
      * .imcf.sender_email: sender's email address.
      * .imcf.smtpserver: the SMTP server used for sending emails.
    * If the sender email or SMTP server is not configured, method logs a
      message and exits.
  * `imcflibs.imagej.misc.sanitize_image_title` to remove special chars and
    various suffixes from an ImagePlus.
  * `imcflibs.imagej.misc.subtract_images` to subtract an image from another.
  * `imcflibs.imagej.misc.close_images` for closing all ImagePluses from a list.
  * `imcflibs.imagej.misc.get_threshold_value_from_method` to get the value that
    a selected AutoThreshold method would be using.
  * `imcflibs.imagej.misc.write_ordereddict_to_csv` to write data from an
    ordered dictionary (or list of ordered dictionaries) to a CSV file.
  * `imcflibs.imagej.misc.save_image_in_format` to save an ImagePlus in a
    specified format, such as ImageJ-TIF or OME-TIFF etc., to a given directory.
  * `imcflibs.imagej.misc.run_imarisconvert` to convert a given file to Imaris
    format using the utility ImarisConvert. Method uses
    `imcflibs.imagej.misc.locate_latest_imaris` to find the path to the Imaris
    installation.
* New functions in `imcflibs.imagej.labelimage`:
  * `imcflibs.imagej.labelimage.cookie_cut_labels` to use a label image as a
    mask for another label image. Objects might get split or merged depending on
    the mask.
  * `imcflibs.imagej.labelimage.binary_to_label` for segmenting a binary image
    to get a label image (2D/3D).
  * `imcflibs.imagej.labelimage.relate_label_images` to relate two label images
    (2D/3D) using the 3D Association plugin from the 3DImageJSuite.
  * `imcflibs.imagej.labelimage.dilate_labels_2d` to dilate a label image slice
    by slice. Works for 2D or 3D images.
* New `imcflibs.imagej.objects3d` submodule, providing:
  * `imcflibs.imagej.objects3d.population3d_to_imgplus` to turn an
    Objects3DPopulation into an ImagePlus (2D/3D).
  * `imcflibs.imagej.objects3d.imgplus_to_population3d` to get the
    Objects3DPopulation from an ImagePlus (2D/3D).
  * `imcflibs.imagej.objects3d.segment_3d_image` to threshold an image into a
    labeled stack.
  * `imcflibs.imagej.objects3d.get_objects_within_intensity` to filter a
    population of 3D objects by intensity.
  * `imcflibs.imagej.objects3d.maxima_finder_3d` to find local maxima in a
    3D image.
  * `imcflibs.imagej.objects3d.seeded_watershed` to perform a seeded watershed
    segmentation on a binary image using seeds points.
* New `imcflibs.imagej.bdv` submodule, providing BigDataViewer related
  functions:
  * New classes:
    * `ProcessingOptions` to store all options on how to process the dataset.
    * `DefinitionOptions` to store all options on how to define the dataset.
  * `imcflibs.imagej.bdv.check_processing_input` to sanitize and clarify the
    acitt input selection.
  * `imcflibs.imagej.bdv.get_processing_settings` to generate the strings needed
    for the processing.
  * `imcflibs.imagej.bdv.backup_xml_files` to create a backup of BDV-XML files.
  * `imcflibs.imagej.bdv.define_dataset_auto` to run "Define Multi-View Dataset"
    using the "Auto-Loader" option.
  * `imcflibs.imagej.bdv.define_dataset_manual` to run "Define Multi-View
    Dataset" using the "Manual Loader" option.
  * `imcflibs.imagej.bdv.resave_as_h5` to resave the dataset in H5 to make it
    compatible with BigDataViewer/BigStitcher.
  * `imcflibs.imagej.bdv.flip_axes` tocall BigStitcher's "Flip Axes" command.
  * `imcflibs.imagej.bdv.phase_correlation_pairwise_shifts_calculation` to
    calculate pairwise shifts using Phase Correlation.
  * `imcflibs.imagej.bdv.filter_pairwise_shifts` for filtering pairwise shifts
    based on different thresholds.
  * `imcflibs.imagej.bdv.optimize_and_apply_shifts` to optimize shifts and apply
    them to a dataset.
  * `imcflibs.imagej.bdv.detect_interest_points` for running the "Detect
    Interest Points" command for registration.
  * `imcflibs.imagej.bdv.interest_points_registration` to run the "Register
    Dataset based on Interest Points" command.
  * `imcflibs.imagej.bdv.duplicate_transformations` for duplicating /
    propagating transformation parameters to other channels.
  * `imcflibs.imagej.bdv.fuse_dataset` to call BigStitcher's "Fuse Multi-View
    Dataset" command.
* New `imcflibs.imagej.trackmate` submodule to provide helper functions to
  interface with Trackmate:
  * Multiple functions to set up Trackmate settings with different detectors,
    such as `cellpose`, `StarDist` or a `log detector`.
  * `imcflibs.imagej.trackmate.spot_filtering` to create settings to  filter
    detected spots based on optional thresholds for quality, area, circularity &
    intensity.
  * `imcflibs.imagej.trackmate.sparse_lap_tracker` to create default settings
    for the sparse LAP tracker.
  * `imcflibs.imagej.trackmate.track_filtering` to create settings to filter
    detected tracks based upon optional distances, such as maximum linking, gap
    closing, track splitting & merging and maximum frame gap.
  * `imcflibs.imagej.trackmate.run_trackmate` to run Fiji's Trackmate plugin on
    an open ImagePlus with given settings, which can be set up with available
    methods in the `imcflibs.imagej.trackmate` submodule. The method then
    returns a label image.
* New `imcflibs.imagej.omerotools` submodule, providing helper functions to
  connect to OMERO using user credentials, fetch and upload an image, retrieve a
  dataset,  or save ROIs to OMERO.
  * `imcflibs.imagej.omerotools.parse_url` to parse the OMERO URL and get a list
    of `ImageWrappers` from multiple image or datasets IDs.
  * `imcflibs.imagej.omerotools.connect` to connect to OMERO using user
    credentials.
  * `imcflibs.imagej.omerotools.fetch_image` to fetch an image from OMERO using
    the image ID.
  * `imcflibs.imagej.omerotools.upload_image_to_omero` to upload a local image
    to OMERO and returning the new image ID.
  * `imcflibs.imagej.omerotools.add_keyvalue_annotation` to add an annotation to
    an OMERO object.
  * `imcflibs.imagej.omerotools.delete_keyvalue_annotations` to delete
    annotations from an OMERO object.
  * `imcflibs.imagej.omerotools.find_dataset` to find a dataset in OMERO using
    the dataset ID.
  * `imcflibs.imagej.get_acquisition_metadata` to get the acquisition metadata
    from an image in OMERO.
  * `imcflibs.imagej.omerotools.get_info_from_original_metadata` to get the
    original metadata from an image in OMERO.
  * `imcflibs.imagej.omerotools.create_table_columns` to create OMERO table
    headings from a list of column names.
  * `imcflibs.imagej.omerotools.upload_array_as_omero_table` to upload a table
    to OMERO.
  * `imcflibs.imagej.omerotools.save_rois_to_omero` to save ROIs to OMERO.
* New `imcflibs.imagej.shading` module for everything background correction.
  * `imcflibs.imagej.shading.simple_flatfield_correction` to perform a
    simple flatfield correction to an ImagePlus.
* `imcflibs.imagej.projection.project_stack` to project a stack using
  different projection methods, such as `max`, `min`, `mean`, `sum` or
  `standard_deviation` using a defined axis.
* `imcflibs.imagej.prefs.set_default_ij_options` to configure ImageJ default
  options for consistency.
* New module `imcflibs.imagej.processing` containing utilities for filtering and thresholding:
  * `imcflibs.imagej.processing.apply_filter` to apply a filter to an
    ImagePlus.
  * `imcflibs.imagej.processing.apply_rollingball_bg_subtraction` to apply a
    rolling ball background subtraction to an ImagePlus.
  * `imcflibs.imagej.processing.apply_threshold` to apply a threshold method to
    an ImagePlus.
  *

## 1.4.0

### Added

* `imcflibs.strtools.sort_alphanumerically` to sort a list of strings taking
  into account numerical values correctly.

### Changed

* `imcflibs.pathtools.listdir_matching` is now using the new
  `sort_alphanumerically()` function from above.

## 1.3.0

### Added

* New functions in `imcflibs.pathtools`:
  * `imcflibs.pathtools.join2` can be used to join paths, much like
    `os.path.join` except that it will work with `java.io.File` objects as well
    (but doesn't support more than two path components / parameters).
  * `imcflibs.pathtools.find_dirs_containing_filetype`
  * `imcflibs.pathtools.folder_size`
* New functions in `imcflibs.imagej.misc`:
  * `imcflibs.imagej.misc.calculate_mean_and_stdv`
  * `imcflibs.imagej.misc.elapsed_time_since`
  * `imcflibs.imagej.misc.find_focus`
  * `imcflibs.imagej.misc.get_free_memory`
  * `imcflibs.imagej.misc.percentage`
  * `imcflibs.imagej.misc.progressbar`
  * `imcflibs.imagej.misc.setup_clean_ij_environment`
  * `imcflibs.imagej.misc.timed_log`
* New `imcflibs.imagej.labelimage` submodule, providing:
  * `imcflibs.imagej.labelimage.filter_objects`
  * `imcflibs.imagej.labelimage.label_image_to_roi_list`
  * `imcflibs.imagej.labelimage.measure_objects_size_shape_2d`
  * `imcflibs.imagej.labelimage.relate_label_images`
* New `imcflibs.imagej.gpu` submodule, providing:
  * `imcflibs.imagej.gpu.erode_labels`
  * `imcflibs.imagej.gpu.dilate_labels`
  * `imcflibs.imagej.gpu.merge_labels`
* New `imcflibs.imagej.resultstable` submodule, providing:
  * `imcflibs.imagej.resultstable.add_results_to_resultstable`
  * `imcflibs.imagej.resultstable.get_resultstable`
  * `imcflibs.imagej.resultstable.preset_results_column`
* New `imcflibs.imagej.roimanager` submodule, providing:
  * `imcflibs.imagej.roimanager.add_rois_to_roimanager`
  * `imcflibs.imagej.roimanager.change_roi_color`
  * `imcflibs.imagej.roimanager.clear_ij_roi_manager`
  * `imcflibs.imagej.roimanager.count_all_rois`
  * `imcflibs.imagej.roimanager.enlarge_all_rois`
  * `imcflibs.imagej.roimanager.extract_color_of_all_rois`
  * `imcflibs.imagej.roimanager.get_roimanager`
  * `imcflibs.imagej.roimanager.load_rois_from_zip`
  * `imcflibs.imagej.roimanager.measure_in_all_rois`
  * `imcflibs.imagej.roimanager.rename_rois_by_number`
  * `imcflibs.imagej.roimanager.rename_rois`
  * `imcflibs.imagej.roimanager.save_rois_to_zip`
  * `imcflibs.imagej.roimanager.scale_all_rois`
  * `imcflibs.imagej.roimanager.select_rois_above_min_intensity`
  * `imcflibs.imagej.roimanager.shift_roi_by_bounding_box`
  * `imcflibs.imagej.roimanager.show_all_rois_on_image`

### Changed

* The functions below now also accept parameters of type `java.io.File` (instead
  of `str`), making them safe for being used directly with variables retrieved
  via ImageJ2's *Script Parameter* `@# File`:
  * `imcflibs.pathtools.parse_path`
  * `imcflibs.strtools.filename`
* Several changes in `imcflibs.pathtools.parse_path`:
  * The returned dict now contains an additional key `basename` that provides
    the filename without extension.
  * OME-TIFF filenames are now treated as special cases in the sense that the
    `.ome` part is stripped from the `basename` key and added to the `ext` key
    instead (as it is part of the suffix).
* `imcflibs.pathtools.listdir_matching` now has an additional optional argument
  `sort` (defaulting to `False`) to request the resulting list to be sorted.
* Many improvements / clarifications in function docstrings.
