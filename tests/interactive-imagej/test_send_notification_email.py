# Prerequisites before running this script in Fiji:
#
# Add the following lines to IJ_Prefs.txt:
#   Linux/Mac: ~/.imagej/IJ_Prefs.txt
#   Windows:   C:\Users\<USERNAME>\.imagej\IJ_Prefs.txt
#
#   .imcf.sender_email=imcf@unibas.ch
#   .imcf.smtpserver=smtp.unibas.ch
#
# Expected result: a mail is sent to nikolaus.ehrenfeuchter@unibas.ch from
# imcf@unibas.ch, with Fiji printing "Successfully sent email to
# <nikolaus.ehrenfeuchter@unibas.ch>".

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
