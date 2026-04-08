from rotctl import *
import time
import matplotlib.pyplot as plt

def parse_pos(res):
    data = res.split("\r\n")
    az = data[0].split(" ")[-1]
    el = data[1].split(" ")[-1]

    return float(az), float(el)

CMD = [ROTCTL.UP, ROTCTL.UP, ROTCTL.UP, ROTCTL.LEFT, ROTCTL.RIGHT, ROTCTL.DOWN, ROTCTL.DOWN, ROTCTL.RIGHT, ROTCTL.LEFT, ROTCTL.UP, ROTCTL.UP]

if __name__ == "__main__":
    T, AZ, EL = [], [], []
    rot = ROTCTL(model=1)

    start = time.perf_counter()
    for _ in CMD:
        rot.move(_, 1)
        if _ == ROTCTL.LEFT:
            rot.stop()
        az, el = parse_pos(rot.get_pos())
        AZ.append(az); EL.append(el)
        T.append(time.perf_counter() - start)
    rot.exit()

    plt.plot(T, AZ)
    plt.plot(T, EL)
    plt.show()