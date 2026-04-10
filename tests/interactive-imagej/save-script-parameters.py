# @ String(label="Username") USERNAME
# @ String(label="Password", style="password") PASSWORD
# @ File(label="Path for results", style="directory") outputPath
# @ Integer threshold
# @ Boolean(label="Yes/No?") choice
# @ RoiManager rm
# @ CommandService command
# @ LogService sjlog

import os

import imcflibs.log
from imcflibs.imagej import misc

imcflibs.log.enable_console_logging()
log = imcflibs.log.LOG

log.warning("Starting...")
misc.save_script_parameters(script_globals=globals(), destination=outputPath)
log.warning("Saved parameters to: %s\script_parameters.txt", outputPath)
