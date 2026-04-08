from rotctld import *
from skyfield.api import Topos, load, EarthSatellite
import time

# Setup
rotor = rotctld(threshold=1.5) # 1.5 degree deadband
ts = load.timescale()
line1 = '1 59051U 24039A   26042.48263889  .00000030  00000-0  61435-5 0  9997'
line2 = '2 59051  98.7124  21.4852 0006214 305.1245  54.9182 14.22370125 10126'
sat = EarthSatellite(line1, line2, 'SAT', ts)
qth = Topos(latitude_degrees=48.8, longitude_degrees=2.3)

try:
    while True:
        # 1. Get current sat position
        geocentric = sat.at(ts.now())
        alt, az, dist = (geocentric - qth).altaz()
        
        # 2. Try to move (The library handles the smoothing internally)
        if alt.degrees > 0:
            status = rotor.move(az.degrees, alt.degrees)
            print(status)
        else:
            print(f"Sat below horizon: {alt.degrees:.1f}°")
            
        time.sleep(2)

except KeyboardInterrupt:
    rotor.stop()
    print("Stopped.")