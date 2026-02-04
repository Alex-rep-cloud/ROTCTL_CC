from follow import *
from rotctl import *
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

rot = ROTCTL()
fol = Follow(rot)

AZ, EL = [], []
TARGET_EL, TARGET_AZ = [], []

fol._follow()
print("Sarting to follow satellite...")
for i in tqdm(range(3), desc="Processing", unit="step"):
    pos = tools.parse_pos(rot.get_pos())
    AZ.append(pos[0])
    EL.append(pos[1])

    target = SatelliteTracker.getPos()
    TARGET_AZ.append(float(target["azimuth"])); TARGET_EL.append(float(target["elevation"]))
    time.sleep(1)
fol._unflollow()
print("Stopped following satellite.")

ax = plt.subplot(1, 1, 1, projection='polar')
ax.plot(np.deg2rad(AZ), 90-np.array(EL), "-", label="Antenna")
ax.plot(np.deg2rad(TARGET_AZ), 90-np.array(TARGET_EL), "x", label="Target")
#plt.plot(np.deg2rad(AZ), 90-np.array(EL), label="Antenna Response")


"""pos = tools.parse_pos(rot.get_pos())

ax = plt.subplot(1, 1, 1, projection='polar')
ax.plot(np.deg2rad(pos[1]), 90-np.array(pos[2]), "x", label="Antenna")
#ax.plot(np.deg2rad(AZ), 90-np.array(EL), label="Response")

ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

ax.legend()"""

plt.show()
