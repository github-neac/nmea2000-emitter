import math
from pyproj                 import Transformer, Geod
from geographiclib.geodesic import Geodesic

# ----------------------------------------------------------------------------------------------------------------
def profile(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        from line_profiler import LineProfiler
        prof = LineProfiler()
        try:
            return prof(func)(*args, **kwargs)
        finally:
            prof.print_stats()

    return wrapper
    
# ----------------------------------------------------------------------------------------------------------------
class NeacCoordHelper:
    """
        Helper to manage conversions from x/y to lat/lon and vice versa. 

        https://pypi.org/project/geographiclib/
    """
    pyprojTransformer = None
    ratio             = 1

    # Coordonnnées des coins de la carte affichée :
    topLat    = 0
    bottomLat = 0
    leftLon   = 0
    rightLon  = 0

    lambTop    = 0
    lambLeft   = 0
    lambRight  = 0
    lambBottom = 0

    scrTop    = 0
    scrLeft   = 0
    scrRight  = 0
    scrBottom = 0
    
    # -------------------------------------------------------------------------
    def __init__(self, config):
        self.scrRight  = config.map.screenWidth
        self.scrBottom = config.map.screenHeight

        self.center_lat = config.map.map_lat
        self.center_lon = config.map.map_lon
        self.distance   = 500
        self.ratio      = config.map.screenWidth / config.map.screenHeight

        self.geod = Geodesic.WGS84 # https://pypi.org/project/geographiclib/


    # -------------------------------------------------------------------------
    def compute_ratio(self):
        """
            Calcul du ratio d'affichage de l'écran (La proportion largeur/Hauteur de l'écran doit être la même que celle de la zone de la carte)

            WGS84        = EPSG:4326
            Lambert Nord = EPSG:27561
            Lambert FR   = EPSG:2154
        """

        E_lon, E_lat = self.getCoordFromDistanceAndAngle(self.center_lon, self.center_lat, self.distance, 90)
        W_lon, W_lat = self.getCoordFromDistanceAndAngle(self.center_lon, self.center_lat, self.distance, 270)
        N_lon, N_lat = self.getCoordFromDistanceAndAngle(self.center_lon, self.center_lat, self.distance/self.ratio, 0)
        S_lon, S_lat = self.getCoordFromDistanceAndAngle(self.center_lon, self.center_lat, self.distance/self.ratio, 180)
    
        self.topLat    = N_lat
        self.bottomLat = S_lat
        self.leftLon   = W_lon
        self.rightLon  = E_lon

        self.pyprojTransformer = Transformer.from_crs("EPSG:4326", "EPSG:27561", always_xy=True)

        self.lambLeft,  self.lambTop    = self.pyprojTransformer.transform(self.leftLon,    self.topLat)
        self.lambRight, self.lambBottom = self.pyprojTransformer.transform(self.rightLon, self.bottomLat)

    # -------------------------------------------------------------------------
    def projPoint(self, lon, lat):
        """
            Returns x/y from lon/lat

            :param float lon: Longitude
            :param float lat: Latitude
            :returns: [x,y]
        """
        point = self.pyprojTransformer.transform(lon, lat)
        x = math.floor((point[0] - self.lambLeft)  / (self.lambRight  - self.lambLeft) * self.scrRight )
        y = math.floor((point[1] - self.lambTop)   / (self.lambBottom - self.lambTop)  * self.scrBottom )
        return [x,y]

    # -------------------------------------------------------------------------
    def projXY(self, x, y):
        """
            Returns lon/lat from x/y

            :param float x: X Screen Coordinate
            :param float y: Y Screen Coordinate
            :returns: [lon,lat]
        """

        x = (x * (self.lambRight  - self.lambLeft)) / self.scrRight + self.lambLeft
        y = (y * (self.lambBottom - self.lambTop))  / self.scrBottom + self.lambTop

        pyprojTransformer = Transformer.from_crs("EPSG:27561", "EPSG:4326", always_xy=True)
        point = pyprojTransformer.transform(x, y)
        return [point[0],point[1]]

    # -------------------------------------------------------------------------
    def computeDistanceAndAzimut(self, lon0, lat0, lon1, lat1):
        """
            Compute Distance and Azimut between 2 points .
            See https://fr.qaz.wiki/wiki/Azimuth :  Azimuth Cartographique

            :param float lon0: Longitude start point
            :param float lat0: Latitude start point
            :param float lon1: Longitude end point
            :param float lat1: Latitude end point
            :returns: Forward azimuth, Back azimuth, distance between the 2 points (in meters)
        """
        geod = Geod(ellps='WGS84')
        azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
        if azimuth1 < 0:
            azimuth1 = azimuth1 + 360
        return azimuth1, azimuth2, distance

    # -------------------------------------------------------------------------
    def compute_range_from_m_to_pixel(self, range):
        """
            Convert a distance from meters to a number of pixels to be displayed on the screen.

            :param float range: Distance in meters.
            :returns: Number of pixels on the screen to represent the distance in meters. 
        """
        newLon, newLat = self.getCoordFromDistanceAndAngle(-0.337851, 49.183854,range, 90)
        x1, y1 = self.projPoint(-0.337851, 49.183854)
        x2, y2 = self.projPoint(newLon, newLat)
        return x2-x1

    # -------------------------------------------------------------------------
    def getCoordFromDistanceAndAngle(self, lon, lat, distance, angle):
        """
            Returns lon/lat from a position + distance + angle

            :param float lon: Longitude
            :param float lat: Latitude
            :param float distance: Distance in meters
            :param float angle: Angle in Degrees 
            :returns: lon,lat
        """
        g = self.geod.Direct(lat, lon, angle, distance)
        return g['lon2'], g['lat2']


__all__ = [
    'NeacCoordHelper','compute_range_from_m_to_pixel', 'computeDistanceAndAzimut', 'getCoordFromDistanceAndAngle', 'projPoint', 'compute_ratio', 'projXY'
]