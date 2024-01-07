"""
 Script name: commands.py

 Author: Michael Dello
 Description:
    CREATE command abstractions
"""
import os
import psutil
import subprocess
import time

import createif
import createutils

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

# To avoid execution hang, cap the default worst case timeout to 1 hour (can
# be overridden)
DEFAULT_CMD_TIMEOUT_IN_SECS = 360

DEFAULT_CMD_RETRIES = 0
DEFAULT_CMD_DELAY = 8

#-------------------------------------------------------------------------------
# Local Variables
#-------------------------------------------------------------------------------

log = createutils.logger.getChild(__name__)

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------
class BaseCommand(object):
    """
        This class describes the base object for an executable command in the
        CREATE framework.
    """

    #---------------------------------------------------------------------------
    # Constants
    #---------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Built-in Methods
    #--------------------------------------------------------------------------
    def __init__(self, config={}, logger=None):
        '''
            Common init for all command objects
        '''
        self.log = logger.getChild(__name__) if logger else log

    #--------------------------------------------------------------------------
    # Private Methods
    #--------------------------------------------------------------------------
    def __executeCmd(
            self,
            cmd,
            expectedreturncode=0,
            expectedOutput=[],
            failonOutput=[],
            retries=DEFAULT_CMD_RETRIES,
            delay=DEFAULT_CMD_DELAY,
            timeout=DEFAULT_CMD_TIMEOUT_IN_SECS,
            cwd=None):
        '''
            Execute the command within current context, verify expected output
            string(s), with configurable retry and delay in-between each attempt

            Returns boolean success, and console output
        '''
        self.log.debug("Executing command (raw): " + cmd)
        self.log.debug(
            "    with timeout = {}".format(
                timeout if timeout else "NONE"))
        success = True
        retry = True
        numretries = 0
        cmdtoexecute = cmd.replace('\\"', '\"')
        while retry:
            output = ""
            err = ""
            retry = False
            success = True
            self.log.debug("About to run subprocess")
            if cwd is not None:
                self.log.debug(f"    from folder {cwd}")
            parentpid = os.getpid()
            self.log.debug(f"Parent PID {parentpid}")
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
                    self.log.debug(f"Running PID {process.pid}")
                    output, err = process.communicate(timeout=timeout)
                    output = f"(stdout): {output}; (stderr): {err}"
                except subprocess.TimeoutExpired:
                    success = False
                    errmsg = \
                        "FAILURE: {} failed; timeout after {} seconds".format(
                            cmdtoexecute, timeout)
                    self.log.error(errmsg)
                    # Kill the process tree under parent
                    # The documented Python behavior
                    # of subprocess with PIPEs and timeouts does not work
                    # (https://bugs.python.org/issue31447)
                    # The psutil library can portably kill a "process tree"
                    psup = psutil.Process(parentpid)
                    psucs = psup.children(recursive=True)
                    for c in psucs:
                        c.kill()
                    psutil.wait_procs(psucs, timeout=1)
                    # Because of the timeout, and process is killed, output is
                    # likely lost
                    output = \
                        "(stdout): {}; (stderr): {}".format(
                            output if output else "no output, process killed",
                            err if err else "")
                except OSError as e:
                    success = False
                    errmsg = \
                        "OS failed to execute command [{}] due to [{}]".format(
                            cmd, os.strerror(e.errno))
                    # While this is an error, report as warning because this
                    # path of execution allows for retries, and ultimately,
                    # caller determines error condition
                    self.log.warning(errmsg)
                finally:
                    # Output may have already been captured in some error cases,
                    # if not, capture here
                    # Always log the return output
                    if output:
                        self.log.debug(
                            "Executed Command [{}] with Output: [{}]".format(
                                cmd,
                                output))
                    else:
                        self.log.debug("No output captured")
                    # Verify the return code matched expected
                    if process.returncode == expectedreturncode:
                        self.log.debug(
                            "Cmd finished w/ expected return code {}".format(
                                expectedreturncode))
                    else:
                        success = False
                        self.log.debug(
                            "Command failed on unexpected result [{}]".format(
                                process.returncode if process.returncode else
                                    "NONE"))
                    cmdfailed = not success
                    for failstring in failonOutput:
                        self.log.debug(
                            "Checking for (fail) [{}] in output".format(
                                failstring))
                        if output and failstring in output:
                            self.log.debug(
                                "Unexpected string [{}] found in output".format(
                                    failstring))
                            cmdfailed = True
                            # Not breaking here to allow full debug information
                            # to be logged
                    for checkstring in expectedOutput:
                        self.log.debug(
                            "Checking for [{}] (raw) in output".format(
                                checkstring))
                        # Make output parsing portable
                        strippedcs = checkstring
                        while '\\"' in strippedcs:
                            self.log.debug(
                                "Stripping extra \\ characters from {}".format(
                                    strippedcs))
                            strippedcs = strippedcs.replace('\\"', '\"')
                        if output:
                            if strippedcs not in output:
                                self.log.debug(
                                    "Expected string [{}] not in output".format(
                                        checkstring))
                                cmdfailed = True
                                # Not breaking here to allow full debug
                                # information to be logged
                        else:
                            self.log.debug(
                                "Unexpected empty output, can't check expected")
                            cmdfailed = True
                            break
                    if cmdfailed:
                        if numretries < retries:
                            self.log.debug(
                                "Retrying command with {} left".format(
                                    retries - numretries))
                            numretries += 1
                            retry = True
                            time.sleep(delay)
                        else:
                            # Stop trying and fail
                            self.log.debug("No more retries, command failed")
                            success = False
        return success, output if output else ""

# -------------------------------------------------------------------------------
def createcmd(version=createif.CV_BASIC, config={}, logger=None):
    """
        Create a new cmd object based on specified parameters
    """
    return BaseCommand(config, logger)
