from  NeacNmea2000.NeacSensor import NeacSensor

class NeacNmea(NeacSensor):
    
    def __init__(self, canvas):
        NeacSensor.__init__(self, canvas)
        self.name   = "NMEA"
        self.unit   = ""



        
