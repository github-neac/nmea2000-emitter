import decimal
import logging

from numpy import character

class NeacAIS():
    """
        AIS Message decoder
    """

    __message_list=[]
    __bin_payload = ""

    ais_message_type = [(0, "Unknown"),
                        (1, "Position Report Class A"),
                        (2, "Position Report Class A (Assigned schedule)"),
                        (3, "Position Report Class A (Response to interrogation)"),
                        (4, "Base Station Report"),
                        (5, "Static and Voyage Related Data"),
                        (6, "Binary Addressed Message"),
                        (7, "Binary Acknowledge"),
                        (8, "Binary Broadcast Message"),
                        (9, "Standard SAR Aircraft Position Report"),
                        (10, "UTC and Date Inquiry"),
                        (11, "UTC and Date Response"),
                        (12, "Addressed Safety Related Message"),
                        (13, "Safety Related Acknowledgement"),
                        (14, "Safety Related Broadcast Message"),
                        (15, "Interrogation"),
                        (16, "Assignment Mode Command"),
                        (17, "DGNSS Binary Broadcast Message"),
                        (18, "Standard Class B CS Position Report"),
                        (19, "Extended Class B Equipment Position Report"),
                        (20, "Data Link Management"),
                        (21, "Aid-to-Navigation Report"),
                        (22, "Channel Management"),
                        (23, "Group Assignment Command"),
                        (24, "Static Data Report"),
                        (25, "Single Slot Binary Message"),
                        (26, "Multiple Slot Binary Message With Communications State"),
                        (27, "Position Report For Long-Range Applications") ]

    ais_navigation_status = [(0, "Under way using engine"),
                             (1, "At anchor"),
                             (2, "Not under command"),
                             (3, "Restricted manoeuverability"),
                             (4, "Constrained by her draught"),
                             (5, "Moored"),
                             (6, "Aground"),
                             (7, "Engaged in Fishing"),
                             (8, "Under way sailing"),
                             (9, "Reserved for future amendment of Navigational Status for HSC"),
                             (10, "Reserved for future amendment of Navigational Status for WIG"),
                             (11, "Reserved for future use"),
                             (12, "Reserved for future use"),
                             (13, "Reserved for future use"),
                             (14, "AIS-SART is active"),
                             (15, "Not defined (default)")]
                        
    ais_maneuver_indicator = [(0, "Not available (default)"),
                              (1, "No special maneuver"),
                              (2, "Special maneuver (such as regional passing arrangement)")]

    ais_ship_type = [ (0, "Not available (default)"),
                      (1, "Reserved for future use"),(18, "Reserved for future use"),(35, "Military ops"),(52,"Tug"),(53, "Port Tender"),(70, "Cargo, all ships of this type"),(87, "Tanker, Reserved for future use"),
                      (2, "Reserved for future use"),(19, "Reserved for future use"),(36, "Sailing"),(54, "Anti-pollution equipment"),(71, "Cargo, Hazardous category A"),(88, "Tanker, Reserved for future use"),
                      (3, "Reserved for future use"),(20, "Wing in ground (WIG), all ships of this type"),(37, "Pleasure Craft"),(55, "Law Enforcement"),(72, "Cargo, Hazardous category B"),(89, "Tanker, No additional information"),
                      (4, "Reserved for future use"),(21, "Wing in ground (WIG), Hazardous category A"),(38, "Reserved"),(56, "Spare - Local Vessel"),(73, "Cargo, Hazardous category C"),(90, "Other Type, all ships of this type"),
                      (5, "Reserved for future use"),(22, "Wing in ground (WIG), Hazardous category B"),(39, "Reserved"),(57, "Spare - Local Vessel"),(74, "Cargo, Hazardous category D"),(91, "Other Type, Hazardous category A"),
                      (6, "Reserved for future use"),(23, "Wing in ground (WIG), Hazardous category C"),(40, "High speed craft (HSC), all ships of this type"),(58, "Medical Transport"),(75, "Cargo, Reserved for future use"),(92, "Other Type, Hazardous category B"),
                      (7, "Reserved for future use"),(24, "Wing in ground (WIG), Hazardous category D"),(41, "High speed craft (HSC), Hazardous category A"),(59, "Noncombatant ship according to RR Resolution No. 18"),(76, "Cargo, Reserved for future use"),(93, "Other Type, Hazardous category C"),
                      (8, "Reserved for future use"),(25, "Wing in ground (WIG), Reserved for future use"),(42, "High speed craft (HSC), Hazardous category B"),(60, "Passenger, all ships of this type"),(77, "Cargo, Reserved for future use"),(94, "Other Type, Hazardous category D"),
                      (9, "Reserved for future use"),(26, "Wing in ground (WIG), Reserved for future use"),(43, "High speed craft (HSC), Hazardous category C"),(61, "Passenger, Hazardous category A"),(78, "Cargo, Reserved for future use"),(95, "Other Type, Reserved for future use"),
                      (10, "Reserved for future use"),(27, "Wing in ground (WIG), Reserved for future use"),(44, "High speed craft (HSC), Hazardous category D"),(62, "Passenger, Hazardous category B"),(79, "Cargo, No additional information"),(96, "Other Type, Reserved for future use"),
                      (11, "Reserved for future use"),(28, "Wing in ground (WIG), Reserved for future use"),(45, "High speed craft (HSC), Reserved for future use"),(63, "Passenger, Hazardous category C"),(80, "Tanker, all ships of this type"),(97, "Other Type, Reserved for future use"),
                      (12, "Reserved for future use"),(29, "Wing in ground (WIG), Reserved for future use"),(46, "High speed craft (HSC), Reserved for future use"),(64, "Passenger, Hazardous category D"),(81, "Tanker, Hazardous category A"),(98, "Other Type, Reserved for future use"),
                      (13, "Reserved for future use"),(30, "Fishing"),(47, "High speed craft (HSC), Reserved for future use"),(65, "Passenger, Reserved for future use"),(82, "Tanker, Hazardous category B"),(99, "Other Type, no additional information"),
                      (14, "Reserved for future use"),(31, "Towing"),(48, "High speed craft (HSC), Reserved for future us"),(66, "Passenger, Reserved for future use"),(83, "Tanker, Hazardous category C"),
                      (15, "Reserved for future use"),(32, "Towing: length exceeds 200m or breadth exceeds 25m"),(49, "High speed craft (HSC), No additional information"),(67, "Passenger, Reserved for future use"),(84, "Tanker, Hazardous category D"),
                      (16, "Reserved for future use"),(33, "Dredging or underwater ops"),(50, "Pilot Vessel"),(68, "Passenger, Reserved for future use"),(85, "Tanker, Reserved for future use"),
                      (17, "Reserved for future use"),(34, "Diving ops"),(51, "Search and Rescue vessel"),(69, "Passenger, No additional information"),(86, "Tanker, Reserved for future use")
    ]

    # ---- Message Type 1, 2 and 3
    message_type       = None
    MMSI               = None
    navigation_status  = None
    rate_of_turn       = None
    speed_over_ground  = None
    position_accuracy  = None
    longitude          = None
    latitude           = None
    course_over_ground = None
    true_heading       = None
    time_stamp         = None
    maneuver_indicator = None
    radio_status       = None

    # ---- Message Type 5
    vessel_name            = None
    ship_type              = None
    dimension_to_bow       = None
    dimension_to_stern     = None
    dimension_to_port      = None
    dimension_to_starboard = None


    # -------------------------------------------------------------------------
    @staticmethod
    def reset_message_list():
        NeacAIS.__message_list=[]
        NeacAIS.__bin_payload = ""

    # -------------------------------------------------------------------------
    @staticmethod
    def add_message(msg):
        if msg.data[1] == 1:
           NeacAIS.reset_message_list()

        NeacAIS.__message_list.append(msg)

    # -------------------------------------------------------------------------
    @staticmethod
    def concatenate_payload(msg):
        payload = msg.data[4]
        try:
            for the_char in payload:
                decimal_value = ord(the_char) - 48
                if decimal_value > 40:
                    decimal_value -= 8
                NeacAIS.__bin_payload = NeacAIS.__bin_payload + format(decimal_value, '06b')
        except:
            logging.error("AIS decrypt message error" + payload)
        return True

    # -------------------------------------------------------------------------
    @staticmethod
    def analyze_payload():
        # print ("  Payload = " + NeacAIS.__bin_payload)

        message_type = NeacAIS.__bin_payload[0:6]
        # print ("  Message Type = " + str(message_type) + " = " + str(int(message_type,2)) + " = " +  str(NeacAIS.ais_message_type[int(message_type,2)]))
        NeacAIS.message_type = NeacAIS.ais_message_type[int(message_type,2)]

        if NeacAIS.message_type[0] >=1 and NeacAIS.message_type[0] <= 3:
            # Type 1, 2 and 3 messages share a common reporting structure for navigational information; we’ll call it the Common Navigation Block (CNB). 
            # This is the information most likely to be of interest for decoding software. Total of 168 bits, occupying one AIVDM sentence.

            repeat_indicator = NeacAIS.__bin_payload[6:8]
            NeacAIS.repeat_indicator = int(repeat_indicator,2)
            mmsi = NeacAIS.__bin_payload[8:38]
            NeacAIS.MMSI = int(mmsi,2)
            navigation_status = NeacAIS.__bin_payload[38:42]
            NeacAIS.navigation_status = NeacAIS.ais_navigation_status[int(navigation_status,2)]
            rate_of_turn = NeacAIS.__bin_payload[42:50]
            NeacAIS.rate_of_turn = int(rate_of_turn,2)
            speed_over_ground = NeacAIS.__bin_payload[50:60]
            NeacAIS.speed_over_ground = int(speed_over_ground,2) / 10
            position_accuracy = NeacAIS.__bin_payload[60:61]
            NeacAIS.position_accuracy = int(position_accuracy,2)
            longitude = NeacAIS.__bin_payload[61:89]
            NeacAIS.longitude = NeacAIS.calc_longitude(longitude)
            latitude = NeacAIS.__bin_payload[89:116]
            NeacAIS.latitude = NeacAIS.calc_latitude(latitude)
            course_over_ground = NeacAIS.__bin_payload[116:128]
            NeacAIS.course_over_ground = int(course_over_ground, 2) / 10
            true_heading       = NeacAIS.__bin_payload[128:137]
            NeacAIS.true_heading = true_heading
            time_stamp         = NeacAIS.__bin_payload[137:143]
            NeacAIS.time_stamp = time_stamp
            maneuver_indicator = NeacAIS.__bin_payload[143:145]
            NeacAIS.maneuver_indicator = NeacAIS.ais_maneuver_indicator[int(maneuver_indicator)]
            radio_status       = NeacAIS.__bin_payload[149:168]
            NeacAIS.radio_status = radio_status
            
            return NeacAIS.message_type[0]

        elif NeacAIS.message_type[0] == 5:
            mmsi = NeacAIS.__bin_payload[8:38]
            NeacAIS.MMSI = int(mmsi,2)

            vessel_name = ""
            for letter_index in range(0, 119):
                bin_letter = NeacAIS.__bin_payload[112+letter_index*6:112+letter_index*6+6]
                if bin_letter!='':
                    letter = chr(int(bin_letter,2)+48+16)
                    vessel_name = vessel_name + letter
            # vessel_name = NeacAIS.__bin_payload[112:232]
            NeacAIS.vessel_name            = vessel_name

            NeacAIS.ship_type              = NeacAIS.ais_ship_type[int(NeacAIS.__bin_payload[232:240], 2)]
            NeacAIS.dimension_to_bow       = int(NeacAIS.__bin_payload[240:249], 2)
            NeacAIS.dimension_to_stern     = int(NeacAIS.__bin_payload[249:258], 2)
            NeacAIS.dimension_to_port      = int(NeacAIS.__bin_payload[258:264], 2)
            NeacAIS.dimension_to_starboard = int(NeacAIS.__bin_payload[264:270], 2)
            return NeacAIS.message_type[0]

        else:
             print (" ******** Message Type = " + str(int(message_type,2)))
             logging.warn(" ******** Message Type = " + str(int(message_type,2)))

    
    # -------------------------------------------------------------------------
    @staticmethod
    def calc_longitude(binary_longitude):
        sign      = int(binary_longitude[0])
        longitude = int(binary_longitude[1:],2)
        nr_bits   = len(binary_longitude)
        if nr_bits == 25:
            factor = 60000 # 1000 * 60
            power  = 24
        elif nr_bits == 28:
            factor = 600000 # 10000 * 60
            power  = 27
        else:
            return None
        if longitude == 181*factor:
            return None # N/A = The longitude are undefined (long=181)
        if sign: # Negative == West
            longitude = pow(2,power) - longitude
            degree = -decimal.Decimal(longitude) / factor
        else: # Positive == East
            degree = decimal.Decimal(longitude) / factor
        return degree.quantize(decimal.Decimal('1E-6'))

    # -------------------------------------------------------------------------
    @staticmethod
    def calc_latitude(binary_latitude):
        sign     = int(binary_latitude[0])
        latitude = int(binary_latitude[1:],2)
        nr_bits  = len(binary_latitude)
        if nr_bits == 24:
            factor = 60000 # 1000 * 60
            power  = 23
        elif nr_bits == 27:
            factor = 600000 # 10000 * 60
            power  = 26
        else:
            return None
        # See if the latitude are undefined (lat=91)
        if latitude == 91*factor:
            return None # N/A
        if sign: # Negative == South
            latitude = pow(2,power) - latitude
            degree = -decimal.Decimal(latitude) / factor
        else: # Positive == North
            degree = decimal.Decimal(latitude) / factor
        return degree.quantize(decimal.Decimal('1E-6'))