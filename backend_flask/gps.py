"""
GPS Module for ESP32 MicroPython
Parses NMEA sentences from GPS module (NEO-6M or similar)
Communicates via UART (Serial)
"""

import machine
import time
from math import radians, sin, cos, sqrt, atan2


class GPS:
    """
    GPS class for parsing NMEA data from a serial GPS module.
    
    Usage:
        gps = GPS(rx=16, tx=17, baudrate=9600)
        while True:
            if gps.update():
                print(gps.lat_float(), gps.lon_float())
                print(gps.maps_url())
            time.sleep(1)
    """
    
    def __init__(self, rx=16, tx=17, baudrate=9600):
        """
        Initialize GPS module.
        
        Args:
            rx (int): RX pin number (receives data from GPS module)
            tx (int): TX pin number (transmits to GPS module)
            baudrate (int): Serial baud rate (default 9600)
        """
        self.uart = machine.UART(2, baudrate=baudrate, tx=tx, rx=rx, timeout=100)
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.satellites = 0
        self.hdop = 0.0
        self.has_fix = False
        self.timestamp = None
        self._buffer = ""
        
        # Default fallback location (Barangay Mabolo, Cebu City)
        self.default_lat = 10.294561
        self.default_lon = 122.955432
        
    def update(self):
        """
        Read and parse NMEA sentences from GPS module.
        Should be called frequently (every 100-500ms).
        
        Returns:
            bool: True if a valid fix was obtained, False otherwise
        """
        try:
            # Read available data from UART buffer
            if self.uart.any():
                chunk = self.uart.read(256).decode('utf-8', errors='ignore')
                self._buffer += chunk
                
                # Process complete sentences (end with \r\n)
                while '\r\n' in self._buffer:
                    sentence, self._buffer = self._buffer.split('\r\n', 1)
                    self._parse_sentence(sentence)
            
            # Return whether we have a valid fix
            return self.has_fix
        except Exception as e:
            print(f"[GPS] Error in update(): {e}")
            return False
    
    def _parse_sentence(self, sentence):
        """
        Parse a single NMEA sentence.
        Supports GGA (fix data) and RMC (position, speed, time) formats.
        """
        if not sentence or not sentence.startswith('$'):
            return
            
        try:
            # Remove checksum if present
            if '*' in sentence:
                sentence = sentence.split('*')[0]
            
            parts = sentence[1:].split(',')
            if not parts:
                return
                
            msg_type = parts[0]
            
            # Parse GGA sentence (Global Positioning System Fix Data)
            # $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
            if msg_type.endswith('GGA'):
                self._parse_gga(parts)
            
            # Parse RMC sentence (Recommended Minimum Specific GNSS Data)
            # $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
            elif msg_type.endswith('RMC'):
                self._parse_rmc(parts)
                
        except (IndexError, ValueError, UnicodeDecodeError):
            # Silently ignore malformed sentences
            pass
    
    def _parse_gga(self, parts):
        """Parse GGA (fix) sentence"""
        try:
            if len(parts) < 10:
                return
            
            # Check fix quality (0=no fix, 1=GPS fix, 2=DGPS fix)
            fix_quality = int(parts[6]) if parts[6] else 0
            if fix_quality == 0:
                self.has_fix = False
                return
            
            utc_time = parts[1]  # hhmmss.ss
            lat_str = parts[2]   # ddmm.mmmm
            lat_dir = parts[3]   # N/S
            lon_str = parts[4]   # dddmm.mmmm
            lon_dir = parts[5]   # E/W
            num_sats = parts[7]  # Number of satellites
            hdop_str = parts[8]  # Horizontal dilution of precision
            altitude = parts[9]  # Altitude
            
            # Parse latitude (ddmm.mmmm format)
            if lat_str and lat_dir:
                lat_deg = int(lat_str[:2])
                lat_min = float(lat_str[2:])
                self.latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    self.latitude = -self.latitude
            
            # Parse longitude (dddmm.mmmm format)
            if lon_str and lon_dir:
                lon_deg = int(lon_str[:3])
                lon_min = float(lon_str[3:])
                self.longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    self.longitude = -self.longitude
            
            # Parse altitude
            try:
                self.altitude = float(altitude) if altitude else 0.0
            except ValueError:
                self.altitude = 0.0
            
            # Parse satellites and HDOP
            try:
                self.satellites = int(num_sats) if num_sats else 0
            except ValueError:
                self.satellites = 0
            
            try:
                self.hdop = float(hdop_str) if hdop_str else 0.0
            except ValueError:
                self.hdop = 0.0
            
            self.has_fix = True
            self.timestamp = utc_time
            
        except Exception as e:
            print(f"[GPS] GGA parse error: {e}")
    
    def _parse_rmc(self, parts):
        """Parse RMC (position/time) sentence"""
        try:
            if len(parts) < 9:
                return
            
            utc_time = parts[1]  # hhmmss
            status = parts[2]    # A=active (valid), V=void (invalid)
            lat_str = parts[3]   # ddmm.mmmm
            lat_dir = parts[4]   # N/S
            lon_str = parts[5]   # dddmm.mmmm
            lon_dir = parts[6]   # E/W
            
            # Check data valid
            if status != 'A':
                self.has_fix = False
                return
            
            # Parse latitude
            if lat_str and lat_dir:
                lat_deg = int(lat_str[:2])
                lat_min = float(lat_str[2:])
                self.latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    self.latitude = -self.latitude
            
            # Parse longitude
            if lon_str and lon_dir:
                lon_deg = int(lon_str[:3])
                lon_min = float(lon_str[3:])
                self.longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    self.longitude = -self.longitude
            
            self.has_fix = True
            self.timestamp = utc_time
            
        except Exception as e:
            print(f"[GPS] RMC parse error: {e}")
    
    def lat_float(self):
        """Return latitude as float. Returns 0 if no fix."""
        return self.latitude if self.has_fix else self.default_lat
    
    def lon_float(self):
        """Return longitude as float. Returns 0 if no fix."""
        return self.longitude if self.has_fix else self.default_lon
    
    def altitude_m(self):
        """Return altitude in meters. Returns 0 if no fix."""
        return self.altitude if self.has_fix else 0.0
    
    def get_satellites(self):
        """Return number of satellites used for fix."""
        return self.satellites
    
    def get_hdop(self):
        """Return horizontal dilution of precision."""
        return self.hdop
    
    def maps_url(self):
        """Generate Google Maps URL for current position"""
        lat = self.lat_float()
        lon = self.lon_float()
        return f"https://maps.google.com/?q={lat},{lon}"
    
    def to_dict(self):
        """Return GPS data as dictionary"""
        return {
            "latitude": self.lat_float(),
            "longitude": self.lon_float(),
            "altitude": self.altitude_m(),
            "satellites": self.get_satellites(),
            "hdop": self.get_hdop(),
            "has_fix": self.has_fix,
            "maps_url": self.maps_url(),
            "timestamp": self.timestamp
        }
    
    def __str__(self):
        """String representation"""
        if self.has_fix:
            return f"GPS: {self.latitude:.6f}, {self.longitude:.6f} (Sats: {self.satellites})"
        else:
            return f"GPS: No fix (Default: {self.default_lat:.6f}, {self.default_lon:.6f})"
