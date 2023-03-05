from NeacCore.NeacCoordHelper import NeacCoordHelper
from NeacCore.NeacFloatingObject       import NeacFloatingObject
from NeacCore.NeacConstant             import DRC_MODE
from typing                            import List, Tuple

Point   = Tuple[float, float]
Polygon = List[Point]

class NeacUfo(NeacFloatingObject):
    """
        UFO = Unknown Floating Object
        The object can come from : Video detection, Radar, AIS, etc... 

        :param type: UFO type (Passenger, fish, Pétrolier, Cargo)
        :param str mmsi: MMSI.
        :param str ais_name: UFO AIS name.
        :param int radar_target_id: UFO target ID coming from Radar.
        :param float heading: UFO heading.
        :param float direction: UFO COG.
        :param float speed: UFO speed.
        :param int width: Vessel size (From AIS).
        :param str status: AIS status (At Anchor, Moored, Under way using engine, Restricted manoeuvrability, Engaged in Fishing)
        :param int height: Vessel size (From AIS).
        :param int r_col: Range Collision.
        :param int r_nm: Range Near Missed (Collision).
        :param int r_min: Range Minimum (Orange Line).
        :param int r_pref: Range Preferred (Green Line).
        :param int dimension_to_bow: AIS Antenna position from bow (in meters).
        :param int dimension_to_stern: AIS Antenna position from stern (in meters).
        :param int dimension_to_port: AIS Antenna position from port (in meters).
        :param int dimension_to_starboard: AIS Antenna position from starboard (in meters).
        :param int drc_mode: Detect Route Collision Mode
    """

    def __init__(self, name=""):
        NeacFloatingObject.__init__(self, name)
        self.type                   = None
        self.mmsi                   = None
        self.ais_name               = ""
        self.radar_target_id        = None
        self.heading                = 0
        self.direction              = 0
        self.speed                  = 0
        self.status                 = None
        self.r_col                  = 1 
        self.r_nm                   = 3
        self.r_min                  = 5
        self.r_pref                 = 10
        self.width                  = 3
        self.height                 = 3
        self.dimension_to_bow       = 0
        self.dimension_to_stern     = 0
        self.dimension_to_port      = 0
        self.dimension_to_starboard = 0
        self.drc_mode               = DRC_MODE.IGNORE

        self.ufo_polygon            = None
        self.r_pref_polygon         = None

        self.lon_30s                = None
        self.lat_30s                = None

    # -------------------------------------------------------------------------
    def compute_ufo_polygon(self, coordHelper : NeacCoordHelper) -> Polygon :
        """
            Dessine le navire en lui-même = Un rectangle
        """
        self.ufo_polygon = []
        P = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_bow,   self.heading)
        E = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_stern, self.heading + 180)

        x_1, y_1 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.dimension_to_port, self.heading + 90)
        x_2, y_2 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.dimension_to_port, self.heading + 90)
        x_3, y_3 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.dimension_to_starboard, self.heading - 90)
        x_4, y_4 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.dimension_to_starboard, self.heading - 90)
        self.ufo_polygon = [(x_1, y_1)] + [(x_2, y_2)] + [(x_3, y_3)] + [(x_4, y_4)]
        return self.ufo_polygon


    # -------------------------------------------------------------------------
    def compute_r_pref_polygon(self, coordHelper : NeacCoordHelper) -> Polygon:
        self.r_pref_polygon = []
        front_coef = 1.6

        P = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_bow,                 self.heading)
        E = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_stern+self.r_pref,   self.heading + 180)
        Q = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_bow + self.r_pref*2, self.heading)

        x_0, y_0 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_starboard, self.heading + 90)
        x_1, y_1 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref            + self.dimension_to_starboard, self.heading + 90)
        x_2, y_2 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref            + self.dimension_to_port,      self.heading - 90)
        x_3, y_3 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_port,      self.heading - 90)
        x_4, y_4 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_port,      self.heading - 90)
        x_5, y_5 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*3,                                        self.heading)
        x_6, y_6 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_starboard, self.heading + 90)

        self.r_pref_polygon = [(x_0, y_0)] + [(x_1, y_1)] + [(x_2, y_2)] + [(x_3, y_3)] + [(x_4, y_4)] + [(x_5, y_5)] + [(x_6, y_6)]
        return self.r_pref_polygon

    # -------------------------------------------------------------------------
    def compute_r_pref_polygon_30s(self, coordHelper : NeacCoordHelper) -> Polygon :
        self.r_pref_polygon = []
        if self.lon_30s != None:
            front_coef = 1.6

            P = coordHelper.getCoordFromDistanceAndAngle(self.lon_30s, self.lat_30s, self.dimension_to_bow,                 self.heading)
            E = coordHelper.getCoordFromDistanceAndAngle(self.lon_30s, self.lat_30s, self.dimension_to_stern+self.r_pref,   self.heading + 180)
            Q = coordHelper.getCoordFromDistanceAndAngle(self.lon_30s, self.lat_30s, self.dimension_to_bow + self.r_pref*2, self.heading)

            x_0, y_0 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_starboard, self.heading + 90)
            x_1, y_1 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref            + self.dimension_to_starboard, self.heading + 90)
            x_2, y_2 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref            + self.dimension_to_port,      self.heading - 90)
            x_3, y_3 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_port,      self.heading - 90)
            x_4, y_4 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_port,   self.heading - 90)
            x_5, y_5 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*3,                                        self.heading)
            x_6, y_6 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_starboard, self.heading + 90)

            self.r_pref_polygon = [(x_0, y_0)] + [(x_1, y_1)] + [(x_2, y_2)] + [(x_3, y_3)] + [(x_4, y_4)] + [(x_5, y_5)] + [(x_6, y_6)]
        return self.r_pref_polygon

    # -------------------------------------------------------------------------
    def compute_r_min_polygon(self, coordHelper : NeacCoordHelper) -> Polygon :
        self.r_pref_polygon = []
        front_coef = 1

        P = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_bow,                 self.heading)
        E = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_stern+self.r_pref*.5,   self.heading + 180)
        Q = coordHelper.getCoordFromDistanceAndAngle(self.lon, self.lat, self.dimension_to_bow + self.r_pref*1.5, self.heading)

        x_0, y_0 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_starboard, self.heading + 90)
        x_1, y_1 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref*.5            + self.dimension_to_starboard, self.heading + 90)
        x_2, y_2 = coordHelper.getCoordFromDistanceAndAngle(E[0], E[1], self.r_pref*.5            + self.dimension_to_port,      self.heading - 90)
        x_3, y_3 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*front_coef + self.dimension_to_port,      self.heading - 90)
        x_4, y_4 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_port,      self.heading - 90)
        x_5, y_5 = coordHelper.getCoordFromDistanceAndAngle(P[0], P[1], self.r_pref*2,                                        self.heading)
        x_6, y_6 = coordHelper.getCoordFromDistanceAndAngle(Q[0], Q[1], self.r_pref*front_coef*.5 + self.dimension_to_starboard, self.heading + 90)

        self.r_pref_polygon = [(x_0, y_0)] + [(x_1, y_1)] + [(x_2, y_2)] + [(x_3, y_3)] + [(x_4, y_4)] + [(x_5, y_5)] + [(x_6, y_6)]
        return self.r_pref_polygon

    # -------------------------------------------------------------------------
    def convert_polygon_coord_to_xy(self, coordHelper : NeacCoordHelper, polygon : Polygon) -> Polygon:
        """
            Converti les coordonnées lat/lon du polygon passé en paramètre en x/y.
            :param NeacCoordHelper coordHelper: coordinates helper.
            :param Polygon polygon : polygon in lat/lon to be converted
            :returns: Polygon.
        """
        xy_polygon = []
        for point in polygon:
            x, y = coordHelper.projPoint(point[0], point[1])
            xy_polygon = xy_polygon + [(x,y)]
        return xy_polygon

    # -------------------------------------------------------------------------
    def get_drawing_information(self, coordHelper : NeacCoordHelper):
        """
            Obsolete. Used to draw a Javascript object.
        """
        x = self.getX(coordHelper)
        y = self.getY(coordHelper)
        return {"x"      : x, 
                "y"      : y,
                "r_col"  : coordHelper.compute_range_from_m_to_pixel(self.r_col),
                "r_nm"   : coordHelper.compute_range_from_m_to_pixel(self.r_nm),
                "r_min"  : coordHelper.compute_range_from_m_to_pixel(self.r_min),
                "r_pref" : coordHelper.compute_range_from_m_to_pixel(self.r_pref) }

# ---- Sphinx objects to document:
__all__ = ['NeacUfo', 'get_drawing_information']