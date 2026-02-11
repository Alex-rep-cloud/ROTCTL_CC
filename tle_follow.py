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

TLE_LINE_1 = "1 25544U 98067A   24001.00000000  .00000000  00000-0  00000-0 0  9999"
TLE_LINE_2 = "2 25544  51.6400  10.0000 0002000   0.0000  0.0000 15.50000000    01"

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
    tle_track(ROTCTL(), TLE_LINE_1, TLE_LINE_2)
