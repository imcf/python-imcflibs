"""Prevent namespace clashes / race conditions when running in Jython."""

import importlib

# Using `import io` will heavily depend on the state of the Python engine and
# may fail when being used as a library inside Jython (as `io` might be shadowed
# by the Java package with the same name then) with something like this:
## AttributeError: 'javapackage' object has no attribute 'BufferedIOBase'
io = importlib.import_module("io")

try:
    # Python 2: "file" is built-in
    file_types = file, io.IOBase
except NameError:
    # Python 3: "file" fully replaced with IOBase
    file_types = (io.IOBase,)
