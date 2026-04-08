
# server.py
import os
import socket
import time
import threading
from typing import Optional, Dict
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

# --- Configuration ---
# If you use rotctld (recommended), set USE_ROTCTLD=True and ensure rotctld is running:
#   rotctld -m <model> -r /dev/ttyUSB0 -s 9600 -T 4533
USE_ROTCTLD = True
USE_PYROTCTL = os.getenv("USE_PYROTCTL", "False").lower() == "true"

ROTCTLD_HOST = os.getenv("ROTCTLD_HOST", "127.0.0.1")
ROTCTLD_PORT = int(os.getenv("ROTCTLD_PORT", "4533"))
STATUS_INTERVAL_SEC = float(os.getenv("STATUS_INTERVAL_SEC", "1.0"))

# If you prefer Python Hamlib bindings, set USE_ROTCTLD=False
# and adjust serial settings below.
SERIAL_DEVICE = os.getenv("SERIAL_DEVICE", "/dev/ttyUSB0")
SERIAL_SPEED = os.getenv("SERIAL_SPEED", "9600")
ROT_MODEL = int(os.getenv("ROT_MODEL", "202"))  # Example Yaesu GS-232A=202

# --- Data models ---
class RotateCmd(BaseModel):
    az: float
    el: float
    # Optional: speed/slew rate could be added here later

# --- Rotor adapters ---
class RotctldClient:
    """Simple client for Hamlib rotctld over TCP (multi-connection safe)."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def _send(self, cmd: str, expect_lines: int = 0, timeout: float = 2.0) -> str:
        """Open a new socket per command; return raw response (may be multi-line)."""
        with socket.create_connection((self.host, self.port), timeout=timeout) as s:
            s.settimeout(timeout)
            s.sendall((cmd.rstrip("\n") + "\n").encode("ascii"))
            chunks = []
            # read until timeout/close; rotctld typically closes after response
            try:
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    chunks.append(data.decode("ascii", errors="ignore"))
                    # quick stop if we got enough lines (optimization)
                    if expect_lines and "".join(chunks).count("\n") >= expect_lines:
                        break
            except socket.timeout:
                pass
            return "".join(chunks)

    def get_position(self) -> Dict[str, float]:
        # 'p' returns:
        #   Azimuth: 123.000000
        #   Elevation: 45.000000
        raw = self._send("p", expect_lines=2)
        az, el = None, None
        for line in raw.splitlines():
            line = line.strip()
            if line.lower().startswith("azimuth:"):
                try:
                    az = float(line.split(":")[1])
                except Exception:
                    pass
            elif line.lower().startswith("elevation:"):
                try:
                    el = float(line.split(":")[1])
                except Exception:
                    pass
        if az is None or el is None:
            raise RuntimeError(f"Failed to parse position from rotctld: {raw!r}")
        return {"az": az, "el": el}

    def set_position(self, az: float, el: float) -> None:
        # 'P <az> <el>' sets the position; rotctld returns "RPRT 0" on success
        raw = self._send(f"P {az:.3f} {el:.3f}", expect_lines=1)
        if "RPRT 0" not in raw:
            raise RuntimeError(f"Set position failed: {raw!r}")


class HamlibBindingsClient:
    """Direct Python Hamlib bindings (single-process control)."""
    def __init__(self):
        try:
            import rotctl  # module is named 'Hamlib' in most distros
            self.Hamlib = rotctl
        except ImportError as e:
            raise RuntimeError("Hamlib Python bindings not installed") from e

        H = self.Hamlib
        H.rot_init()
        self.rot = H.Rot(ROT_MODEL)
        self.rot.set_conf("serial_speed", SERIAL_SPEED)
        self.rot.set_conf("serial_port", SERIAL_DEVICE)
        ret = self.rot.open()
        if ret != 0:
            raise RuntimeError(f"Hamlib rot.open() failed with code {ret}")

    def get_position(self) -> Dict[str, float]:
        az, el = self.rot.get_position()
        return {"az": float(az), "el": float(el)}

    def set_position(self, az: float, el: float) -> None:
        ret = self.rot.set_position(az, el)
        if ret != 0:
            raise RuntimeError(f"Hamlib set_position failed with code {ret}")


# Optional: use the local `rotctl.py` wrapper from the repository
class PyRotctlClient:
    def __init__(self, model: int = ROT_MODEL, device: str = SERIAL_DEVICE):
        # allow importing rotctl from parent directory (repo root)
        parent = os.path.dirname(os.path.dirname(__file__))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        try:
            import rotctl as rc
        except Exception as e:
            raise RuntimeError("Failed to import local rotctl module") from e
        # instantiate
        self._rc = rc.ROTCTL(model=model, device=device)

    def get_position(self) -> Dict[str, float]:
        raw = self._rc.get_pos()
        try:
            az, el = self._rc.tools.parse_pos(raw)
            return {"az": float(az), "el": float(el)}
        except Exception as e:
            raise RuntimeError(f"Failed to parse position from rotctl: {raw!r}") from e

    def set_position(self, az: float, el: float) -> None:
        ret = self._rc.set_pos(az, el)
        if ret is False:
            raise RuntimeError("rotctl set_pos failed")

# Select implementation
if USE_PYROTCTL:
    Rotor = PyRotctlClient(ROT_MODEL, SERIAL_DEVICE)
else:
    Rotor = RotctldClient(ROTCTLD_HOST, ROTCTLD_PORT) if USE_ROTCTLD else HamlibBindingsClient()

# --- FastAPI app ---
app = FastAPI(title="Rotor Control API")

# Serve the single-page UI from the `static` directory next to this file
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# Allow multi-computer access (adjust allowed origins as needed!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected WebSocket clients
clients_lock = threading.Lock()
clients = set()

def broadcast(payload: Dict):
    with clients_lock:
        for ws in list(clients):
            try:
                ws.send_json(payload)
            except Exception:
                # Drop broken sockets
                clients.discard(ws)

@app.get("/status")
def status() -> Dict[str, float]:
    """Return current rotor azimuth/elevation."""
    return Rotor.get_position()

@app.post("/rotate")
def rotate(cmd: RotateCmd):
    """Set rotor azimuth/elevation."""
    Rotor.set_position(cmd.az, cmd.el)
    # Return echo + new status
    return {"requested": {"az": cmd.az, "el": cmd.el}, "actual": Rotor.get_position()}

@app.post("/park")
def park(az: float = Body(0.0), el: float = Body(0.0)):
    """Park rotor at a predefined position (defaults 0°, 0°)."""
    Rotor.set_position(az, el)
    return {"parked_to": {"az": az, "el": el}}

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    with clients_lock:
        clients.add(websocket)
    try:
        # push initial state
        broadcast({"type": "status", **Rotor.get_position()})
        # periodic status push
        while True:
            time.sleep(STATUS_INTERVAL_SEC)
            broadcast({"type": "status", **Rotor.get_position()})
    except WebSocketDisconnect:
        pass
    except Exception:
        # best effort cleanup
        with clients_lock:
            clients.discard(websocket)
