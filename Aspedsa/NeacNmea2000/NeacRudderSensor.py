from  NeacNmea2000.NeacSensor import NeacSensor

class NeacRudderSensor(NeacSensor):
    
    def __init__(self, canvas):
        NeacSensor.__init__(self, canvas)
        self.name   = "RUDDER"
        self.unit   = "°"



        
