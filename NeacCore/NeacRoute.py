from NeacCore.NeacLocation import NeacLocation
from NeacCore.NeacStation import NeacStation
from NeacCore.NeacWayPoint import NeacWayPoint
from NeacCore.NeacConstant import NAVIGATION_MODE
from random                import randrange
import logging

class NeacRoute:
    """
        A route is a list of Waypoints (NeacWayPoint)
    """
    
    #--------------------------------------------------------------------------
    def __init__(self, name:str=""):
        self.name                  = name
        self.destination_station   = None
        self.way_point_list        = []
        self.a                     = 0 # Coefficient directeur de la droite du tronçon de la route en cours de parcours
        self.b                     = 0

    #--------------------------------------------------------------------------
    def set_destination_station (self, station : NeacStation) -> None: 
        """
            Set the NeacStation Destination of the route. It is used when searching for
            which routes are sending to a specific destination
        """
        self.destination_station = station

    #--------------------------------------------------------------------------
    def add_way_point(self, new_way_point : NeacWayPoint) -> None:
        """
            Insert the new_waypoint at the end of the route

            :param NeacWayPoint new_way_point: waypoint to be inserted into the route            
            :returns: None
        """
        self.way_point_list = self.way_point_list + [new_way_point]

    #--------------------------------------------------------------------------
    def insert_way_point(self, new_way_point=None, position=None) :
        """
            Check if the new_way_point is alredy in the route. 
            If not, then insert the new_way_point into the route at the given position.  

            :param NeacWayPoint new_way_point: waypoint to be inserted
            :param int          position: Position in the list
            :returns: index position of the waypoint in the route, -1 if the waypoint is not is the route
        """
        found = False
        for wp in self.way_point_list:
            if wp.name == new_way_point.name and wp.lon==new_way_point.lon and wp.lat==new_way_point.lat:
                return self, None

        self.way_point_list = self.way_point_list[:position] + [new_way_point] + self.way_point_list[position:] 
        return self, new_way_point

    #--------------------------------------------------------------------------
    def get_current_wp_index(self, searched_wp) -> int:
        """
            Return the index position of the waypoint in the route

            :param NeacWayPoint searched_wp: waypoint to be searched
            :returns: index position of the waypoint in the route, -1 if the waypoint is not is the route
        """
        for i,wp in enumerate(self.way_point_list):
            if wp == searched_wp:
                return i
        return -1

__all__ = [
    'NeacRoute', 'set_destination_station', 'add_way_point','insert_way_point','get_current_wp_index'
]