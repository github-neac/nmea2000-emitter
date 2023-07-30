import serial
import io
import logging
import time
import threading

class NeacNmea2000(threading.Thread):
    def __init__(self, config, shuttle, replay_file, timeout_retrying_delay = 5):
        threading.Thread.__init__(self, name="NeacNmea2000")
        self.shuttle = shuttle
        self.config = config
        self.serial_port  = None
        self.replay_file  = replay_file
        self.nmea_flow    = None
        self.nmea_write   = None

    # ----------------------------------------------------------------------------------------------------------------
    def run(self):
        message_id = 0
        if self.replay_file is not None:
            logging.info("NMEA replay file : " + self.replay_file)
            self.nmea_flow  = open(file=self.replay_file)
            line = self.nmea_flow.readline()

            self.nmea_write = self.start_serial_port()

            while line:
                line = self.nmea_flow.readline()
                if line != '':
                    nmea_message = line[line.index(';')+1:]
                    
                    if self.nmea_write != None:
                        nmea_trame = nmea_message.encode('utf-8')[:(len(nmea_message)-1)] + b'\r\n'
                        # nmea_trame = b'$HEHDT,309.35,T*13' + b'\r\n'
                        # nmea_trame = b'$GPVTG,20.89,T,,M,4.80,N,8.88,K,D*0F' + b'\r\n'
                        # nmea_trame = b'$TIROT,189.53,A*0D' + b'\r\n'
                        # nmea_trame = b'$GPGGA,164912.600,4911.76449,N,00019.25818,W,2,20,0.80,50.85,M,47.50,M,,*4D' + b'\r\n'
                        # nmea_trame = b'$AGRSA,-18.08,A,,V*53' + b'\r\n'
                        
                        cross_track_error_magnitude              = '37.14'
                        direction_to_steer                       = 'R'
                        cross_track_units                        = 'N'
                        bearing_origin_to_destination            = '180.3'
                        destination_waypoint_id                  = '69'
                        bearing_present_position_to_Destination  = '336.4' # Relèvement du point à atteindre;
                        heading_to_steer_to_destination_waypoint = '56.4'

                        # --- Décommenter ces 3 lignes pour générer un message APB
                        # message = 'IIAPB,A,A,' + cross_track_error_magnitude + ',' + direction_to_steer + ',' + cross_track_units + ',A,A,' + bearing_origin_to_destination + ',M,' + destination_waypoint_id + ',' + bearing_present_position_to_Destination + ',M,' + heading_to_steer_to_destination_waypoint + ',M,D'
                        # checksum    = self.compute_nmea_checksum(message)
                        # nmea_trame  = b'$' + message.encode('utf-8') + b'*' + checksum.encode('utf-8') + b'\r\n'

                        try:
                            nb_bytes   = self.serial_port.write(nmea_trame)
                        except PermissionError:
                            print ("Error while writing to port !")
                            self.serial_port.flush()
                        print ("   message_id = " + str(message_id) + " - message = " + nmea_trame.decode("utf-8", "strict")  )
                        time.sleep(0.5)
                        message_id = message_id + 1
                        
            self.nmea_flow.close()
        else : 
            print ("ERROR :NMEA log file not provided !")
       

    # ----------------------------------------------------------------------------------------------------------------
    def start_serial_port(self):
        try:
            self.serial_port = serial.Serial(self.config.nmea2000.COM_PORT, baudrate=38400, timeout=0, write_timeout=0, rtscts=0)
            if (self.serial_port.isOpen() == False):
                try:
                    self.serial_port.open()
                    print("NMEA200 : port " + self.config.nmea2000.COM_PORT + " opened sucessfully")
                except serial.serialutil.SerialException:
                   print("NMEA200 Start Error : Could not open serial port : " + self.config.nmea2000.COM_PORT)
            else:
                print("NMEA200 Start open serial port : " + self.config.nmea2000.COM_PORT)
            sio = io.TextIOWrapper(io.BufferedRWPair(self.serial_port, self.serial_port))
            return sio
        except serial.serialutil.SerialException:
            print("Unable to open serial port")
            self.serial_port = None

    # -------------------------------------------------------------------------------------------------------------------------------
    def compute_nmea_checksum(self, cmd):
        # Compute the checksum by XORing all the character values in the string.
        checksum = 0
        for char in cmd:
            checksum ^= ord(char)

        # Convert it to hexadecimal (base-16, upper case, most significant nybble first).
        hexsum = str(hex(checksum))[2:].upper()
        if len(hexsum) < 2:
            hexsum = ("00" + hexsum)[-2:]

        return hexsum
