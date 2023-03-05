from pyproj         import CRS
from pyproj         import Transformer, Geod
#from geopy.distance import distance  # Pas utilisé pour le moment. Pourrait servir à calculer une distance. 
import math
import logging

from NeacCore.NeacConfig    import NeacConfig

class NeacCoordHelper:
    """
        Helper to manage conversions from x/y to lat/lon and vice versa. 
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
    def __init__(self, screenSize):
        self.scrRight  = screenSize[0]
        self.scrBottom = screenSize[1]


    # -------------------------------------------------------------------------
    def compute_ratio(self):
        """
            Calcul du ratio d'affichage de l'écran (La proportion largeur/Hauteur de l'écran doit être la même que celle de la zone de la carte)

            WGS84        = EPSG:4326
            Lambert Nord = EPSG:27561
            Lambert FR   = EPSG:2154
        """
        self.pyprojTransformer = Transformer.from_crs("EPSG:4326", "EPSG:27561", always_xy=True)

        self.lambLeft,  self.lambTop    = self.pyprojTransformer.transform(self.leftLon,    self.topLat)
        self.lambRight, self.lambBottom = self.pyprojTransformer.transform(self.rightLon, self.bottomLat)

        self.ratio     = abs((self.lambRight-self.lambLeft) / (self.lambBottom-self.lambTop))
        self.scrBottom = self.scrRight / self.ratio

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
    def getCoordFromDistanceAndAngle(self, lon, lat, distance, angle):
        """
            Returns lon/lat from a position + distance + angle

            :param float lon: Longitude
            :param float lat: Latitude
            :param float distance: Distance in meters
            :param float angle: Angle in Degrees 
            :returns: lon,lat
        """
        a      = math.radians((angle - 90) * -1)  # degrees
        lat0   = math.cos(math.pi / 180.0 * lat)
        newLon = lon + (180/math.pi) * (distance / 6378137) / math.cos(lat0) * math.cos(a)
        newLat = lat + (180/math.pi) * (distance / 6378137) * math.sin(a)
        return newLon, newLat

    # -------------------------------------------------------------------------
    def computeDistanceAndAzimut(self, lon0, lat0, lon1, lat1):
        """
            Compute Distance and Azimut between 2 points .
            See https://fr.qaz.wiki/wiki/Azimuth :  Azimuth Cartographique

            :param float lon0: Longitude start point
            :param float lat0: Latitude start point
            :param float lon1: Longitude end point
            :param float lat1: Latitude end point
            :returns: azimuth1, azimuth2, distance
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


__all__ = [
    'NeacCoordHelper','compute_range_from_m_to_pixel', 'computeDistanceAndAzimut', 'getCoordFromDistanceAndAngle', 'projPoint', 'compute_ratio', 'projXY'
]