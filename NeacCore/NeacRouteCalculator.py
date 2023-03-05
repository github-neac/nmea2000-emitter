import logging
from NeacCore.NeacShuttle   import NAVIGATION_MODE, NeacShuttle
from NeacCore.NeacRoute     import NeacRoute
from NeacCore.NeacWayPoint  import NeacWayPoint
from typing                 import List, Tuple

Point   = Tuple[float, float]
Polygon = List[Point]

class NeacRouteCalculator:
    
    # -------------------------------------------------------------------------
    def __init__(self, coordHelper):
        logging.info ("--> NeacScheduler.NeacRouteCalculator()")
        self.coordHelper = coordHelper
        return None

    # -------------------------------------------------------------------------
    def compute_target(self, shuttle : NeacShuttle, routes):
        """
            Regarde la destination de la navette
            Recherche toutes les routes dont la destination est la même 
            Parcours chaque route, chaque waypoint, et recherche le waypoint le plus proche 
            qui n'est pas dans la liste des précédents waypoint de la navette. 
        """
        closestWP            = None
        closestPointDistance = 9999999999999
        closestPointAzimut   = 0
        closestRoute         = None
            
        if shuttle.destination:
            destination        = shuttle.destination

            for route in routes:
                if (route.destination_station == destination):
                    closestWP            = None
                    closestPointDistance = 1000000
                    closestPointAzimut   = 0
                    for waypoint in route.way_point_list:
                        azimuth1, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut(shuttle.lon, shuttle.lat, waypoint.lon, waypoint.lat)
                        if distance > 1.5 :
                            if (distance < closestPointDistance
                                and shuttle.is_previous_point(waypoint)==False 
                                and waypoint.mode!=NAVIGATION_MODE.AVOID
                                and self.is_wp_acessible(waypoint, shuttle) ):
                                closestWP            = waypoint
                                closestPointDistance = distance
                                closestPointAzimut   = azimuth1
                                closestRoute         = route
                        else:
                            # the WP is very short distance, Assuming the shuttle as already reached the WP previously
                            #logging.info("  Analysing WP <0.5 : " + waypoint.name + " - Dist=" + str(distance))
                            shuttle.add_previous_point(waypoint)

        return closestRoute, closestWP, closestPointDistance, closestPointAzimut

    # -------------------------------------------------------------------------
    def is_wp_acessible(self, waypoint : NeacWayPoint, shuttle : NeacShuttle):
        """
            Return True is the waypoint id not included in any Ufo polygon 
            Pour un polygone convexe, si la somme des angles entre le point et les sommets du polygone est égale à 360,
            alors le point est dans le polygon
        """        
        for ufo_name, ufo in list(shuttle.ufos.items()):
            sum_angles = 0
            ufo.compute_r_pref_polygon(self.coordHelper)
            p_prev=None
            for Pn in ufo.r_pref_polygon:
                if p_prev != None:
                    azimuth_prev, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut( waypoint.lon, waypoint.lat, p_prev[0], p_prev[1])
                    azimuth_n,    azimuth2, distance = self.coordHelper.computeDistanceAndAzimut( waypoint.lon, waypoint.lat, Pn[0], Pn[1])
                    sum_angles = sum_angles + (azimuth_n-azimuth_prev)
                else:
                    p_prev = Pn
            if sum_angles==360:
                return False
        return True
            
    # -------------------------------------------------------------------------
    def compute_route_gap(self, shuttle : NeacShuttle, route : NeacRoute):
        """
            Calcul le point d'intersection entre la route et la projection orthogonale de la navette. 
            Retourne : X, Y, distance, Azimuth
        """
        for waypoint in route.way_point_list:
            index_current_wp = route.way_point_list.index(shuttle.target)
            if index_current_wp > 0:
                index_previous_wp = index_current_wp - 1
                previous_wp = route.way_point_list[index_previous_wp]

                # route equation
                P = previous_wp
                N = shuttle.target
                if (float(N.lon) - float(P.lon)) != 0:
                    a = (float(N.lat) - float(P.lat)) / (float(N.lon) - float(P.lon) )
                    b = float(N.lat) - float(N.lon) * a 
                    route.a = a
                    route.b = b

                    # Equation de la droite perpendiculaire
                    if a!=0:
                        ap = -1 / a 
                        bp = shuttle.lat - shuttle.lon * ap

                        # Intersection des deux droites
                        x_inter = (bp - b) / (a - ap)
                        y_inter = a * x_inter + b

                        azimuth1, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut(shuttle.lon, shuttle.lat, x_inter, y_inter)
                        return (x_inter, y_inter), distance, azimuth1
                    else:
                        return (0, 0), 0, 0
                    
                else:
                    return (0, 0), 0, 0

    # -------------------------------------------------------------------------
    def compute_dist_between_pt_and_route(self, pt : NeacWayPoint, route : NeacRoute) :
        for waypoint in route.way_point_list:
            index_current_wp = route.way_point_list.index(pt)
            if index_current_wp > 0:
                index_previous_wp = index_current_wp - 1
                previous_wp = route.way_point_list[index_previous_wp]

                # route equation
                P = previous_wp
                N = pt
                if (float(N.lon) - float(P.lon)) != 0:
                    a = (float(N.lat) - float(P.lat)) / (float(N.lon) - float(P.lon) )
                    b = float(N.lat) - float(N.lon) * a 

                    # Equation de la droite perpendiculaire
                    if a!=0:
                        ap = -1 / a 
                        bp = pt.lat - pt.lon * ap

                        # Intersection des deux droites
                        x_inter = (bp - b) / (a - ap)
                        y_inter = a * x_inter + b

                        azimuth1, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut(pt.lon, pt.lat, x_inter, y_inter)
                        return (x_inter, y_inter), distance, azimuth1
                    else:
                        return (0, 0), 0, 0
                    
                else:
                    return (0, 0), 0, 0

    # -------------------------------------------------------------------------
    def compute_avoid_route_distance (self, shuttle : NeacShuttle, route : NeacRoute, avoid_point_lon, avoid_point_lat):
        # Equation de la droite d'évitement 
        a = route.a
        b = avoid_point_lat - a * avoid_point_lon

        # Equation de la droite perpendiculaire
        if a!=0:
            ap = -1 / a 
            bp = shuttle.lat - shuttle.lon * ap

            # Intersection des deux droites
            x_inter = (bp - b) / (a - ap)
            y_inter = a * x_inter + b

            azimuth1, azimuth2, distance = self.coordHelper.computeDistanceAndAzimut(shuttle.lon, shuttle.lat, x_inter, y_inter)
            return (x_inter, y_inter), distance, azimuth1
        else:
            return (0, 0), 0, 0
