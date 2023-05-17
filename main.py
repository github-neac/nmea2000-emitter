import logging
from Aspedsa.NeacNmea2000.NeacNmea2000  import NeacNmea2000
from NeacCore.NeacShuttle               import NeacShuttle
from NeacCore.NeacConfig                import NeacConfig

# Version 1

logging.basicConfig(filename='./log/neac_aspedsa.log',level=logging.DEBUG, format='%(asctime)s - %(message)s')
logging.info("Neac Test NMEA - v 1.0")

# ---- NEAC CONFIG WINDOW
config_file_name = "config_test_nmea.json"

# ---- NEAC CONFIG
config = NeacConfig("config/" + config_file_name)

# ---- NEAC SHUTTLE
shuttle    = NeacShuttle (config)
# shuttle.set_location(lon=float(config.simulator.shuttle_longitude), lat=float(config.simulator.shuttle_latitude))
# shuttle.set_current_heading(float(config.simulator.shuttle_heading))
# shuttle.set_current_speed(0)
logging.info("NEAC Shuttle SUCCESSFULLY completed.")

nmea = NeacNmea2000(config, shuttle, "./log/2022 04 30 - nmea_log.csv")
nmea.start()