from rotctl import *
import time

rotor = ROTCTL()

print(rotor.get_pos())
rotor.move(ROTCTL.UP, 100)
time.sleep(10)
print(rotor.get_pos())

