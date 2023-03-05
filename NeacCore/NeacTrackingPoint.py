from NeacCore.NeacLocation  import NeacLocation

from datetime import datetime

class NeacTrackingPoint(NeacLocation):
    """
        Tracking Point Object

        :param time: tracking timestamp.
    """
    
    #--------------------------------------------------------------------------
    def __init__(self):
        NeacLocation.__init__(self)
        self.time        = datetime.now()

    #--------------------------------------------------------------------------
    def set_time_and_location(self, time, lon, lat):
        """
            Set the timestamp and the coordinates on the tracking point. 

            :param time: datime.time. Timestamp
            :param float lon: Longitude
            :param float lat: Latitude
        """
        #logging.debug ("NeacTrackingPoint(" + str(self.time) + ").set_location(lat="+ str(lat) + " lon=" + str(lon) + ")")
        self.time = time
        self.set_location(lon, lat)


    #--------------------------------------------------------------------------
    def draw_tracking_point(self, coordHelper):
        """
            Returns a JSON containing all the necessary information to draw the point. 

            :returns: JSON
        """
        x = self.getX(coordHelper)
        y = self.getY(coordHelper) 

        return {"time"     : self.time,
                "x"        : x,
                "y"        : y,
                "lat"      : self.lat,
                "lon"      : self.lon}

__all__ = [
    'NeacTrackingPoint','set_time_and_location', 'get_xy', 'draw_tracking_point'
]