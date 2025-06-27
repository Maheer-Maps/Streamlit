import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from shapely.geometry import Point

st.set_page_config(page_title="Liverpool Sensor Map", layout="wide")

st.title("Liverpool Air Pollution Database")

st.subheader("Project Scope")
st.text("This project was conducted as part of the Python for Data Storytelling workshop hosted by the UCL Social Data Institute. The data was sourced from the Geographic Data Service, part of Smart Data Research UK and based at UCL, the University of Liverpool, the University of Oxford and the University of Edinburgh.")


st.subheader("PM25 in Liverpool")

# Load sensor data
sensors_df = pd.read_csv("sensors.csv")

# Swap lat/lon if needed
sensors_df[["lon", "lat"]] = sensors_df[["lat", "lon"]]

# Ensure longitude and latitude are numeric
sensors_df["lon"] = pd.to_numeric(sensors_df["lon"], errors="coerce")
sensors_df["lat"] = pd.to_numeric(sensors_df["lat"], errors="coerce")

# Drop rows with invalid coordinates
sensors_df.dropna(subset=["lon", "lat"], inplace=True)

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(sensors_df["lon"], sensors_df["lat"])]
gdf_sensors = gpd.GeoDataFrame(sensors_df, geometry=geometry, crs="EPSG:4326")

# Plot using Plotly – fixed to show PM2.5
fig = px.scatter_mapbox(
    gdf_sensors,
    lat=gdf_sensors.geometry.y,
    lon=gdf_sensors.geometry.x,
    color="pm25",  # <- show PM2.5 values
    color_continuous_scale="tropic",
    size_max=15,
    zoom=11,
    height=600,
    mapbox_style="carto-darkmatter"
)

# Display map
st.plotly_chart(fig, use_container_width=True)

st.subheader("PM10 in Liverpool")


# Plot using Plotly – fixed to show PM2.5
fig = px.scatter_mapbox(
    gdf_sensors,
    lat=gdf_sensors.geometry.y,
    lon=gdf_sensors.geometry.x,
    color="pm10",  # <- show PM2.5 values
    color_continuous_scale="tropic",
    size_max=15,
    zoom=11,
    height=600,
    mapbox_style="carto-darkmatter"
)

# Display map
st.plotly_chart(fig, use_container_width=True)

# Expandable info
with st.expander("ℹ️ About this map"):
    st.write("""
        - Sensors represent real-time or recorded environmental data.
        - Hover over a point to see its values.
        - Toggle ward boundaries on or off via the sidebar.
    """)

# Sensor data table
st.subheader("📊 Sensor Data Preview")
st.dataframe(sensors_df.head(20))

# Download option
st.download_button("📥 Download Sensor Data", sensors_df.to_csv(index=False), file_name="sensors_export.csv", mime="text/csv")
