"""
 Script name: stages.py

 Author: Michael Dello
 Description:
    Stages classes, defining the various properties and behaviors possible for
    CREATE stages

"""

import createif
import createutils

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Local Variables
#-------------------------------------------------------------------------------

log = createutils.logger.getChild(__name__)

#------------------------------------------------------------------------------
# Reusable Stage Classes
#------------------------------------------------------------------------------
class BaseStage(object):
    '''
        This class describes the API for executing a Stage object.
    '''

    #--------------------------------------------------------------------------
    # Built-in Methods
    #--------------------------------------------------------------------------
    def __init__(self, config={}, logger=None):
        '''
            Common init for all SWUpdaters: set logging object
        '''
        self.log = logger.getChild(__name__) if logger else log
        self.log.debug(
            "Creating {}()".format(self.__class__.__name__))
        # Data members
        self.steps = []

    #--------------------------------------------------------------------------
    # Public Methods
    #--------------------------------------------------------------------------
    def execute(self):
        '''
            Execute sw upgrade/update
        '''
        rc = createif.RC_SUCCESS
        self.log.debug("TBD - Execute configured stage")
        return rc

# -------------------------------------------------------------------------------
def createStage(version=createif.CV_BASIC, config={}, logger=None):
    """
        Create a new cmd object based on specified parameters
    """
    return BaseStage(config, logger)


