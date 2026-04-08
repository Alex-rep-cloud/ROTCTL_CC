import socket

class rotctld:
    """
    A smooth-tracking wrapper for Hamlib's rotctld.
    Includes a deadband to prevent mechanical wear.
    """
    
    def __init__(self, host='127.0.0.1', port=4533, threshold=1.0):
        self.address = (host, port)
        self.threshold = threshold
        
        # Internal state to remember the last commanded position
        self.last_sent_az = -999.0
        self.last_sent_el = -999.0

    def _send(self, command):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(self.address)
                s.sendall(f"{command}\n".encode())
                return s.recv(1024).decode().strip()
        except Exception as e:
            return f"ERR: {e}"

    def move(self, az, el, force=False):
        """
        Moves the rotor only if the change exceeds the threshold.
        Set force=True to bypass the smoothing logic (e.g., for parking).
        """
        # Calculate the absolute difference from the last update
        az_delta = abs(az - self.last_sent_az)
        el_delta = abs(el - self.last_sent_el)

        if force or az_delta >= self.threshold or el_delta >= self.threshold:
            response = self._send(f"P {az:.2f} {el:.2f}")
            
            if "RPRT 0" in response:
                self.last_sent_az = az
                self.last_sent_el = el
                return f"OK: Moved to {az}, {el}"
            return f"FAIL: {response}"
        
        return "SKIP: Change below threshold"

    def get_position(self):
        """Queries the hardware for real-time position."""
        resp = self._send("p")
        try:
            parts = resp.split()
            return float(parts[0]), float(parts[1])
        except:
            return None

    def stop(self):
        """Emergency stop."""
        return self._send("S")