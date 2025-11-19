import requests
from datetime import datetime, timezone

class SatelliteTracker:
    id = "54234"
    url = f"https://www.n2yo.com/sat/instant-tracking.php?s={id}&hlat=48.68333&hlng=2.13333&d=300&r=789964367127.4452&tz=GMT+01:00&O=n2yocom&rnd_str=38461526dff975b9cebfdc6ac2abb3d6&callback="
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    @staticmethod
    def fetch_positions(target_time):
        r = requests.get(SatelliteTracker.url, headers=SatelliteTracker.headers)
        data = r.json()

        if isinstance(data, list) and len(data) > 0:
            positions = data[0]["pos"]
            closest = None
            min_diff = float("inf")

            for pos in positions:
                fields = pos["d"].split("|")
                if len(fields) >= 10:
                    timestamp = int(fields[9])
                    diff = abs(timestamp - target_time)
                    if diff < min_diff:
                        min_diff = diff
                        closest = fields

            if closest:
                latitude = closest[0]
                longitude = closest[1]
                altitude = closest[2]
                azimuth = closest[3]
                elevation = closest[4]
                timestamp = closest[9]
                readable_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

                return {
                    "time": readable_time,
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude_km": altitude,
                    "azimuth": azimuth,
                    "elevation": elevation
                }
        return None
    
    @staticmethod
    def getPos():
        return SatelliteTracker.fetch_positions(int(datetime.now(timezone.utc).timestamp()))
    
print(SatelliteTracker.getPos())