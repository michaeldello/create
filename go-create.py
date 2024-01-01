#!/usr/bin/env python3
"""
  Script name: go-create.py

  Author: Michael Dello
  Description:
     CLI access to the CREATE functionality

     CREATE - Configurable Reusable Extensible Automation Tinkering Executive

     Execution is controlled by a configuration file specifying the parameters
     and options for executing commands on the host.

     Interface can be obtained using the -h/--help CLI option, or analyzing the
     __main__ program in this file.
"""
import argparse
import json
import glob
import logging
import os
import subprocess
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),"modules"))

import createif
import createutils

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

# These can be optionally overridden in a configuration file
STAGE_ORDER_KEY = createif.CAK_STAGEORDER
STEP_ORDER_KEY = createif.CAK_STEPORDER
#
DEFAULT_STAGE_ORDER = createif.DEFAULT_STAGE_ORDER
DEFAULT_STEP_ORDER = createif.DEFAULT_STEP_ORDER
#
OUTPUT_SEPARATOR = createif.OUTPUT_SEPARATOR

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

log = createutils.logger.getChild(__name__)

#------------------------------------------------------------------------------
def clearLogs():
    log.info(f"Clearing {createutils.OUTPUTDIR}/...")
    files = \
        glob.glob(
            os.path.join(
                createutils.OUTPUTDIR, createutils.LOGFILENAME.format("*")))
    for file in files:
        if createutils.loggingIsStarted() and \
                (createutils.THISLOGFILE not in file):
            os.remove(file)

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
def main(args):
    """
    Iterate through the specified configuration and execute the stages
    """
    retcode = createif.RC_SUCCESS
    try:
        createutils.startLogging()
        if args.clear_logs:
            clearLogs()
        log.info(OUTPUT_SEPARATOR)
        log.info(f"Using '{args.config}' config")
        with (open(os.path.join("configs", f"{args.config}.json")) as cf):
            # Load the execution map from the configuration
            execmap = json.load(cf)
        stageorder = execmap.get(STAGE_ORDER_KEY,DEFAULT_STAGE_ORDER)
        steporder = execmap.get(STEP_ORDER_KEY,DEFAULT_STEP_ORDER)
        stages = \
            execmap.get("stages", "ERROR: Stages section missing from config")
        # Iterate the stages
        for stage in stageorder:
            steps = \
                stages.get(stage, f"ERROR: {stage} missing from stages section")
            # Iterate the steps in each stage
            for step in steporder:
                cmdentries = \
                    steps.get(
                        step,
                        f"ERROR: {step} missing from {stage} section")
                # Iterate the cmds in each step
                for cmdentry in cmdentries:
                    # Get the command if one is specified
                    cmd = cmdentry.get("cmd", "")
                    # Use shell by default, unless specified otherwise
                    executeinshell = cmdentry.get("shell", True)
                    log.info(OUTPUT_SEPARATOR)
                    log.info(
                        "Executing: [stage = {}] - [step = {}] - [cmd = {}]".format(
                            stage,
                            step,
                            cmd if cmd else '(No cmd specified)'))
                    cc = None
                    if cmd:
                        try:
                            cc = \
                                subprocess.run(
                                    cmd if executeinshell else cmd.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=executeinshell,
                                    cwd=cmdentry.get("cwd", None),
                                    timeout=cmdentry.get("timeout", None),
                                    check=cmdentry.get("check", True),
                                    encoding=cmdentry.get("encoding", "utf-8"))
                        except Exception as e:
                            log.error(f"Exception on cmd=[{cmd}]: {str(e)}")
                            retcode = createif.RC_FAILEXC
                    if cc:
                        log.info(f"\tFinished cmd\t: {cmd}")
                        log.info(f"\tReturn code \t: {cc.returncode}")
                        log.info(
                            "\tCaptured Output\t: {}".format(
                                cc.stdout.replace('\\n', '\n')))
    except Exception as e:
        log.info(OUTPUT_SEPARATOR)
        log.error(
            f"Execution failed on exception: {str(e)}")
        retcode = createif.RC_FAILEXC
    log.info(OUTPUT_SEPARATOR)
    if retcode == createif.RC_SUCCESS:
        log.info(f"{os.path.basename(__file__)} SUCCEEDED")
    else:
        log.info(
            "{} FAILED: return code = {} ({}) -- see {}".format(
                os.path.basename(__file__),
                retcode,
                createif.rc2str(retcode),
                createutils.LOGFILEPATH))
    log.info(OUTPUT_SEPARATOR)
    # Flush console in case this is used in the context of another script
    createutils.flushconsole()
    return retcode

#------------------------------------------------------------------------------
if __name__ == '__main__':
    """
        Set up the CLI separately to decouple
        main function from CLI. This allows
        the main function to be imported in
        other scripts as an app handler, if
        needed
    """
    rc = createif.RC_FAILEXC
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version",
        version=f'{createutils.MODULE_NAME}-v{createutils.MODULE_VERSION}')
    parser.add_argument(
        "-cl", "--clear-logs", action="store_true",
        help=f"Optionally clear the {createutils.OUTPUTDIR} folder")
    parser.add_argument('-c', '--config',
                        action="store",
                        help="Specify a config from the 'configs/' folder",
                        default="guidance")
    # Set parser function to run as main
    parser.set_defaults(func=main)
    args = parser.parse_args()
    # Go!
    try:
        rc = args.func(args)
    except Exception as e:
        sys.stderr.write("Immediate exception: " + str(e))
    exit(rc)