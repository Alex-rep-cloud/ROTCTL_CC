""" Alexandre Hachet

Classe qui fait l'interface entre python et la librairie ROTCTL.
Documentation reprise depuis celle de la librairie ROTCTL.

Commands (some may not be available for this rotator):
P: set_pos     (Azimuth, Elevation)
p: get_pos     ()
K: park        ()
S: stop        ()
R: reset       (Reset)
M: move        (Direction, Speed)
V: set_level   (Level, Level Value)
v: get_level   (Level)
U: set_func    (Func, Func Status)
u: get_func    (Func)
X: set_parm    (Parm, Parm Value)
x: get_parm    (Parm)
C: set_conf    (Token, Value)
_: get_info    ()
s: get_status  ()
w: send_cmd    (Cmd)
1: dump_caps   ()
3: dump_conf   ()
?: dump_state  ()
L: lonlat2loc  (Longitude, Latitude, Loc Len [2-12])
l: loc2lonlat  (Locator)
D: dms2dec     (Degrees, Minutes, Seconds, S/W)
d: dec2dms     (Dec Degrees)
E: dmmm2dec    (Degrees, Dec Minutes, S/W)
e: dec2dmmm    (Dec Deg)
B: qrb         (Lon 1, Lat 1, Lon 2, Lat 2)
A: a_sp2a_lp   (Short Path Deg)
a: d_sp2d_lp   (Short Path km)
?: pause       (Seconds)
?: get_conf    (Token)
"""

import pexpect

class ROTCTL:

    # @move parameters
    UP = "2"
    DOWN = "4"
    LEFT = "8"
    RIGHT = "16"

    # S/W paramaters
    NORTH_EAST = "0"
    SOUTH_WEST = "1"

    def __init__(self, model=1, device="/dev/ttyUSB0", timeout=3):
        cmd = f"rotctl -m {model} -r {device}"
        self.child = pexpect.spawn(cmd, encoding="utf-8", timeout=timeout)
        try:
            self.child.expect(r"Rotator command:\s*", timeout=timeout)
        except pexpect.TIMEOUT:
            print("Error while connecting to the rotor.")

    def __str__(self):
        return self._get_info()

    def send(self, command, timeout=3):
        """
        Send messages through the child process.
        """
        self.child.sendline(command)
        self.child.expect(r"Rotator command:\s*", timeout=timeout)
        out = self.child.before.strip()

        if out.startswith(command):
            out = out[len(command):].strip()
        return out
    
    def set_pos(self, az, el):
        """
        Set position.
        'Azimuth' and 'Elevation' are floating point values.
        Azimuth can be -180 to 540 depending on the rotator to allow for rotators facing south and the capabilities of the rotator.
        Elevation can be -20 to 210 depending on the rotator.
        For example:
        P 163.0 41.0
        Note: If the rotator does not support setting elevation (most do not) supply “0.0” for 'Elevation'.
        """
        try:
            return self.send(f"P {az} {el}")
        except Exception:
            return False
        
    def get_pos(self):
        """
        Get position.
        'Azimuth' and 'Elevation' are returned as double precision floating point values.
        Format: Azimuth: (value)\r\nElevation: (value)
        """
        try:
            return self.send("p")
        except Exception:
            return False
        
    def move(self, dir, speed):
        """
        Move the rotator in a specific direction at the given rate.
        'Direction' is an integer or keyword defined as '2' = UP, '4' = DOWN, '8' = LEFT or CCW and '16' = RIGHT or CW
        'Speed' is an integer between 1 and 100. Use -1 for no change to current speed.
        Note: Not all backends that implement the move command use the Speed value.
        """
        try:
            return self.send(f"M {dir} {speed}")
        except Exception:
            return False
        
    def stop(self):
        """
        Stop the rotator
        """
        try:
            return self.send("S")
        except Exception:
            return False
        
    def park(self):
        """
        Park the rotator
        """
        try:
            return self.send("K")
        except Exception:
            return False
        
    def _get_info(self):
        """
        Get miscellaneous information about the rotator.
        Returns 'Info' “Model Name” at present.
        """
        try:
            return self.send("_")
        except Exception:
            return False

    def exit(self):
        """
        Exit rotctl in interactive mode.
        When rotctl is controlling the rotator directly, will close the rotator backend and port. 
        When rotctl is connected to rotctld (rotator model 2), the TCP/IP connection to rotctld is closed and rotctld remains running, available for another TCP/IP network connection.
        """
        try:
            self.child.sendline("q")
        except Exception:
            pass
        self.child.close()

    def lonlat2loc(self, long, lat, loc_len):
        """
        Returns the Maidenhead 'Locator' for the given 'Longitude' and 'Latitude'.
        Floating point values are supplied. The precision of the returned square is controlled by 'Loc Len' which should be an even numbered integer value between 2 and 12.
        For example:
        L -170.0 -85.0 12
        returns:
        Locator: AA55AA00AA00
        """
        try:
            return self.send(f"L {long} {lat} {loc_len}")
        except Exception:
            return False
        
    def loc2lonlat(self, locator):
        """
        Returns 'Longitude' and 'Latitude' in decimal degrees at the approximate center of the requested Maidenhead grid square.
        'Locator' can be from 2 to 12 characters in length.
        West longitude is expressed as a negative value.
        South latitude is expressed as a negative value.
        For example:
        l AA55AA00AA00
        returns:
        Longitude: -169.999983 Latitude: -84.999991
        """
        try:
            return self.send(f"l {locator}")
        except Exception:
            return False
        
    def dms2dec(self, deg, min, sec, S_W):
        """
        Returns 'Dec Degrees', a signed floating point value.
        'Degrees' and 'Minutes' are integer values.
        'Seconds' is a floating point value.
        'S/W' is a flag with '1' indicating South latitude or West longitude and '0' North or East (the flag is needed as computers don't recognize a signed zero even though only
          the 'Degrees' value is typically signed in DMS notation).
        """
        try:
            return self.send(f"D {deg} {min} {sec} {S_W}")
        except Exception:
            return False
        
    def dec2dms(self, dec_deg):
        """
        Returns 'Degrees' 'Minutes' 'Seconds' 'S/W'.
        Values are as in dms2dec above.
        """
        try:
            return self.send(f"d {dec_deg}")
        except Exception:
            return False
        
    def dmmm2dec(self, deg, dec_min, S_W):
        """
        Returns 'Dec Degrees', a signed floating point value.
        'Degrees' is an integer value.
        'Dec Minutes' is a floating point value.
        'S/W' is a flag as in dms2dec above.
        """
        try:
            return self.send(f"E {deg} {dec_min} {S_W}")
        except Exception:
            return False
        
    def dec2dmmm(self, dec_deg):
        """
        Returns 'Degrees' 'Minutes' 'S/W'.
        Values are as in dmmm2dec above.
        """
        try:
            return self.send(f"e {dec_deg}")
        except Exception:
            return False
        
    def qrb(self, lon1, lat1, lon2, lat2):
        """
        Returns 'Distance' and 'Azimuth'.
        'Distance' is in km.
        'Azimuth' is in degrees.
        """
        try:
            return self.send(f"B {lon1} {lat1} {lon2} {lat2}")
        except Exception:
            return False
        
    def a_sp2a_lp(self, short_path_deg):
        """
        Returns 'Long Path Deg'.
        Both the supplied argument and returned value are floating point values within the range of 0.00 to 360.00.
        Note: Supplying a negative value will return an error message.
        """
        try:
            return self.send(f"A {short_path_deg}")
        except Exception:
            return False
        
    def d_sp2d_lp(self, short_path_km):
        """
        Returns 'Long Path km'.
        Both the supplied argument and returned value are floating point values.
        """
        try:
            return self.send(f"A {short_path_km}")
        except Exception:
            return False
        
    def pause(self, sec):
        """
        Pause for the given whole (integer) number of 'Seconds' before sending the next command to the rotator.
        """
        try:
            return self.send(f"pause {sec}")
        except Exception:
            return False


class tools:
    
    @staticmethod
    def parse_pos(res):
        data = res.split("\r\n")
        az = data[0].split(" ")[-1]
        el = data[1].split(" ")[-1]

        return float(az), float(el)