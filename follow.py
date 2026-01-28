""" Alexandre Hachet

Classe qui prend en argument une suite de positions (azimuth, élévation) en fonction du temps
pour que l'antenne suive un objet (typiquement satellite)

Ou bien qui suive en temps réel un satellite en interrogeant l'API NOAA
"""
from rotctl import *
import threading
from get_noaa import *

class Follow:

    def __init__(self, rot, pos=[]):
        self.pos = pos
        self.rot = rot
        self.running = True

    @staticmethod
    def _posfromtxt(file):
        T, AZ, EL = [], [], []
        with open(file, "r") as f:
            for line in f.readlines():
                data = line.split("\t")
                T.append(data[0]); AZ.append(float(data[1])); EL.append(float(data[2]))
        return T, AZ, EL

    def _follow_path(self):
        AZ, EL = [], []
        for i in range(len(self.pos[0])):
            self.rot.set_pos(self.pos[1][i], self.pos[2][i])
            az, el = tools.parse_pos(self.rot.get_pos())
            AZ.append(az); EL.append(el)
        return AZ, EL
    
    def _follow_routine(self, *args):
        while self.running:
            target = SatelliteTracker.getPos()
            self.rot.set_pos(float(target["azimuth"]), float(target["elevation"]))
            while (tools.dist4tuple((float(target["azimuth"]), float(target["elevation"])), tools.parse_pos(self.rot.get_pos())) < ROTCTL.EPS) & self.running:
                time.sleep(0.5)
    
    def _follow(self):
        threading.Thread(target=self._follow_routine, args=[self]).start()

    def _unflollow(self):
        self.running = False


    
