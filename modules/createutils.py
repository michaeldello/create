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

logactivated = False

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def activateLogging():
    global logactivated
    # File handler
    if not os.path.isdir(OUTPUTDIR):
        os.mkdir(OUTPUTDIR)
    fh = logging.FileHandler(LOGFILEPATH)
    # Everything goes in the log file
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logactivated = True

#------------------------------------------------------------------------------
def loggingIsActivated():
    return logactivated

#------------------------------------------------------------------------------
def flushconsole():
    # Only need to do this if logging is activated
    if logactivated:
        ch.flush()

#-------------------------------------------------------------------------------
def logmsg(msg, logger=None, level=logging.DEBUG):
    '''
    Logging facility, because this is a generic/common module, and logging
    during certain functions in this module may need to be supressed in certain
    contexts, provide a way to allow caller to pass in their own logger object
    that uses the python logging API, implemented on their own terms
    :param msg: Message to log
    :param logger: logger object to use
    :param level: Logging level per python logging module
    :return:
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

# Use this as a basis to set the worst case timeout on a subprocess, derated
# 20%, if not otherwise overridden
# Based purely on reasonable user experience given worst case operation carried
# out during card prep
WC_CMD_TIMEOUT_IN_SECS = 360

DEFAULT_CMD_RETRIES  = 0
DEFAULT_CMD_DELAY    = 8
#-------------------------------------------------------------------------------
def executeCmdWithRetriesAndOutput(
        cmd,
        expectedreturncode=0,
        expectedOutput=[],
        failonOutput=[],
        retries=DEFAULT_CMD_RETRIES,
        delay=DEFAULT_CMD_DELAY,
        logger=None,
        timeout=WC_CMD_TIMEOUT_IN_SECS,
        cwd=None):
    '''
        Execute the command within current context, verify expected output
        string(s), with configurable retry and delay in-between each attempt

        Returns boolean success, and console output
    '''
    import subprocess
    logmsg("Executing command (raw): " + cmd, logger)
    logmsg(
        "    with timeout = {}".format(
            timeout if timeout else "NONE"), logger)
    success = True
    retry = True
    numretries = 0
    cmdtoexecute = cmd
    # PCR configuration, which executes in executive context,
    # builds up a cmd executable path cache, then executive
    # sends this cache to the PTA layer ... this action
    # processes (i.e., strips) '\' characters because the
    # strings are dumped to a JSON string sent over TCP, which
    # effectively strips those characters from the string ...
    # so during executive side PCR config processing, the path
    # cache entries account for that by adding an extra "level"
    # of '\' characters to existing '\' characters in a cmd's
    # executable's path ... however, those extra '\' characters
    # need to be stripped on the executive side prior to usage
    # in PCR execution
    #
    # Note: the generic command processing is used in both
    # contexts, executive and PTA layer
    while '\\"' in cmdtoexecute:
        logmsg(
            "Stripping extra \\ characters from {}".format(
                cmdtoexecute),
            logger)
        cmdtoexecute = cmdtoexecute.replace('\\"', '\"')
    while retry:
        output = ""
        err = ""
        retry = False
        success = True
        logmsg("About to run subprocess", logger)
        if cwd is not None:
            logmsg(f"    from folder {cwd}", logger)
        parentpid = os.getpid()
        logmsg(f"Parent PID {parentpid}", logger)
        with subprocess.Popen(
                cmdtoexecute,
                # Capture output
                stdout=subprocess.PIPE,
                # Capture errors with output
                stderr=subprocess.STDOUT,
                # Encode output as string instead of binary
                encoding="utf-8",
                errors="backslashreplace",
                shell=True,
                cwd=cwd) as process:
            try:
                logmsg(f"Running PID {process.pid}", logger)
                output, err = process.communicate(timeout=timeout)
                output = f"(stdout): {output}; (stderr): {err}"
            except subprocess.TimeoutExpired:
                success = False
                errmsg = \
                    "FAILURE: {} failed due to timeout after {} seconds".format(
                        cmdtoexecute, timeout)
                # While this is an error, report as warning because this path of
                # execution allows for retries, and ultimately, caller
                # determines error condition
                logmsg(errmsg, logger, logging.error)
                # Kill the process (tree under parent)
                # This method is used because the documented Python behavior
                # of subprocess with PIPEs and timeouts does not work
                # (see https://bugs.python.org/issue31447)
                # The psutil library allows killing a "process tree" in Windows
                psup = psutil.Process(parentpid)
                psucs = psup.children(recursive=True)
                for c in psucs:
                    c.kill()
                psutil.wait_procs(psucs, timeout=1)
                # Because of the timeout, and process is killed, output is
                # likely lost
                logmsg(
                    "Potential output loss due to process being killed",
                    logger)
                output = \
                    "(stdout): {}; (stderr): {}".format(
                        output if output else "",
                        err if err else "")
            except OSError as e:
                success = False
                errmsg = \
                    "OS failed to execute command [{}] due to [{}]".format(
                        cmd, os.strerror(e.errno))
                # While this is an error, report as warning because this path of
                # execution allows for retries, and ultimately, caller
                # determines error condition
                logmsg(errmsg, logger, logging.warning)
            finally:
                # Output may have already been captured in some error cases, if
                # not, capture here
                # Always log the return output
                if output:
                    logmsg(
                        "Executed Command [{}] with Output: [{}]".format(
                            cmd,
                            output),
                        logger)
                else:
                    logmsg("No output captured", logger)
                # Verify the return code matched expected
                if process.returncode == expectedreturncode:
                    logmsg(
                        "Command finished with expected return code {}".format(
                            expectedreturncode),
                        logger)
                else:
                    success = False
                    logmsg(
                        "Command failed on unexpected result [{}]".format(
                            process.returncode if process.returncode else
                                "NONE"),
                        logger)
                cmdfailed = not success
                for failstring in failonOutput:
                    logmsg(
                        "Checking for (fail) [{}] in output".format(failstring),
                         logger)
                    if output and failstring in output:
                        logmsg(
                            "Unexpected string [{}] found in output".format(
                                failstring),
                            logger)
                        cmdfailed = True
                        # Not breaking here to allow full debug information to
                        # be logged
                for checkstring in expectedOutput:
                    logmsg(
                        "Checking for [{}] (raw) in output".format(
                            checkstring),
                        logger)
                    # Make output parsing portable
                    strippedcs = checkstring
                    while '\\"' in strippedcs:
                        logmsg(
                            "Stripping extra \\ characters from {}".format(
                                strippedcs),
                            logger)
                        strippedcs = strippedcs.replace('\\"', '\"')
                    if output:
                        if strippedcs not in output:
                            logmsg(
                                "Expected string [{}] not found in output".format(
                                    checkstring),
                                logger)
                            cmdfailed = True
                            # Not breaking here to allow full debug information
                            # to be logged
                    else:
                        logmsg(
                            "Unexpected empty output, can't check expected",
                            logger)
                        cmdfailed = True
                        break
                if cmdfailed:
                    if numretries < retries:
                        logmsg(
                            f"Retrying command with {retries - numretries} left", logger)
                        numretries += 1
                        retry = True
                        time.sleep(delay)
                    else:
                        # Stop trying and fail
                        logmsg("No more retries, command failed", logger)
                        success = False
    return success, output if output else ""

# -------------------------------------------------------------------------------
def executeCmdWithRetries(
        cmd,
        expectedreturncode=0,
        expectedOutput=[],
        failonOutput=[],
        retries=DEFAULT_CMD_RETRIES,
        delay=DEFAULT_CMD_DELAY,
        logger=None,
        timeout=WC_CMD_TIMEOUT_IN_SECS,
        cwd=None):
    '''
        Execute the command within current context, verify expected output
        string(s), with configurable retry and delay in-between each attempt

        Returns boolean success/failure only
    '''
    return \
        executeCmdWithRetriesAndOutput(
            cmd,
            expectedreturncode,
            expectedOutput,
            failonOutput,
            retries,
            delay,
            logger,
            timeout,
            cwd)[0]
