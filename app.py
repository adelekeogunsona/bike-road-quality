"""
ride quality dashboard
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from src.load_data import load_all
from src.analysis import compute_bumpiness, compute_lean, compute_braking, find_rough_segments

st.set_page_config(page_title="Ride Quality", layout="wide")


@st.cache_data
def get_data():
    data = load_all()
    pos = data['position']
    acc = data['acceleration']
    orient = data['orientation']

    bumpiness = compute_bumpiness(pos, acc)
    lean = compute_lean(pos, orient)
    braking = compute_braking(pos)
    speed_kmh = pos['speed'].values * 3.6

    timestamps = pos['timestamp'].values
    time_min = np.array(
        [(t - timestamps[0]) / np.timedelta64(1, 's') for t in timestamps]
    ) / 60

    return pos, bumpiness, lean, braking, speed_kmh, time_min


pos, bumpiness, lean, braking, speed_kmh, time_min = get_data()

tab1, tab2, tab3 = st.tabs(["Route Map", "Timeline", "Speed vs Bumpiness"])


def val_to_hex(val, vmin, vmax):
    """map a value to a green-yellow-red hex color."""
    cmap = plt.cm.RdYlGn_r
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    rgba = cmap(norm(val))
    return mcolors.to_hex(rgba)


with tab1:
    st.header("Route Bumpiness Map")
    st.markdown("Green = smooth, red = rough. Based on accelerometer vibration intensity.")

    moving = speed_kmh > 2
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ride Duration", f"{time_min[-1]:.0f} min")
    c2.metric("Avg Bumpiness", f"{np.mean(bumpiness[moving]):.2f} m/s²")
    c3.metric("Max Bumpiness", f"{np.max(bumpiness):.2f} m/s²")
    c4.metric("Avg Speed", f"{np.mean(speed_kmh[moving]):.0f} km/h")

    overlay = st.radio("Color by:", ["Bumpiness", "Lean angle", "Speed"],
                       horizontal=True)

    if overlay == "Bumpiness":
        values = bumpiness
        label = "bumpiness"
    elif overlay == "Lean angle":
        values = lean
        label = "lean"
    else:
        values = speed_kmh
        label = "speed"

    vmin = np.percentile(values[values > 0], 5) if np.any(values > 0) else 0
    vmax = np.percentile(values[values > 0], 95) if np.any(values > 0) else 1

    center = [pos['latitude'].mean(), pos['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=14, tiles='CartoDB positron')

    lats = pos['latitude'].values
    lons = pos['longitude'].values

    for i in range(1, len(lats)):
        color = val_to_hex(values[i], vmin, vmax)
        folium.PolyLine(
            [(lats[i - 1], lons[i - 1]), (lats[i], lons[i])],
            color=color, weight=4, opacity=0.8
        ).add_to(m)

    folium.CircleMarker([lats[0], lons[0]], radius=6, color='black',
                        fill=True, tooltip='Start').add_to(m)

    st_folium(m, width=None, height=500)


with tab2:
    st.header("Ride Timeline")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_min, y=speed_kmh, mode='lines',
                             line=dict(color='#3b82f6', width=1),
                             fill='tozeroy', fillcolor='rgba(59,130,246,0.06)',
                             name='Speed (km/h)'))
    fig.update_layout(height=220, margin=dict(t=30, b=20),
                      title='Speed', yaxis_title='km/h')
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=time_min, y=bumpiness, mode='lines',
                              line=dict(color='#ef4444', width=1),
                              fill='tozeroy', fillcolor='rgba(239,68,68,0.06)',
                              name='Bumpiness'))
    fig2.update_layout(height=220, margin=dict(t=30, b=20),
                       title='Bumpiness', yaxis_title='m/s²')
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=time_min, y=lean, mode='lines',
                              line=dict(color='#8b5cf6', width=1),
                              fill='tozeroy', fillcolor='rgba(139,92,246,0.06)',
                              name='Lean'))
    fig3.update_layout(height=220, margin=dict(t=30, b=20),
                       title='Lean Angle', yaxis_title='degrees',
                       xaxis_title='Time (min)')
    st.plotly_chart(fig3, use_container_width=True)


with tab3:
    st.header("Does Faster = Bumpier?")
    st.markdown("Each dot is one second of the ride. Filtered to moving only (>2 km/h).")

    mask = speed_kmh > 2
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=speed_kmh[mask], y=bumpiness[mask], mode='markers',
        marker=dict(size=5, color=bumpiness[mask],
                    colorscale='RdYlGn_r', opacity=0.5,
                    colorbar=dict(title='Bumpiness')),
        name='',
    ))
    fig.update_layout(xaxis_title='Speed (km/h)',
                      yaxis_title='Bumpiness (m/s²)',
                      height=450, margin=dict(t=30, b=40))
    st.plotly_chart(fig, use_container_width=True)

    corr = np.corrcoef(speed_kmh[mask], bumpiness[mask])[0, 1]
    st.markdown(f"Correlation: **{corr:.2f}** — "
                + ("yeah, faster riding is bumpier." if corr > 0.2
                   else "not really, speed and bumpiness are mostly independent."
                   if abs(corr) < 0.2
                   else "interesting, bumpier roads are actually slower."))
