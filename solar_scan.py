import math
import datetime

def get_precise_sun(lat, lon):
    """
    Calculates Sun position using standard physics formulas.
    Returns (azimuth, elevation) as floats.
    """
    now = datetime.datetime.utcnow()
    # Days since J2000.0
    diff = now - datetime.datetime(2000, 1, 1, 12, 0, 0)
    d = diff.total_seconds() / 86400.0

    # Solar Mean Elements
    g = math.radians(357.529 + 0.98560028 * d)
    q = 280.459 + 0.98564736 * d
    L = math.radians(q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    e = math.radians(23.439 - 0.00000036 * d)

    # Convert to Rectangular/Celestial
    ra = math.atan2(math.cos(e) * math.sin(L), math.cos(L))
    dec = math.asin(math.sin(e) * math.sin(L))

    # Sidereal Time for Local Longitude
    gmst = (18.697374558 + 24.06570982441908 * d) % 24
    lst = math.radians(gmst * 15 + lon)
    ha = lst - ra

    # Transform to Az/El
    lat_r = math.radians(lat)
    el = math.asin(math.sin(lat_r) * math.sin(dec) + 
                   math.cos(lat_r) * math.cos(dec) * math.cos(ha))
    az = math.atan2(-math.sin(ha), 
                    math.cos(lat_r) * math.tan(dec) - math.sin(lat_r) * math.cos(ha))
    
    return round(math.degrees(az) % 360, 4), round(math.degrees(el), 4)

def generate_float_scan(lat, lon, span=5.0, step=0.5):
    """
    Generates a high-precision 'Snake' scan pattern.
    :param span: Total degrees to cover (e.g. 5.0 degree square)
    :param step: Increment in float degrees (e.g. 0.5)
    """
    center_az, center_el = get_precise_sun(lat, lon)
    
    # Create the float range for offsets
    # We use a list comprehension to handle float stepping safely
    steps_count = int(span / step)
    offsets = [round(- (span/2) + (i * step), 4) for i in range(steps_count + 1)]

    scan_path = []
    for i, d_el in enumerate(offsets):
        # Reverse the azimuth direction every other row (Snake pattern)
        current_az_offsets = offsets[::-1] if i % 2 else offsets
        
        for d_az in current_az_offsets:
            # Re-calculate Sun center inside the loop if the scan is slow
            # but for simplicity, we apply the offset to the initial center
            target_az = (center_az + d_az) % 360
            target_el = center_el + d_el
            scan_path.append((target_az, target_el))
            
    return scan_path

# Example: 4x4 degree scan with 0.25 degree precision
path = generate_float_scan(48.68333, 2.13333, span=4.0, step=0.25)

print(f"{'Step':<5} | {'Azimuth':<10} | {'Elevation':<10}")
print("-" * 30)
for idx, (az, el) in enumerate(path): # Showing first 10
    print(f"{idx+1:<5} | {az:<10.4f} | {el:<10.4f}")
