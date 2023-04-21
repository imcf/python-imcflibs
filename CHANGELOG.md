# Changelog

<!-- markdownlint-disable MD024 (no-duplicate-header) -->

## 1.3.0

### Added

* `imcflibs.pathtools.join2` can be used to join paths, much like `os.path.join`
  except that it will work with `java.io.File` objects as well (but doesn't
  support more than two path components / parameters).
* `imcflibs.imagej.resultstable` sub-module with the following functions:
  * `imcflibs.imagej.resultstable.add_results_to_resultstable`
  * `imcflibs.imagej.resultstable.get_resultstable`
  * `imcflibs.imagej.resultstable.preset_results_column`
* `imcflibs.imagej.misc.timed_log` for printing log messages with a timestamp.
* Several functions in the `imcflibs.imagej.misc` submodule:
  * `imcflibs.imagej.misc.calculate_mean_and_stdv`
  * `imcflibs.imagej.misc.elapsed_time_since`
  * `imcflibs.imagej.misc.find_focus`
  * `imcflibs.imagej.misc.get_free_memory`
  * `imcflibs.imagej.misc.percentage`
  * `imcflibs.imagej.misc.progressbar`
  * `imcflibs.imagej.misc.setup_clean_ij_environment`
  * `imcflibs.imagej.misc.timed_log`

### Changed

* `imcflibs.strtools.filename` and `imcflibs.pathtools.parse_path` can now also
  work on `java.io.File` objects, which happen to be the type when using
  ImageJ2's *Script Parameter* `@# File`.
* The dict returned by `imcflibs.pathtools.parse_path` now also contains the key
  `basename` that provides the filename without extension.
* `imcflibs.pathtools.parse_path` treats OME-TIFF filenames as special cases now
  in the sense that the `.ome` part is stripped from the `basename` key and
  added to the `ext` key instead (as it is part of the suffix).
* Many improvements / clarifications in function docstrings.
