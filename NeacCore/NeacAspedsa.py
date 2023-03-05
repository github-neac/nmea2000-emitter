import threading
import logging
import multiprocessing
from datetime                              import datetime, timedelta

from NeacCore.NeacConfig                   import NeacConfig
from NeacCore.NeacShuttle                  import NeacShuttle
from NeacCore.NeacCoordHelper              import NeacCoordHelper
from NeacCore.NeacRouteCalculator          import NeacRouteCalculator
from NeacCore.NeacConstant                 import NAVIGATION_MODE
from NeacCore.NeacUfo                      import NeacUfo

from Aspedsa.NeacControl.NeacController    import NeacController
from Aspedsa.NeacMap.NeacMap               import start_map_process
from Aspedsa.Video.NeacTorchDetector       import NeacTorchDetector
from Aspedsa.NeacNmea2000.NeacNmea2000     import NeacNmea2000


class NeacAspedsa(threading.Thread):
    """
        THE ASPEDSA Module
    """
    # ----------------------------------------------------------------------------------------------------------------
    def __init__(self, config : NeacConfig, shuttle : NeacShuttle, nmea : NeacNmea2000, controller : NeacController):
        threading.Thread.__init__(self, name="NeacAspedsa")
        self.shuttle         = shuttle
        self.config          = config
        self.nmea            = nmea
        self.controller      = controller

        self.routes           = []
        self.stations         = []
        self.ufos             = None
        self.current_sys_time = datetime.now()

        self.coordHelper       = NeacCoordHelper(config)
        self.routeCalculator   = NeacRouteCalculator(self.coordHelper)
        self.video_detector    = NeacTorchDetector(config.camera.front_1_url, self)

        # ---- NeacMap MultiProcessing Object
       
        self.shuttle_queue = multiprocessing.Queue()
        self.shuttle_queue.put([self.shuttle, self.ufos])

        logging.debug ("NeacAspedsa.int() : start_map_process() ...")
        self.map_process = multiprocessing.Process(target=start_map_process, args=(config, self.shuttle_queue))
        self.map_process.start() 
        logging.debug ("NeacAspedsa.int() : start_map_process() completed")

        self.ufos            = dict()
        logging.debug("NeacAspedsa initialized.")

    # ----------------------------------------------------------------------------------------------------------------
    def run(self):
        """
            - Starts the NeacController
            - Starts the NeacNMEA2000
            - Generates the UFO list
            - Run infinitley the update_data() loop
        """
        logging.debug("Starting NeacAspedsa ...")
        self.controller.start()
        self.nmea.start()
        # self.video_detector.start()
        self.generate_ufos(self)
        while True:
            self.aspedsa_loop()
        
    # ----------------------------------------------------------------------------------------------------------------
    def aspedsa_loop(self):
        """
            Main loop for Aspedsa module. Every config.simulator.update_frequency (1000 ms), it does:
                - compute the new simulated time
                - Move the objects (in simulation mode only)
                - Send the objects (shuttle and Ufos) to the NeacMap process (using a Queue Object)
                - Update the information displayed on the NeacMonitor
        """
        new_sys_time = datetime.now()
        ellapse_time = (new_sys_time-self.current_sys_time).seconds * 1000  + (new_sys_time-self.current_sys_time).microseconds / 1000
        if ellapse_time >= int(self.config.simulator.update_frequency):
            # Les informations du moniteur ne sont rafraichit qu'une fois toutes les update_frequency millisecondes
            self.current_time           = self.shuttle.gps_time_stamp + timedelta(seconds=int(self.config.simulator.update_frequency)/1000)
            self.shuttle.gps_time_stamp = self.current_time

            self.compute_aspedsa_route(self.current_time)
            self.send_route_to_autopilot()

            if self.config.aspedsa.mode == 'simu':
                self.move_shuttle()
                self.move_ufos()

            self.update_shuttle_and_ufos_on_the_map()
            self.current_sys_time = datetime.now()

    # -------------------------------------------------------------------------
    def send_route_to_autopilot(self):
        """
        Ask NeacNMEA module to send the APB command to the autopilot to route to the target waypoint. 
        """
        if self.shuttle.target != None:
            self.nmea.send_APB_message(self.shuttle.target)

    # -------------------------------------------------------------------------
    def move_shuttle(self):
        """
            Simulate the change speed and heading since the last tick : simu_frequency
        """
        self.shuttle.model_shuttle_heading(int(self.config.simulator.simu_frequency))
        self.shuttle.model_shuttle_speed()

        speed          = self.shuttle.current_speed
        heading        = self.shuttle.current_heading
        # simu_frequency : chaque tick du simulateur correspond à 'simu_frequency' millisecondes. Cela
        #                  permet d'accélérer ou de ralentir le simulateur.
        newDistance    = speed * 1852 / 60 / 60 / 1000 * int(self.config.simulator.simu_frequency)
        newLon, newLat = self.coordHelper.getCoordFromDistanceAndAngle(self.shuttle.lon, self.shuttle.lat, newDistance, heading)
        self.shuttle.trace = self.shuttle.trace + [(newLon, newLat)]
        self.shuttle.set_location(newLon, newLat)

    # -------------------------------------------------------------------------
    def move_ufos(self):
        if self.ufos:
            for mmsi, theUfo in self.ufos.items():
                speed          = theUfo.speed
                heading        = theUfo.heading
                newDistance    = speed * 1852 / 60 / 60 / 1000 * int(self.config.simulator.simu_frequency)
                newLon, newLat = self.coordHelper.getCoordFromDistanceAndAngle(theUfo.lon, theUfo.lat, newDistance, heading)
                theUfo.set_location(newLon, newLat)

    # --------------------------------------------------------------------------
    def update_shuttle_and_ufos_on_the_map(self):
        """
            Put the shuttle object and the UFO list in the MultiProcessing Queue Object. It will be read by the NeacMap Object to display
            The shuttle information on the map
        """
        try:
            self.shuttle_queue.put([self.shuttle, self.ufos])
        except multiprocessing.Queue.Full:
            logging.erro("Queue Full")

    # ----------------------------------------------------------------------------------------------------------------
    def generate_ufos(self, monitor):
        logging.debug("NeacAspedsa.generate_ufos()...")
        if self.config.aspedsa.simulate_ufo == True:
            logging.debug("  Simulating UFOs from config file.")
            for ufo_name, ufo in self.config.simulator.ufos.items():
                new_ufo = NeacUfo(ufo_name)
                new_ufo.ais_name               = ufo['ais_name']
                new_ufo.heading                = ufo['heading']
                new_ufo.direction              = ufo['direction']
                new_ufo.speed                  = ufo['speed']
                new_ufo.width                  = ufo['width']
                new_ufo.status                 = ufo['status']
                new_ufo.height                 = ufo['height']
                new_ufo.dimension_to_bow       = ufo['dimension_to_bow']
                new_ufo.dimension_to_stern     = ufo['dimension_to_stern']
                new_ufo.dimension_to_port      = ufo['dimension_to_port']
                new_ufo.dimension_to_starboard = ufo['dimension_to_starboard']
                new_ufo.set_location(ufo['longitude'], ufo['latitude'])
                self.ufos[ufo_name] = new_ufo
            monitor.ufos = self.ufos
            self.shuttle.ufos = self.ufos

    # -------------------------------------------------------------------------
    def compute_aspedsa_route(self, currentTime):
        """
            Recherche de la meilleure route et du prochain waypoint.
            Cette recherche se fait indépendemment des évitements de collision
        """

        route, targetWaypoint, distance, azimutTarget = self.routeCalculator.compute_target(self.shuttle, self.routes) #, self.stations)
        self.shuttle.set_route(route)
        self.shuttle.set_target(targetWaypoint)
        self.shuttle.set_distance_to_target(distance)

        self.compute_drc()

        if self.shuttle.mode != NAVIGATION_MODE.AVOID:
            if (self.shuttle.last_way_point != None):
                if (self.shuttle.last_way_point.mode == NAVIGATION_MODE.DP) : 
                    self.shuttle.set_U_speed(0)
                    self.shuttle.set_distance_to_target(0)
                elif (self.shuttle.last_way_point.mode == NAVIGATION_MODE.CRUISE) : 
                    self.shuttle.set_U_speed(self.config.aspedsa.speed_cruise)
                elif (self.shuttle.last_way_point.mode == NAVIGATION_MODE.AVOID) : 
                    self.shuttle.set_U_speed(self.config.aspedsa.speed_avoid)                        
                elif (self.shuttle.last_way_point.mode == NAVIGATION_MODE.UNDOCKING) : 
                    self.shuttle.set_U_speed(self.config.aspedsa.speed_undocking)
                elif (self.shuttle.last_way_point.mode == NAVIGATION_MODE.DOCKING) : 
                    self.shuttle.set_U_speed(self.config.aspedsa.speed_docking)

                self.shuttle.setMode(self.shuttle.last_way_point.mode)
        
        # ---- Calcul de l'écart actuel par rapport à la route
        if route != None:
            self.shuttle.route_gap = self.routeCalculator.compute_route_gap(self.shuttle, route)

        if self.shuttle.mode == NAVIGATION_MODE.AVOID:
            azimuth_avoid_point, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut(self.shuttle.lon, self.shuttle.lat, self.shuttle.avoid_point.lon, self.shuttle.avoid_point.lat)

            # Calcul de l'écart avec la route // à la route actuelle, mais passant par le waypoint d'évitement
            avoid_route_intersection, avoid_route_gap, azimuth_avoid = self.routeCalculator.compute_avoid_route_distance(self.shuttle, route, self.shuttle.avoid_point.lon, self.shuttle.avoid_point.lat)
            correction = 0
            if abs(avoid_route_gap) > 2:
                if self.shuttle.current_heading > azimuth_avoid:
                    correction = +5 * avoid_route_gap # La correction est proportionnel à l'écart avec la route. 
                else:
                    correction = +5 * avoid_route_gap 

                if correction > 70 : 
                    correction = 70
                if correction < -70 : 
                    correction = -70

            self.shuttle.set_U_heading(azimuth_avoid_point + correction)  
            self.shuttle.set_distance_to_target(distance)
        else:
            if self.shuttle.route_gap != None:
                # Si l'écart de route est > 2m, alors on exagère la correction de cap de 5°
                correction = 0
                if self.shuttle.route_gap[1] > 2:
                    if self.shuttle.current_heading > azimutTarget:
                        correction = -5 * self.shuttle.route_gap[1] # La correction est proportionnel à l'écart avec la route. 
                    else:
                        correction = -5 * self.shuttle.route_gap[1] 

                    if correction > 70 : 
                        correction = 70
                    if correction < -70 : 
                        correction = -70
                    
                    self.shuttle.set_U_heading(azimutTarget + correction)        
                else:
                    self.shuttle.set_U_heading(azimutTarget)        

    # --------------------------------------------------------------------------
    def compute_drc(self):
        """
            Detect Potential Collision with each UFO
        """
        self.shuttle.collision_points = []
        self.shuttle.avoid_point      = None
        if self.shuttle.target != None:
            self.shuttle.mode = self.shuttle.target.mode
        else:
            self.shuttle.mode = NAVIGATION_MODE.DP
            
        for ufo_name, ufo in list(self.shuttle.ufos.items()):
            ufo.compute_r_pref_polygon(self.coordHelper)
            self.shuttle.drc.estimate_ufo_next_position(ufo, self.coordHelper)
            if self.shuttle.drc.estimate_ufo_r_pref_collision(ufo, self.coordHelper) == True:
                # There is at least one collision point. Shuttle is switched to AVOID mode
                self.shuttle.mode = NAVIGATION_MODE.AVOID


# Sphinx objects to document:
__all__ = ['NeacAspedsa', 'compute_drc', 'compute_aspedsa_route', 'generate_ufos', 'update_shuttle_and_ufos_on_the_map', 'move_ufos', 'move_shuttles', 'aspedsa_loop', 'send_route_to_autopilot' ]
