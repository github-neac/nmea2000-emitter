from enum import Enum

class NeacSensorStatus(Enum):
    INACTIVE = 0 
    ACTIVE   = 1
    ERROR    = 2
    WARNING  = 3
    TIMEOUT  = 4