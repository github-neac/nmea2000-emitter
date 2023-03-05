import logging

from NeacCore.NeacCollisionPoint import NeacCollisionPoint
from NeacCore.NeacAvoidPoint     import NeacAvoidPoint
from NeacCore.NeacConstant       import DRC_MODE
from NeacCore.NeacConstant       import NAVIGATION_MODE
from NeacCore.NeacCoordHelper    import NeacCoordHelper
from NeacCore.NeacUfo            import NeacUfo
from NeacCore.NeacWayPoint       import NeacWayPoint

class NeacDrc ():
    """
        Neac Detect Route Collision
    """

    # -------------------------------------------------------------------------
    def __init__(self, shuttle):
        self.shuttle      = shuttle
        self.coordHelper  = None
        
    # -------------------------------------------------------------------------
    def estimate_ufo_r_pref_collision(self, ufo : NeacUfo, coordHelper : NeacCoordHelper) -> bool:
        """
            Compute the intersection point(s) between the current shuttle route and 
            each segment of the r_pref_polygon
        """
        ufo.drc_mode   = DRC_MODE.IGNORE
        avoid_waypoint = None
        max_azimut     = 0

        # TODO : Ne pas prendre le prochain point de la route, mais le vecteur vitesse du navire. 
        if self.shuttle.target != None:
            shuttleA, shuttleB = self.get_a_and_b([self.shuttle.lon, self.shuttle.lat], [self.shuttle.target.lon, self.shuttle.target.lat])

            if ufo.r_pref_polygon:
                nb_segments  = len(ufo.r_pref_polygon)
                min_distance = 99999999
                returned_cp  = None
                for segment_id in range(0,nb_segments-1):
                    point_1    = ufo.r_pref_polygon[segment_id]
                    point_2    = ufo.r_pref_polygon[segment_id+1]
                    ufoA, ufoB = self.get_a_and_b(point_1, point_2)

                    avoid_azimuth1, avoid_azimuth2, avoid_distance = coordHelper.computeDistanceAndAzimut(self.shuttle.lon, self.shuttle.lat, point_1[0], point_1[1])
                    if avoid_azimuth1 > 180:
                        avoid_azimuth1 =  avoid_azimuth1 - 360

                    if avoid_azimuth1 > max_azimut and abs(avoid_azimuth1) < 90:
                        avoid_waypoint = NeacAvoidPoint()
                        avoid_waypoint.lon = point_1[0]
                        avoid_waypoint.lat = point_1[1]
                        max_azimut     = avoid_azimuth1

                    # if (shuttleA - ufoA) != 0 and avoid_distance<80: # Les 2 routes se croisent à moins de 80 mètres de distance
                    if (shuttleA - ufoA) != 0 : # Les 2 routes se croisent à moins de 80 mètres de distance
                        lonCollision = (ufoB - shuttleB) / (shuttleA - ufoA)
                        latCollision = shuttleA * lonCollision + shuttleB

                        # Recherche si le point d'intersection est bien sur le segment
                        if point_2[0]-point_1[0] !=0 and point_2[1]-point_1[1] !=0:
                            X = (lonCollision - point_1[0])/(point_2[0]-point_1[0])
                            Y = (latCollision - point_1[1])/(point_2[1]-point_1[1])

                            if int(X*1000)==int(Y*1000) and X>=0 and Y<=1: # Le point de collision est sur le segment
                                
                                # Calcul distance et azimut avec le point CPA
                                azimuth1, azimuth2, distance = coordHelper.computeDistanceAndAzimut(self.shuttle.lon, self.shuttle.lat, lonCollision, latCollision)
                                angle_azimuth                = self.compute_angle(azimuth1, self.shuttle.current_heading)
                                if distance < min_distance: # and angle_azimuth < 90: # On ne retient le point que si c'est le plus proche, et devant le bateau
                                    cp = NeacCollisionPoint()
                                    cp.ufo       = ufo
                                    cp.shuttle   = self.shuttle
                                    cp.lon       = lonCollision
                                    cp.lat       = latCollision

                                    returned_cp  = cp
                                    ufo.drc_mode = DRC_MODE.RISK
                                    min_distance = distance
                                else:
                                    print ("azimuth1 : " + str(azimuth1) + " - current_heading : "  + str(self.shuttle.current_heading))

                    else : # Les 2 routes sont paralèlles, ou bien confondues
                        # TODO : Tester si b = b prime --> collision assurée !
                        lonCollision = 0
                        latCollision = 0
                    
                if returned_cp != None:
                    self.shuttle.collision_points += [returned_cp]
                    # Set the new avoid point only if it is closer than the current one :
                    closest_avoid_point = self.get_closest_avoid_point(self.shuttle.avoid_point, avoid_waypoint, coordHelper)
                    
                    if closest_avoid_point != None:
                        targetWaypoint      = NeacWayPoint("Avoid UFO " + str(ufo.name))
                        targetWaypoint.lon  = closest_avoid_point.lon
                        targetWaypoint.lat  = closest_avoid_point.lat
                        targetWaypoint.mode = NAVIGATION_MODE.AVOID

                        self.shuttle.set_distance_to_target(avoid_distance)
                        self.shuttle.mode = NAVIGATION_MODE.AVOID
                        self.shuttle.avoid_point = targetWaypoint
                        return True
                return False
    
    #--------------------------------------------------------------------------
    def estimate_ufo_next_position(self, ufo: NeacUfo, coordHelper : NeacCoordHelper):
        """
            Compute the UFO next position in 30sec and 1min
        """
        next_time_in_sec = 30
        distance_30_seconds = ufo.speed * 1852 / 60 / 60 * next_time_in_sec
        ufo.lon_30s, ufo.lat_30s = coordHelper.getCoordFromDistanceAndAngle(ufo.lon, ufo.lat, distance_30_seconds, ufo.heading)

    #--------------------------------------------------------------------------
    def compute_angle(self, angle1, angle2):
        """
            Calcul la valeur absolue de l'angle entre les deux caps
        """
        if abs(angle1 - angle2) > 180:
            new_angle1 = max(angle1, angle2) - 360
            new_angle2 = min(angle1, angle2)
            return abs(new_angle1 - new_angle2)
        return abs(angle1 - angle2)

    #--------------------------------------------------------------------------
    def get_closest_avoid_point(self, shuttle_avoid_point, new_avoid_point, coordHelper):
        """
            return the closest point from the shuttle
        """
        if self.shuttle.avoid_point!=None and new_avoid_point!=None:
            azimuth1, azimuth2, distance_current_avoid_point = coordHelper.computeDistanceAndAzimut(self.shuttle.lon, self.shuttle.lat, shuttle_avoid_point.lon, shuttle_avoid_point.lat)
            azimuth1, azimuth2, distance_new_avoid_point     = coordHelper.computeDistanceAndAzimut(self.shuttle.lon, self.shuttle.lat, new_avoid_point.lon,     new_avoid_point.lat)
            if distance_new_avoid_point < distance_current_avoid_point:
                return new_avoid_point
            else:
                return shuttle_avoid_point
        else:
            return new_avoid_point

    #--------------------------------------------------------------------------
    def get_a_and_b(self, point_1, point_2):
        """
            Retourne les paramètres de l'équation de la droite
        """
        # TODO : Ne vaudrait il pas mieux travailler sur les projections en Lambert ? 
        a  = 0
        b  = 0
        i2 = point_2
        i1 = point_1
        if (i2[0] - i1[0]) != 0:
            a = (i2[1] - i1[1]) / (i2[0] - i1[0])   
        else:
            a = 0
        b = i2[1] - a * i2[0]
        # logging.debug("i2.lat: " + str(i2[1]) + " - i1.lat: " + str(i1[1]) + " - i2.lon: " + str(i2[0]) + " - i1.lon: " + str(i1[0]))
        # logging.debug("getAandB() : a=" + str(a) + " b=" + str(b) )
        return a, b



__all__ = [
    'NeacDrc', 'get_a_and_b', 'estimate_ufo_r_pref_collision', 'compute_angle', 'estimate_ufo_next_position'
]
