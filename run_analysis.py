"""
run ride quality analysis and generate plots.
"""

import numpy as np
from src.load_data import load_all
from src.analysis import compute_bumpiness, compute_lean, compute_braking, find_rough_segments
from src.plots import plot_route_bumpiness, plot_ride_timeline, plot_speed_vs_bumpiness


def main():
    data = load_all()
    pos = data['position']
    acc = data['acceleration']
    orient = data['orientation']

    timestamps = pos['timestamp'].values
    duration = (timestamps[-1] - timestamps[0]) / np.timedelta64(1, 's')
    time_min = np.array([(t - timestamps[0]) / np.timedelta64(1, 's') for t in timestamps]) / 60

    speed_kmh = pos['speed'].values * 3.6

    print(f"loaded {len(pos)} GPS points, {len(acc)} accel readings")
    print(f"ride: {duration / 60:.1f} min\n")

    print("computing bumpiness...")
    bumpiness = compute_bumpiness(pos, acc)

    print("computing lean angles...")
    lean = compute_lean(pos, orient)

    print("computing braking...")
    braking = compute_braking(pos)

    # rough segment detection
    segments, threshold = find_rough_segments(bumpiness)

    print("\ngenerating plots...")
    plot_route_bumpiness(pos, bumpiness, 'outputs/route_bumpiness.png')
    print("  route_bumpiness.png")

    plot_ride_timeline(time_min, speed_kmh, bumpiness, lean, 'outputs/ride_timeline.png')
    print("  ride_timeline.png")

    plot_speed_vs_bumpiness(speed_kmh, bumpiness, 'outputs/speed_vs_bumpiness.png')
    print("  speed_vs_bumpiness.png")

    # summary
    moving = speed_kmh > 2
    print(f"\n--- summary ---")
    print(f"duration: {duration / 60:.1f} min")
    print(f"avg speed (moving): {np.mean(speed_kmh[moving]):.1f} km/h")
    print(f"max speed: {np.max(speed_kmh):.1f} km/h")
    print(f"\nbumpiness (while moving):")
    print(f"  mean: {np.mean(bumpiness[moving]):.2f} m/s²")
    print(f"  max:  {np.max(bumpiness):.2f} m/s²")
    print(f"  rough threshold (p85): {threshold:.2f} m/s²")
    print(f"  rough segments found: {len(segments)}")

    if segments:
        print(f"\nroughest stretches:")
        ranked = sorted(segments, key=lambda s: np.mean(bumpiness[s[0]:s[1]]), reverse=True)
        for i, (s, e) in enumerate(ranked[:5]):
            t_start = time_min[s]
            t_end = time_min[min(e, len(time_min) - 1)]
            avg_bump = np.mean(bumpiness[s:e])
            print(f"  #{i+1}: {t_start:.1f}-{t_end:.1f} min "
                  f"(avg bumpiness {avg_bump:.2f} m/s², {e-s} sec)")

    print(f"\nlean angle:")
    print(f"  mean: {np.mean(lean[moving]):.1f}°")
    print(f"  max:  {np.max(lean):.1f}°")

    hard_brakes = np.sum(braking < -1.0)
    print(f"\nbraking events (>1 m/s² decel): {hard_brakes}")

    print("\nplots saved to outputs/")


if __name__ == '__main__':
    main()
