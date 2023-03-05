from NeacCore.NeacLocation import NeacLocation

class NeacAvoidPoint(NeacLocation):
    """
        Avoid Point. Used to represent a new point on the current route to avoid collision with an UFO. 

        :param NeacShuttle shuttle: shuttle.
        :param NeacUfo ufo: Corresponding UFO.
     """

    #--------------------------------------------------------------------------
    def __init__(self):
        NeacLocation.__init__(self)
        self.shuttle        = None
        self.ufo            = None

__all__ = [
    'NeacAvoidPoint'
]