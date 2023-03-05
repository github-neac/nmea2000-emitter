import logging
import datetime
# import numpy             as np

from  Aspedsa.NeacNmea2000.NeacSensorStatus import NeacSensorStatus

# ----------------------------------------------------------------------------------------------------------------
class NeacSensor():

    # ----------------------------------------------------------------------------------------------------------------
    def __init__(self, name, type):
        self.status          = NeacSensorStatus.INACTIVE
        self.name            = name
        self.type            = type 
        self.value           = None
        self.unit            = "°"
        self.alert_threshold = 4000
        self.last_update     = datetime.datetime.now()
        self.canvas          = None
        self.canvas_object   = None
        # TODO : utiliser np.ndarray
        self.values          = dict()
        self.chart_image     = None
        logging.info('NeacSensor created (type ' + type + '): ' + name)
        
    # ----------------------------------------------------------------------------------------------------------------
    def set_value(self, new_value, time_stamp):
        if new_value != self.value:
            self.value = new_value
        self.last_update = time_stamp
        self.values[time_stamp] = new_value
        # self.create_chart()

    # ----------------------------------------------------------------------------------------------------------------
    def set_last_update(self, last_update):
        self.last_update = last_update

    # ----------------------------------------------------------------------------------------------------------------
    def update_status(self, status):
        self.status = status

    