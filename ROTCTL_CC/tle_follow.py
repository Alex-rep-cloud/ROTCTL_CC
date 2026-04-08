"""
Satellite tracking script using TLE orbit parameters.
Moves the antenna to follow the satellite using rotctl.
Updates position every 5 seconds.
"""

import time
from datetime import datetime, timezone
from skyfield.api import Topos, load, EarthSatellite
from rotctl import ROTCTL

OBSERVER_LAT = 48.68333
OBSERVER_LON = 2.13333
OBSERVER_ELEV = 0

line1 = '1 59051U 24039A   26042.48263889  .00000030  00000-0  61435-5 0  9997'
line2 = '2 59051  98.7124  21.4852 0006214 305.1245  54.9182 14.22370125 10126'

def tle_track(rot, TLE_LINE_1, TLE_LINE_2):
    satellite = EarthSatellite(TLE_LINE_1, TLE_LINE_2, name="Satellite")

    observer = Topos(latitude_degrees=OBSERVER_LAT,
                     longitude_degrees=OBSERVER_LON,
                     elevation_m=OBSERVER_ELEV)

    try:
        while True:
            ts = load.timescale()
            t = ts.now()

            difference = satellite - observer
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()

            azimuth = az.degrees
            elevation = alt.degrees

            print(f"Azimuth: {azimuth:.1f}, Elevation: {elevation:.1f}")

            rot.set_pos(azimuth, elevation)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping tracking...")
        rot.stop()
        rot.exit()

if __name__ == "__main__":
    tle_track(ROTCTL(), line1, line2)
