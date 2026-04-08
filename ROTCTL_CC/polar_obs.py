import matplotlib.pyplot as plt
import numpy as np

def load_obstacles(path="obstacles.txt"):
    AZ, EL = [], []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            parts = s.split(";")
            if len(parts) < 2:
                continue
            AZ.append(float(parts[0]))
            EL.append(float(parts[1]))
    return np.array(AZ), np.array(EL)


def main():
    AZ, EL = load_obstacles("obstacles.txt")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='polar')

    # Map elevation so 90° (zenith) is at the center: r = 90 - EL
    r = 90.0 - EL
    theta = np.deg2rad(AZ)

    ax.scatter(theta, r, c='C1', s=36, alpha=0.85)

    # Configure polar plot: 0° at top, clockwise
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # Radial limits: r=0 at center (90° elevation), r=90 at outer (0° elevation)
    ax.set_ylim(0, 90)
    ax.set_yticks([0, 30, 60, 90])
    ax.set_yticklabels(['90°', '60°', '30°', '0°'])
    ax.set_rlabel_position(135)

    ax.set_title('Obstacles', va='bottom')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()