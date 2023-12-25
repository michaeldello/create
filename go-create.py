#!/usr/bin/env python3

import argparse
import json
import os
import subprocess

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

STAGE_ORDER_KEY = "stage_order"
DEFAULT_STAGE_ORDER = [
    "build",
    "test",
    "analyze"
]

STEP_ORDER_KEY = "step_order"
DEFAULT_STEP_ORDER = [
    "prep",
    "execute",
    "cleanup"
]

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
def main(args):
    print(
        "-----------------------------------------------------")
    print(f"Using '{args.config}' config")
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
            stages.get(stage,f"ERROR: {stage} missing from stages section")
        # Iterate the steps in each stage
        for step in steporder:
            cmdentries = \
                steps.get(
                    step,
                    f"ERROR: {step} missing from {stage} section")
            # Iterate the cmds in each step
            for cmdentry in cmdentries:
                # Get the command if one is specified
                cmd = cmdentry.get("cmd","")
                # Use shell by default, unless specified otherwise
                executeinshell = cmdentry.get("shell",True)
                print(
                    "-----------------------------------------------------")
                print(
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
                                cwd=cmdentry.get("cwd",None),
                                timeout=cmdentry.get("timeout",None),
                                check=cmdentry.get("check",False),
                                encoding=cmdentry.get("encoding","utf-8"))
                    except Exception as e:
                        print(f"Exception on cmd=[{cmd}]: {str(e)}")
                if cc:
                    print(f"\tFinished cmd\t: {cmd}")
                    print(f"\tReturn code \t: {cc.returncode}")
                    print(
                        "\tCaptured Output\t: {}".format(
                            cc.stdout.replace('\\n', '\n')))
    print(
        "-----------------------------------------------------")
    print("Processing Completed")
    print(
        "-----------------------------------------------------")

#------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        action="store",
                        help="Specify a config from the 'configs/' folder",
                        default="guidance")
    args = parser.parse_args()
    # Go
    main(args)
