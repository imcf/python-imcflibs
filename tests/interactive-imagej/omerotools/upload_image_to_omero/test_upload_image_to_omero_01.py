from imcflibs.imagej import omerotools


error_type = "FileNotFoundError"
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
    error_type = "IOError"

path = "/usr/fancy/path/pony-with-one-horn.tiff"

try:
    # No client needed. Only testing the exception
    omerotools.upload_image_to_omero(None, path, None)
except FileNotFoundError:
    print("Got the expected {}".format(error_type))

print("Test completed!")
