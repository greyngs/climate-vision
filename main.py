import datetime
import streamlit as st
import folium
from streamlit_folium import st_folium
from modules.data_provider import get_image
from modules.google_earth_engine import initialize_gee
from modules.watershed_method import watershed

# Page configuration
st.set_page_config(
    page_title="Climate Vision with Watershed",
    page_icon="❄️",
    layout="wide"
)

# CSS for centered text
st.markdown(
    """
    <style>
    .center-text {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Centered title and description
st.markdown("<h1 class='center-text'>Climate Change Analysis: Snow/Ice Segmentation</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text'>This application uses the watershed algorithm to segment snow and ice in satellite imagery from the Sentinel-2 collection (2015-present).</p>", unsafe_allow_html=True)
st.markdown("<p class='center-text'><a href='https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2' target='_blank'>Learn more about Sentinel-2</a></p>", unsafe_allow_html=True)

# Centered subtitle
st.markdown("<h3 class='center-text'>Select a location on the map</h3>", unsafe_allow_html=True)

# Default values
default_lat = 4.8808  # Vatnajökull Glacier, Iceland
default_lon = -75.3164
default_init_date = datetime.date(2024, 1, 15)
default_end_date = datetime.date(2025, 1, 15)

# Initialize data
map_lat = 0
map_lon = 0

init_date = datetime.date(2001, 7, 6)
end_date = datetime.date.today

# Create interactive map with Folium
m = folium.Map(location=[default_lat, default_lon], zoom_start=14)
folium.Marker([default_lat, default_lon], tooltip="Map center").add_to(m)

# Center map using Streamlit columns
col1, col2, col3 = st.columns([1, 3, 1])

with col2:  # Map in center column
    map_data = st_folium(m, width=1000, height=500)

# Get map center coordinates
if map_data is not None and 'center' in map_data:
    map_lat = map_data['center']['lat']
    map_lon = map_data['center']['lng']
    zoom = map_data['zoom']
else:
    map_lat, map_lon = default_lat, default_lon
    zoom = 6
with col2:
    st.write("Latitude:", map_lat, "Longitude:", map_lon)

# Initialize GEE
if initialize_gee():
    st.success("Google Earth Engine initialized successfully")
else:
    st.error("Failed to initialize Google Earth Engine")

# Date selection using Streamlit columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    init_date = st.date_input("From:", default_init_date)
    end_date = st.date_input("To:", default_end_date)

if col2.button("Compare", icon="🧊", use_container_width=True):
    image_init = get_image(map_lat, map_lon, init_date, zoom)
    image_end = get_image(map_lat, map_lon, end_date, zoom)

    if image_init.any() and image_end.any():
        image_init_watershed = watershed(image_init)
        image_end_watershed = watershed(image_end)

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        col2.write(init_date)
        col2.image(image_init, caption="Satellite RGB", width=400)
        col2.image(image_init_watershed, caption="Watershed", width=400)

        col3.write(end_date)
        col3.image(image_end, caption="Satellite RGB", width=400)
        col3.image(image_end_watershed, caption="Watershed", width=400)
