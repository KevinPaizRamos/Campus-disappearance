import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from analysis import primary_matches, cams, metro_swipes

st.title("Campus Disappearance Investigation")

st.subheader("Primary Suspects: Jordan, Maria, and Sam")

# Merge primary_matches with metro_swipes to include card names
primary_matches = primary_matches.merge(
    metro_swipes[['card_id', 'timestamp']].drop_duplicates(subset='card_id'),
    left_on='device_id',
    right_on='card_id',
    how='left'
)

# Display the suspects table
st.dataframe(primary_matches[['name', 'device_id', 'card_id', 'timestamp_x', 'lat', 'lon', 'priority']])

st.subheader("Map View")
map = folium.Map(location=[40.730610, -73.935242], zoom_start=15)

# Add Alex's last known position
alex_location = [40.730610, -73.935242]
folium.Marker(
    alex_location,
    popup="<b>Alex's Last Known Position</b>",
    icon=folium.Icon(color='Yellow', icon='info-sign')
).add_to(map)

# Plot pings for primary suspects (filter out rows with NaN lat/lon)
valid_primary_matches = primary_matches.dropna(subset=['lat', 'lon'])
for _, row in valid_primary_matches.iterrows():
    color = 'blue' if row['device_id'] == 'device_jordan' else 'green'
    folium.Marker(
        [row['lat'], row['lon']],
        popup=(
            f"<b>Name:</b> {row['name']}<br>"
            f"<b>Device:</b> {row['device_id']}<br>"
            f"<b>Card:</b> {row['card_id']}<br>"
            f"<b>Time:</b> {row['timestamp_x']}"
        ),
        icon=folium.Icon(color=color)
    ).add_to(map)

# Plot all suspect positions (replace cameras with suspect positions)
for _, row in valid_primary_matches.iterrows():
    folium.Marker(
        [row['lat'], row['lon']],
        popup=(
            f"<b>Name:</b> {row['name']}<br>"
            f"<b>Device:</b> {row['device_id']}<br>"
            f"<b>Card:</b> {row['card_id']}<br>"
            f"<b>Time:</b> {row['timestamp_x']}"
        ),
        icon=folium.Icon(color='green')
    ).add_to(map)

# Render the map
folium_static(map)