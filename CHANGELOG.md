# python-imcflibs Change Log

<!-- markdownlint-disable MD024 (no-duplicate-header) -->

## 1.3.0

### Added

* `pathtools.join2` can be used to join paths, much like `os.path.join` except
  that it will work with `java.io.File` objects as well (but doesn't support
  more than two path components / parameters).
* `resultstable` sub-module with the following functions:
  * `add_results_to_resultstable`
  * `get_resultstable`
  * `preset_results_column`
* `misc.timed_log` for printing log messages with a timestamp.
* Several functions in the `misc` submodule:
  * `calculate_mean_and_stdv`
  * `elapsed_time_since`
  * `find_focus`
  * `get_free_memory`
  * `percentage`
  * `progressbar`
  * `setup_clean_ij_environment`
  * `timed_log`

### Changed

* `strtools.filename` and `pathtools.parse_path` can now also work on
  `java.io.File` objects, which happen to be the type when using ImageJ2's
  *Script Parameter* `@# File`.
* Many improvements / clarifications in function docstrings.
