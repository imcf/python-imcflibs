# Testing script for misc.save_script_parameters()

```Python
#@ String(label="Username") USERNAME
#@ String(label="Password", style="password") PASSWORD
#@ File(label="Path for results", style="directory") outputPath
#@ Integer threshold
#@ Boolean(label="Yes/No?") choice
#@ RoiManager rm
#@ CommandService command
#@ LogService sjlog

import os
from imcflibs.imagej import misc, omerotools

misc.save_script_parameters(outputPath, script_globals=globals())
print("Saved params")
```
