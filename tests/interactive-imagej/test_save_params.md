# Testing script for misc.save_script_parameters()

```python
# @ String(label="Password", description="please enter your password", style="password") PASSWORD
# @ String(label="USERNAME", description="please enter your USR") USERNAME
# @ File(label="Path for storage", style="directory") outputPath
# @ Integer threshold
# @ Boolean taDa
# @ RoiManager rm
# @ CommandService command
# @ LogService sjlog

import os
from imcflibs.imagej import misc, omerotools
    
misc.save_script_parameters(outputPath, script_globals=globals())
print("Saved params")
```
