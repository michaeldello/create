"""
 Script name: createutils.py

 Author: Michael Dello
 Description:
    Common items needed across various CREATE scripts and modules
"""
import logging
import time
import os
import sys

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

MODULE_NAME = "create"
MODULE_VERSION = "1.1"

# Some implementations diverge based on OS
THIS_IS_WINDOWS  = True if "nt" in os.name else False

# Logging
OUTPUTDIR   = "logs"
LOGFILENAME = "create-{}.log"
THISLOGFILE = LOGFILENAME.format(time.strftime("%y%m%d_%H%M%S"))
LOGFILEPATH = os.path.join(OUTPUTDIR, THISLOGFILE)

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

logger = logging.getLogger(MODULE_NAME)
logger.setLevel(logging.DEBUG)
# Console handler
ch = logging.StreamHandler(sys.stdout)
# Don't clutter the console
ch.setLevel(logging.INFO)
formatter = \
    logging.Formatter(
        '%(asctime)s - [%(name)17s:%(lineno)-5s] - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logstarted = False

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def startLogging():
    global logstarted
    # File handler
    if not os.path.isdir(OUTPUTDIR):
        os.mkdir(OUTPUTDIR)
    fh = logging.FileHandler(LOGFILEPATH)
    # Everything goes in the log file
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logstarted = True

#------------------------------------------------------------------------------
def loggingIsStarted():
    return logstarted

#------------------------------------------------------------------------------
def flushconsole():
    # Only need to do this if logging is started
    if logstarted:
        ch.flush()

#-------------------------------------------------------------------------------
def logmsg(msg, logger=None, level=logging.DEBUG):
    '''
    Logging facility, because this is a generic/common module, and logging
    during certain functions in this module may need to be supressed in certain
    contexts, provide a way to allow caller to pass in their own logger object
    that uses the python logging API, implemented on their own terms
    '''
    if logger:
        if level == logging.DEBUG:
            logger.debug(msg)
        elif level == logging.INFO:
            logger.info(msg)
        elif level == logging.WARNING:
            logger.warning(msg)
        else:
            # Treat all else as errors
            logger.error(msg)
