from NeacCore.NeacLocation import NeacLocation
import math

class NeacCollisionPoint(NeacLocation):
    """
        Collision Point. Used to represent the estimated collision point between a shuttle and an UFO on the map. 

        :param NeacShuttle shuttle: shuttle.
        :param NeacUfo ufo: Corresponding UFO.
        :param datetime collision_time: Expected collision time.
        :param str collision_type: 'front', 'back', 'unknown'.
        :param int xAvoid: X coordinate on the screen.
        :param int yAvoid: Y coordinate on the screen.
        :param int rAvoid: Avoiding Circle radius (meters)
     """

    #--------------------------------------------------------------------------
    def __init__(self):
        NeacLocation.__init__(self)
        self.shuttle        = None
        self.ufo            = None
        self.collision_time = -1
        # self.collision_type = "unknown"  # front, back, unknown
        self.xAvoid         = 0
        self.yAvoid         = 0
        self.rAvoid         = 0 # Rayon du cercle d'évitement en mètres

    #--------------------------------------------------------------------------
    def get_r_avoid(self):
        return self.rAvoid

    #--------------------------------------------------------------------------
    def set_ufo(self, ufo):
        self.ufo = ufo

    #--------------------------------------------------------------------------
    def get_ufo(self):
        return self.ufo

    #--------------------------------------------------------------------------
    def set_shuttle(self, shuttle):
        self.shuttle = shuttle

    #--------------------------------------------------------------------------
    def set_collision_time(self, collision_time):
        self.collision_time = collision_time

    #--------------------------------------------------------------------------
    def set_collision_type(self, collision_type):
        self.collision_type = collision_type

    # #--------------------------------------------------------------------------
    # def set_avoid_location(self, lon, lat, coordHelper):
    #     """
    #         compute X, Y, xAvoid, yAvoid, rAvoid

    #         :param float lon: longitude.
    #         :param float lat: latitude.
    #         :param NeacCoordHelper coordHelper: latitude.
    #         :returns: None.
    #     """
    #     NeacLocation.set_location(self, lon, lat)

    #     # Calcul du rayon d'évitement ! 
    #     x = self.get_x(coordHelper)
    #     y = self.get_y(coordHelper)
    #     avoidLimitLon, avoidLimitLat = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, 15, 0) # Rayon de 15 mètres
    #     self.xAvoid, self.yAvoid = coordHelper.projPoint(avoidLimitLon, avoidLimitLat)
    #     self.rAvoid = math.sqrt( (self.xAvoid - x)*(self.xAvoid - x) + (self.yAvoid - y)*(self.yAvoid - y))

    # #--------------------------------------------------------------------------
    # def get_drawing_information(self, coordHelper):
    #     x = self.get_x(coordHelper)
    #     y = self.get_y(coordHelper)
    #     return {"id"            : "collisionPoint",
    #             "ufo"           : self.ufo.getName(), 
    #             "shuttle"       : self.shuttle.getName(),
    #             "x"             : x, 
    #             "y"             : y,
    #             "type"          : self.collision_type,
    #             "time"          : self.collision_time}

__all__ = [
    'NeacCollisionPoint', 'set_collision_type', 'set_collision_time', 
    'set_shuttle', 'get_ufo', 'set_ufo', 'get_r_avoid'
]