from datetime import datetime
import logging

from NeacCore.NeacCollisionPoint import NeacCollisionPoint
from NeacCore.NeacWayPoint       import NeacWayPoint
from NeacCore.NeacFloatingObject import NeacFloatingObject
from NeacCore.NeacConstant       import NAVIGATION_MODE
from NeacCore.NeacDrc            import NeacDrc
from NeacCore.NeacUfo            import NeacUfo

class NeacShuttle(NeacFloatingObject):
    """
        Main Neac Shuttle Object. Represent the current ship status
    """

    # Paramètres du modèle de la navette
    speed_KP = 0   # P   : Coefficient de proportionnalité de l'erreur 
    speed_KI = .09 # PI  : Coefficient de proportionnalité de la somme des erreurs = Rapidité de correction. Plus la valeur est haute, plus la correction est rapide

    heading_KP = 0.3    # P  : Coefficient de proportionnalité de l'erreur 
    heading_KI = 0      # I  : Coefficient de proportionnalité de la somme des erreurs = Rapidité de correction. Plus la valeur est haute, plus la correction est rapide
    heading_KD = 0.3    # D  :

    def __init__(self, config):
        NeacFloatingObject.__init__(self, config.aspedsa.shuttle_name)
        self.mode              = NAVIGATION_MODE.DP

        # ---- STATIC SHUTTLE INFORMATION
        self.width         = config.aspedsa.shuttle_width
        self.height        = config.aspedsa.shuttle_height
        self.turn_velocity = config.aspedsa.turn_velocity

        # ---- HEADING
        self.current_heading  = 0   # Cap actuel de la navette
        self.u_heading        = 0   # Consigne de cap du bateau
        self.err_heading      = 0   # Historique des erreurs de cap
        self.err_heading_prec = 0   # Erreur précédente de heading
        self.chart_heading_values = []

        # ---- SPEED
        self.current_speed    = 0   # vitesse en noeuds SOG (Speed Over Ground)
        self.u_speed          = 0   # consigne de vitesse en noeuds
        self.errSpeed         = 0   # Historique des erreurs de vitesse

        # ---- ROUTE
        self.destination      = None   # Station destination finale de la navette
        self.route            = None   # Route actuelle suivi par la navette
        self.target           = None   # Prochain Waypoint à atteindre
        self.distance_to_target = 0    # Distance restante jusqu'au prochain waypoint
        self.previous_points  = []     # Liste des WP par lesquels la navette est déjà passée. 
        self.last_way_point   = None   # Le waypoint précédant par lequel la navette est passée. Initialisé avec le point de départ de la route
        self.route_gap        = ((0, 0), 0, 0 )     # Ecart en mètres par rapport à la route suivie

        # ---- TRACE
        self.trace            = []     # Liste des points de la trace du navire. 

        # ---- COLLISION DETECTION
        self.collision_point  = None
        # self.avoid_mode       = False
        self.avoid_ufo        = None
        self.collision_points = []
        self.collision_point  = None
        self.avoid_point      = None

        # ---- NMEA INFORMATION
        self.rudder           = 0  # Current position of the rudder
        self.throttle         = 0  # Current position of the throttle command
        self.pitch            = 0  # Tangage https://lamisaine.jimdofree.com/2016/04/03/mouvements-du-bateau/#gsc.tab=0
        self.roll             = 0  # Roulis
        self.rate_of_turn     = 0  # Rate of turn from GPS, in ° per minutes
        self.heave            = 0  # Heave = Houle
        self.pressure         = 0  # Barometric pressure in millibars
        self.temperature      = 0  # Air temperature, degrees C, to the nearest 0.1 degree C
        self.gps_time_stamp   = datetime.now()  # timeStamp de la dernière remontée du GPS
        self.relat_wind_direction = 0 # Current relative wind direction
        self.relat_wind_speed     = 0 # Current relative wind speed (kn)

        
        
        
        self.ufos                 = dict()
        """ List of UFOs detected by AIS, Video, Radar, etc. """

        # ---- DRC : Detect Route Collision
        self.drc = NeacDrc(self)

    # -------------------------------------------------------------------------
    def setMode(self, mode):
        self.mode = mode

    # -------------------------------------------------------------------------
    # def setAvoidMode(self, avoid_mode):
    #     self.avoid_mode = avoid_mode

    # -------------------------------------------------------------------------
    # def isAvoidMode(self):
    #     return self.avoid_mode

    # -------------------------------------------------------------------------
    def setAvoidUfo(self, ufo):
        self.avoid_ufo = ufo

    # -------------------------------------------------------------------------
    def getAvoidUfo(self):
        return self.avoid_ufo

    # -------------------------------------------------------------------------
    def set_collision_point(self, collision_point):
        self.collision_point = collision_point

    # -------------------------------------------------------------------------
    def getCollisionPoint(self):
        return self.collision_point

    # -------------------------------------------------------------------------
    # ---- DIRECTION
    # -------------------------------------------------------------------------
    def set_current_heading(self, heading):
        self.current_heading = heading

    # -------------------------------------------------------------------------
    def set_U_heading(self, heading):
        self.u_heading = heading

    # -------------------------------------------------------------------------
    def model_shuttle_heading(self, ellapse_time):
        """
        Simulate the new heading of the shuttle based on the elapsed time 
        à chaque boucle, on met à jour progressivement le cap du bateau
        Modélisation basée sur le rate of turn

        :param int ellapse_time: number of milliseconds since the last calculation
        :returns: None.
        """
        if self.u_heading > 180:
            u_heading = self.u_heading-360
        else:
            u_heading = self.u_heading

        if self.current_heading > 180:
            current_heading = self.current_heading-360
        else:
            current_heading = self.current_heading

        turn_velocity = self.turn_velocity # ° / min = On fait un tour complet en une minute = relativement lent
        if current_heading > u_heading:
            turn_velocity = -turn_velocity # ° / min = On fait un tour complet en une minute = relativement lent
        elif current_heading < u_heading :
            turn_velocity = turn_velocity # ° / min = On fait un tour complet en une minute = relativement lent
        else:
            turn_velocity = 0

        delta_angle = turn_velocity / 60 / 1000 * ellapse_time
        self.current_heading = self.current_heading + delta_angle
        if abs(self.current_heading-self.u_heading) < abs(delta_angle):
            self.current_heading = self.u_heading
        



    # -------------------------------------------------------------------------
    # ---- SPEED
    # -------------------------------------------------------------------------
    def set_current_speed(self, speed):
        self.current_speed = speed

    # -------------------------------------------------------------------------
    def set_U_speed(self, speed):
        self.u_speed = speed

    # -------------------------------------------------------------------------
    def model_shuttle_speed(self):
        """
        Simulate the new speed of the shuttle based on the elapsed time 
        à chaque boucle, on met à jour progressivement la vitesse du bateau

        :returns: None.
        """
        erreur            = self.u_speed - self.current_speed
        self.errSpeed     = self.errSpeed + erreur
        self.current_speed = self.speed_KP*erreur + self.speed_KI*self.errSpeed
        if (erreur==0):
            self.errSpeed

    # -------------------------------------------------------------------------
    def set_target(self, target):
        self.target = target
        
    # -------------------------------------------------------------------------
    def set_distance_to_target(self, distance_to_target):
        self.distance_to_target = distance_to_target

    # -------------------------------------------------------------------------
    def set_destination(self, destination):
        self.destination = destination

    # -------------------------------------------------------------------------
    # ---- ROUTE
    # -------------------------------------------------------------------------
    def set_route(self, route):
        self.route  = route

    # -------------------------------------------------------------------------
    def add_previous_point(self, wayPoint : NeacWayPoint) -> None: 
        """
            Ajout le WayPoint à la liste des waypoint déjà croisés, de sorte à ne  pas revenir sur ses pas.
        """
        alreadyExists = False
        for wp in self.previous_points:
            if wp.name == wayPoint.name and wp.lon==wayPoint.lon and wp.lat==wayPoint.lat:
                alreadyExists = True
        if alreadyExists == False:
            self.previous_points = self.previous_points + [wayPoint]
            self.last_way_point   = wayPoint
    
    # -------------------------------------------------------------------------
    def is_previous_point(self, wayPoint : NeacWayPoint):
        for wp in self.previous_points:
            if wp.name == wayPoint.name and wp.lon==wayPoint.lon and wp.lat==wayPoint.lat:
                return True
        return False

    # -------------------------------------------------------------------------
    def reset_previous_points(self): 
        self.previous_points = []

    # -------------------------------------------------------------------------
    def start_navigation(self, mode : NAVIGATION_MODE):
        return None

    # # -------------------------------------------------------------------------
    # def estimate_collisions(self):
    #     #logging.debug("--> NeacShuttle.estimateCollisions()")
    #     self.drc.estimate_ufo_routes()

    # -------------------------------------------------------------------------
    def update_AIS_type_1_3(self, mmsi : str, longitude : float, latitude : float, position_accuracy, navigation_status, rate_of_turn, speed_over_ground : float, course_over_ground, true_heading, time_stamp, maneuver_indicator, radio_status):
        """
            When a message 1 or 3 is received from the shuttle AIS, the UFO list is updated accordingly. 

            :param str mmsi: MMSI Id of the UFO
            :param float longitude: WGS84 longitude of the UFO
            :param float latitude: WGS84 latitude of the UFO
            :param  position_accuracy: 
            :param  navigation_status: 
            :param  rate_of_turn: 
            :param float speed_over_ground: 
            :param  course_over_ground: 
            :param  true_heading: 
            :param  time_stamp: 
            :param maneuver_indicator:
            :param radio_status:
            :returns: None.
        """
        try:
            the_ufo = self.ufos[mmsi]
        except KeyError:
            the_ufo = NeacUfo(mmsi)
            self.ufos[mmsi] = the_ufo
    
        self.ufos[mmsi].mmsi      = mmsi
        self.ufos[mmsi].ais_name  = str(mmsi)
        self.ufos[mmsi].heading   = true_heading
        self.ufos[mmsi].direction = course_over_ground
        self.ufos[mmsi].speed     = speed_over_ground
        self.ufos[mmsi].status    = navigation_status[1]
        self.ufos[mmsi].set_location(longitude, latitude)
        
    # -------------------------------------------------------------------------
    def update_AIS_type_5(self, mmsi, vessel_name, ship_type, dimension_to_bow, dimension_to_stern, dimension_to_port, dimension_to_starboard):
        """
            When a message is received from the shuttle AIS, the UFO list is updated accordingly. 
        """
        try:
            the_ufo = self.ufos[mmsi]
        except KeyError:
            the_ufo = NeacUfo(mmsi)
            self.ufos[mmsi] = the_ufo
    
        self.ufos[mmsi].mmsi                   = mmsi
        self.ufos[mmsi].vessel_name            = vessel_name
        self.ufos[mmsi].ship_type              = ship_type
        self.ufos[mmsi].dimension_to_bow       = dimension_to_bow
        self.ufos[mmsi].dimension_to_stern     = dimension_to_stern
        self.ufos[mmsi].dimension_to_port      = dimension_to_port
        self.ufos[mmsi].dimension_to_starboard = dimension_to_starboard
        self.ufos[mmsi].width  = dimension_to_bow + dimension_to_stern
        self.ufos[mmsi].height = dimension_to_port + dimension_to_starboard

__all__ = [
    'NeacShuttle', 'model_shuttle_heading', 'model_shuttle_speed', 'update_AIS_type1_3', 'update_AIS_type_5', 'add_previous_point'
]