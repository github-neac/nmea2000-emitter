# Test de génération d'un message NMEA2000 $APB

# -------------------------------------------------------------------------------------------------------------------------------
def compute_nmea_checksum(cmd):
    # Compute the checksum by XORing all the character values in the string.
    checksum = 0
    for char in cmd:
        checksum ^= ord(char)

    # Convert it to hexadecimal (base-16, upper case, most significant nybble first).
    hexsum = str(hex(checksum))[2:].upper()
    if len(hexsum) < 2:
        hexsum = ("00" + hexsum)[-2:]

    return hexsum

# -------------------------------------------------------------------------------------------------------------------------------
cross_track_error_magnitude              = '37.14'
direction_to_steer                       = 'L'
cross_track_units                        = 'N'
bearing_origin_to_destination            = '180.3'
destination_waypoint_id                  = '69'
bearing_present_position_to_Destination  = '336.4' # Relèvement du point à atteindre;
heading_to_steer_to_destination_waypoint = '56.4'

message    = 'IIAPB,A,A,' + cross_track_error_magnitude + ',' + direction_to_steer + ',' + cross_track_units + ',V,V,' + bearing_origin_to_destination + ',M,' + destination_waypoint_id + ',' + bearing_present_position_to_Destination + ',M,' + heading_to_steer_to_destination_waypoint + ',M,D'
checksum   = compute_nmea_checksum(message)
nmea_trame = b'$' + message.encode('utf-8') + b'*' + checksum.encode('utf-8') + b'\r\n'

print (nmea_trame)

# Résultat : b'$IIAPB,A,A,37.14,L,N,V,V,180.3,M,69,336.4,M,56.4,M,D*45\r\n'