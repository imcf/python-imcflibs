# Changelog 🧾

<!-- markdownlint-disable MD024 (no-duplicate-header) -->

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
