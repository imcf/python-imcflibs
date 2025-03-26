# Test the send_notification_email function

```Python
from imcflibs.imagej.misc import send_notification_email

from imcflibs.log import LOG as log
from imcflibs.log import enable_console_logging
from imcflibs.log import set_loglevel


enable_console_logging()
set_loglevel(2)


# see if logging works:
log.warn("warn")
log.debug("DEBUG")

send_notification_email(
    job_name="my job",
    recipient="nikolaus.ehrenfeuchter@unibas.ch",
    filename="magic-segmentation.py",
    total_execution_time="5 years",
)

log.info("DONE")
```
