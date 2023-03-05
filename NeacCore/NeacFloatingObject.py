from NeacCore.NeacLocation       import NeacLocation
from NeacCore.NeacTrackingPoint  import NeacTrackingPoint
import logging

class NeacFloatingObject(NeacLocation):
    """
        Common class for UFO and SHUTTLE
        http://labomath.free.fr/qcms/seconde/equadroite/droites.pdf

        :param name: Name of the Floating Object.
        :param track: Historical of the tracking positions. Array of NeacTrackingPoint
    """

    #--------------------------------------------------------------------------
    def __init__(self, name):
        NeacLocation.__init__(self)
        self.name    = name
        self.track   = []
        
    #--------------------------------------------------------------------------
    def get_name(self):
        """
            :param mode: None
            :returns: The name of the floating Object
        """
        return self.name

    #--------------------------------------------------------------------------
    def record_track(self, time, lon, lat):
        """
            Create a new 'NeacCore.NeacTrackingPoint' object, set the values, and add the point to the track attribute of the NeacFloatingObject.

            :param time: Time of the tracking
            :param lon: Longitude of the new Tracking Point
            :param lat: Latitude of the new Tracking Point
            :returns: None
        """
        newTP = NeacTrackingPoint()
        newTP.set_time_and_location(time, lon, lat)
        self.track.append(newTP)

    #--------------------------------------------------------------------------
    # Retourne le coefficient directeur de la trajectoire estimée de l'UFO
    def get_a(self):
        a = 0
        if len(self.track) > 2:
            i2 = self.track[len(self.track)-1]
            i1 = self.track[len(self.track)-2]
            if (i2.lon - i1.lon) != 0:
                a = (i2.lat - i1.lat) / (i2.lon - i1.lon)
            else:
                a = 0
        return a

    #--------------------------------------------------------------------------
    def get_b(self):
        b = 0
        if len(self.track) > 2:
            i2 = self.track[len(self.track)-1]
            b = i2.lat - self.get_a() * i2.lon
        return b

    #--------------------------------------------------------------------------
    def get_a_and_b(self):
        a = 0
        b = 0
        if len(self.track) > 2:
            i2 = self.track[len(self.track)-1]
            i1 = self.track[len(self.track)-2]
            logging.debug("i2.lat: " + str(i2.lat) + " - i1.lat: " + str(i1.lat) + " - i2.lon: " + str(i2.lon) + " - i1.lon: " + str(i1.lon))
            if (i2.lon - i1.lon) != 0:
                a = (i2.lat - i1.lat) / (i2.lon - i1.lon)   
            else:
                a = 0
            b = i2.lat - self.get_a() * i2.lon

        logging.debug("getAandB("+self.name+ ") : a=" + str(a) + " b=" + str(b) )
        return a, b

__all__ = [
    'NeacFloatingObject','record_track', 'get_a', 'get_b', 'get_a_and_b'
]