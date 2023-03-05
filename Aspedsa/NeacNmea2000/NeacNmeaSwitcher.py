import datetime
import logging

from Aspedsa.NeacNmea2000.NeacAIS          import NeacAIS

# -------------------------------------------------------------------------------------------------------------------------------
class NeacNmeaSwitcher(object):
    def __init__(self, nmea2000, shuttle):
        self.nmea2000 = nmea2000
        self.msg      = None
        self.shuttle  = shuttle

    def select(self, msg):
        self.msg    = msg
        method_name = 'message_' + str(msg.sentence_type)
        method      = getattr(self, method_name, lambda :'Invalid')
        return method()

    # ---- RUDDER
    def message_RSA(self):
        # rudderSensor = self.nmea2000.sensor_list["RUDDER"]
        # rudderSensor.set_value(new_value=self.msg.data[0], time_stamp=datetime.datetime.now())
        # rudderSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        self.shuttle.rudder = float(self.msg.data[0])
        return self.msg.data[0]

    # ---- GPATT
    def message_GPATT(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        try:
            self.shuttle.pitch = float(self.msg.data[3])
            self.shuttle.roll  = float(self.msg.data[4])
        except IndexError:
            logging.error("message_GPATT IndexError")
        return self.msg.data[3]

    # ---- GPATT
    def message_GPATT(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        try:
            self.shuttle.pitch = float(self.msg.data[3])
            self.shuttle.roll  = float(self.msg.data[4])
        except IndexError:
            logging.error("message_GPATT IndexError")
        return self.msg.data[3]

    # ---- GPHVE
    def message_GPHVE(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        self.shuttle.heave = float(self.msg.data[2])
        return self.msg.data[2]

    # ---- TIROT
    def message_ROT(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        try:
            self.shuttle.rate_of_turn = float(self.msg.data[0])
        except:
            logging.error("Error TIROT")
        return self.msg.data[0]

    # ---- WIMDA
    def message_MDA(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        try:
            self.shuttle.pressure = float(self.msg.data[2]) * 1000
        except ValueError:
            self.shuttle.pressure = 0
        self.shuttle.temperature = float(self.msg.data[4])
        return self.msg.data[3]    

    # ---- WINWV
    def message_MWV(self):
        try:
            # windSensor = self.nmea2000.sensor_list["WIND"]
            # windSensor.set_last_update(datetime.datetime.now())
            # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
            self.shuttle.relat_wind_direction = float(self.msg.data[0])
            self.shuttle.relat_wind_speed     = float(self.msg.data[2])
            # windSensor.set_value(self.shuttle.relat_wind_speed, datetime.datetime.now())
            # print(self.shuttle.relat_wind_speed)
            return self.msg.data[3]  
        except:
            return ""

    # ---- RMC
    def message_RMC(self):
        try:
            # gpsSensor = self.nmea2000.sensor_list["GPS"]
            # gpsSensor.set_last_update(datetime.datetime.now())
            # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
            self.shuttle.set_location(float(self.msg.longitude), float(self.msg.latitude))
            self.shuttle.gps_time_stamp = self.msg.datetime
            self.shuttle.current_speed  = float(self.msg.data[6])
            # gpsSensor.set_value(self.shuttle.current_speed, datetime.datetime.now())
            return self.msg.data[3] 
        except:
            return ""
        
    # ---- HEADING True
    def message_HDT(self):
        # gpsSensor = self.nmea2000.sensor_list["GPS"]
        # gpsSensor.set_last_update(datetime.datetime.now())
        # self.nmea2000.sensor_list["NMEA"].set_last_update(datetime.datetime.now())
        self.shuttle.current_heading = float(self.msg.data[0])

    # ---- AIS VDM
    def message_VDM(self):
        # self.nmea2000.sensor_list["AIS"].set_last_update(datetime.datetime.now())
        fragment_count  = int(self.msg.data[0])
        fragment_number = int(self.msg.data[1])
        if fragment_number == 1:
            NeacAIS.reset_message_list()
        NeacAIS.concatenate_payload(self.msg)
        if fragment_count == fragment_number:
            # tous les fragments ont été reçus, on peut analyser le message complet maintenant
            if NeacAIS.analyze_payload() == 1 or NeacAIS.analyze_payload() == 3:
                mmsi               = NeacAIS.MMSI
                navigation_status  = NeacAIS.navigation_status
                rate_of_turn       = NeacAIS.rate_of_turn
                speed_over_ground  = NeacAIS.speed_over_ground 
                position_accuracy  = NeacAIS.position_accuracy
                longitude          = NeacAIS.longitude
                latitude           = NeacAIS.latitude
                course_over_ground = NeacAIS.course_over_ground
                true_heading       = NeacAIS.course_over_ground
                time_stamp         = NeacAIS.time_stamp
                maneuver_indicator = NeacAIS.maneuver_indicator
                radio_status       = NeacAIS.radio_status
                self.shuttle.update_AIS_type_1_3(mmsi, longitude, latitude, position_accuracy, navigation_status, rate_of_turn, speed_over_ground, course_over_ground, true_heading, time_stamp, maneuver_indicator, radio_status)

            elif NeacAIS.analyze_payload() == 5:
                mmsi                   = NeacAIS.MMSI
                vessel_name            = NeacAIS.vessel_name 
                ship_type              = NeacAIS.ship_type
                dimension_to_bow       = NeacAIS.dimension_to_bow
                dimension_to_stern     = NeacAIS.dimension_to_stern
                dimension_to_port      = NeacAIS.dimension_to_port
                dimension_to_starboard = NeacAIS.dimension_to_starboard
                self.shuttle.update_AIS_type_5(mmsi, vessel_name, ship_type, dimension_to_bow, dimension_to_stern, dimension_to_port, dimension_to_starboard)

    # ---- AIS VDO
    def message_VDO(self):
        self.nmea2000.sensor_list["AIS"].set_last_update(datetime.datetime.now())
        fragment_count = self.msg.data[0]
        fragment_number = self.msg.data[1]
        # TODO : Implémenter le message VDO


