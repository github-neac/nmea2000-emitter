from enum                    import Enum

class NAVIGATION_MODE(Enum):
    """
        This Enum represents the current navigation mode of the shuttle. 

        **DP**        : Dynamic Positionning. The shuttle is static

        **DOCKING**   : The shuttle is currently docking

        **UNDOCKING** : The shuttle is currently undocking

        **CRUISE**    : The shuttle is in standard cruising mode

        **AVOID**     : The shuttle is currently avoiding an Ufo

    """
    DP        = 1
    DOCKING   = 2
    UNDOCKING = 3
    CRUISE    = 4
    AVOID     = 5


class MAP_STATE(Enum):
    """
        This Enum represents the current running status of the map simulator (or replay). 

        **DP**        : Dynamic Positionning. The shuttle is static

        **DOCKING**   : The shuttle is currently docking

        **UNDOCKING** : The shuttle is currently undocking

        **CRUISE**    : The shuttle is in standard cruising mode

        **AVOID**     : The shuttle is currently avoiding an Ufo

    """
    INIT    = 1
    RUNNING = 2
    PAUSE   = 3


class DRC_MODE(Enum):
    """
        This enum represents the currently analysis of Ufo Collsion Risk.

        **IGNORE**   : The Ufo is not on the route. No risk

        **WARNING**  : The Ufo is potentially on the route, but currently no CPA clearly defined

        **RISK**     : If nothing is changed, collision is possible between the Ufo and the shuttle. 
    """
    IGNORE   = 1
    WARNING  = 2
    RISK     = 3

# ---- Sphinx objects to document:
__all__ = ['NAVIGATION_MODE', 'DRC_MODE']