# python-imcflibs Change Log

<!-- markdownlint-disable MD024 (no-duplicate-header) -->

## 1.3.0

### Added

* `pathtools.join2` can be used to join paths, much like `os.path.join` except
  that it will work with `java.io.File` objects as well (but doesn't support
  more than two path components / parameters).)

### Changed

* `strtools.filename` and `pathtools.parse_path` can now also work on
  `java.io.File` objects, which happen to be the type when using ImageJ2's
  *Script Parameter* `@# File`.
