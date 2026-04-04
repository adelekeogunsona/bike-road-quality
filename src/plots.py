"""
visualizations for ride quality analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import LineCollection


def bumpiness_colormap():
    """green (smooth) -> yellow -> red (rough)"""
    return plt.cm.RdYlGn_r


def make_colored_route(ax, lons, lats, values, cmap, vmin=None, vmax=None, lw=2.5):
    """draw a route as colored line segments."""
    points = np.array([lons, lats]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    if vmin is None:
        vmin = np.percentile(values, 5)
    if vmax is None:
        vmax = np.percentile(values, 95)

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(values[:-1])
    lc.set_linewidth(lw)
    ax.add_collection(lc)
    ax.autoscale()
    return lc


def plot_route_bumpiness(pos, bumpiness, save_path):
    fig, ax = plt.subplots(figsize=(9, 9))

    lc = make_colored_route(
        ax, pos['longitude'].values, pos['latitude'].values,
        bumpiness, bumpiness_colormap()
    )
    cbar = plt.colorbar(lc, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('Bumpiness (m/s²)', fontsize=10)

    ax.plot(pos['longitude'].iloc[0], pos['latitude'].iloc[0],
            'ko', ms=8, zorder=5, label='Start/End')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Road Bumpiness Along the Route')
    ax.set_aspect('equal')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_ride_timeline(time_min, speed_kmh, bumpiness, lean, save_path):
    fig, axes = plt.subplots(3, 1, figsize=(13, 7), sharex=True)

    axes[0].plot(time_min, speed_kmh, '-', color='#3b82f6', lw=0.8)
    axes[0].set_ylabel('Speed (km/h)')
    axes[0].set_title('Ride Timeline')
    axes[0].fill_between(time_min, speed_kmh, alpha=0.08, color='#3b82f6')

    axes[1].plot(time_min, bumpiness, '-', color='#ef4444', lw=0.8)
    axes[1].set_ylabel('Bumpiness (m/s²)')
    axes[1].fill_between(time_min, bumpiness, alpha=0.08, color='#ef4444')

    axes[2].plot(time_min, lean, '-', color='#8b5cf6', lw=0.8)
    axes[2].set_ylabel('Lean angle (deg)')
    axes[2].set_xlabel('Time (min)')
    axes[2].fill_between(time_min, lean, alpha=0.08, color='#8b5cf6')

    for ax in axes:
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_speed_vs_bumpiness(speed_kmh, bumpiness, save_path):
    # filter out stationary points
    mask = speed_kmh > 2

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(speed_kmh[mask], bumpiness[mask], s=8, alpha=0.4,
               c=bumpiness[mask], cmap=bumpiness_colormap(), edgecolors='none')
    ax.set_xlabel('Speed (km/h)')
    ax.set_ylabel('Bumpiness (m/s²)')
    ax.set_title('Faster = Bumpier?')
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
