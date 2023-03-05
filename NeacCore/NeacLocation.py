class NeacLocation:
    """
        Basic Location Object. Also contain X/Y coordinates based on the screen referential

        :param lon: Longitude. WGS84
        :param lat: Latitude. WGS84
        :param x: X coordinates refering to the screen.
        :param y: Y coordinates refering to the screen.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        self.lon = -0.345611
        self.lat = 49.183902
        self.x = 0
        self.y = 0

    #--------------------------------------------------------------------------
    def set_location(self, lon, lat):
        """
            Set the latitude and longitude for the location object

            :param lon: longitude.
            :param lat: latitude.
            :returns: None.
        """
        self.lon = lon
        self.lat = lat

    #--------------------------------------------------------------------------
    def print(self):
        print ("|Coordinates : ")
        print ("|  lon = " + str(self.lon))
        print ("|  lat = " + str(self.lat))

    #--------------------------------------------------------------------------
    def toString(self):
        return "lon = " + str(self.lon) + " - lat = " + str(self.lat)

    #--------------------------------------------------------------------------
    def get_x(self, coordHelper):
        """
            Compute and returns the X coordinate of the location, based on the screen parameters.

            :param coordHelper: NeacCoordHelper Object.
            :returns: X coordinate.
        """
        self.x, self.y = coordHelper.projPoint(self.lon, self.lat)
        return self.x
        
    #--------------------------------------------------------------------------
    def get_y(self, coordHelper):
        """
            Compute and returns the Y coordinate of the location, based on the screen parameters.

            :param coordHelper: NeacCoordHelper Object.
            :returns: Y coordinate.
        """
        self.x, self.y = coordHelper.projPoint(self.lon, self.lat)
        return self.y

    #--------------------------------------------------------------------------
    def get_xy(self, coordHelper):
        """
            Compute and returns the X and Y coordinates of the location, based on the screen parameters.

            :param NeacCoordHelper coordHelper: NeacCoordHelper Object.
            :returns: X and Y coordinates.
            :rtype: (x,y)
        """
        x = self.getX(coordHelper)
        y = self.getY(coordHelper)
        return x, y 

__all__ = [
    'NeacLocation','set_location', 'get_x', 'get_y', 'get_xy'
]