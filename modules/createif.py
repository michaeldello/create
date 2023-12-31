"""
 Script name: createif.py

 Author: Michael Dello
 Description:
    Interface used to execute the main CREATE script
"""

#-------------------------------------------------------------------------------
# Return Codes
#-------------------------------------------------------------------------------

# For use in the code so hard coded values aren't used
RC_SUCCESS = 0
RC_FAILEXC = 255

RCMAP = {
    0: "SUCCESS",
    255: "FAILURE - Unknown/Unexpected"
}


def rc2str(retcode):
    """
        Create a new cmd object based on specified parameters
    """
    return RCMAP.get(retcode,"")


#-------------------------------------------------------------------------------
# Default config settings
#-------------------------------------------------------------------------------

# These can be optionally overridden in a configuration file
#
# Config access keys
CAK_STAGEORDER = "stage_order"
CAK_STEPORDER = "step_order"
#
DEFAULT_STAGE_ORDER = [
    "build",
    "test",
    "analyze"
]
#
DEFAULT_STEP_ORDER = [
    "prep",
    "execute",
    "cleanup"
]

# Prettification
OUTPUT_SEPARATOR = "-----------------------------------------------------"
