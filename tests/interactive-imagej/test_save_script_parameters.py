#@ String(label="Username") USERNAME
#@ String(label="Password", style="password") PASSWORD
#@ File(label="Path for results", style="directory") outputPath
#@ Integer threshold
#@ Boolean(label="Yes/No?") choice
#@ RoiManager rm
#@ CommandService command
#@ LogService sjlog

# Prerequisites before running this script in Fiji:
#
# - Drag and drop, and run this script in Fiji.
# - Set parameters in the dialog box.
#
# Expected result: a file named "script_parameters.txt" is written to the
# chosen output directory, with all parameters from the script.

import os
import imcflibs.log
from imcflibs.imagej import misc

imcflibs.log.enable_console_logging()
log = imcflibs.log.LOG

log.warning("Starting...")
misc.save_script_parameters(script_globals=globals(), destination=outputPath)
log.warning("Saved parameters to: %s\script_parameters.txt", outputPath)
