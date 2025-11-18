""" Alexandre Hachet

Classe qui prend en argument une suite de positions (azimuth, élévation) en fonction du temps
pour que l'antenne suive un objet (typiquement satellite)
"""
from rotctl import *

class Follow:

    def __init__(self, pos, rot):
        self.pos = pos
        self.rot = rot

    @staticmethod
    def _posfromtxt(file):
        T, AZ, EL = [], [], []
        with open(file, "r") as f:
            for line in f.readlines():
                data = line.split("\t")
                T.append(data[0]); AZ.append(float(data[1])); EL.append(float(data[2]))
        return T, AZ, EL

    def _follow(self):
        AZ, EL = [], []
        for i in range(len(self.pos[0])):
            self.rot.set_pos(self.pos[1][i], self.pos[2][i])
            az, el = tools.parse_pos(self.rot.get_pos())
            AZ.append(az); EL.append(el)
        return AZ, EL
    
    """
    Still need to implement time tracking to follow in real time
    """


    