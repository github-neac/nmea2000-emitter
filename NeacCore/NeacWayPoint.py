from NeacCore.NeacLocation  import NeacLocation
from NeacCore.NeacConstant  import NAVIGATION_MODE
import logging

class NeacWayPoint(NeacLocation):
    iconSize = 4
    
    def __init__(self, name=""):
        NeacLocation.__init__(self)
        self.name        = name
        self.mode        = NAVIGATION_MODE.DP


    def set_mode(self, mode : NAVIGATION_MODE):
        self.mode = NAVIGATION_MODE[mode]
        logging.debug ("NeacWayPoint(" + self.name + ").setMode(mode="+ self.mode.name + ")")


    def get_mode_str(self):
        if self.mode ==NAVIGATION_MODE.DP:
            return "Dynamic Pos."
        elif self.mode ==NAVIGATION_MODE.CRUISE:
            return "Cruise"
        elif self.mode ==NAVIGATION_MODE.AVOID:
            return "Avoid"
        elif self.mode ==NAVIGATION_MODE.DOCKING:
            return "Docking"
        elif self.mode ==NAVIGATION_MODE.UNDOCKING:
            return "Undocking"

    def get_drawing_information(self, coordHelper):
        x = self.getX(coordHelper)
        y = self.getY(coordHelper) 

        return {"name"     : self.name,
                "x"        : x,
                "y"        : y,
                "mode"     : self.mode.name,
                "lat"      : self.lat,
                "lon"      : self.lon}
