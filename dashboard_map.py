import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from shapely.geometry import Point
import json

st.set_page_config(page_title="Liverpool Sensor Map", layout="wide")

st.title("🌍 Liverpool Environmental Sensor Dashboard")

# Load sensor data
sensors_df = pd.read_csv("sensors.csv")

# Fix swapped columns
sensors_df[["lon", "lat"]] = sensors_df[["lat", "lon"]]

# Ensure longitude and latitude are numeric
sensors_df["lon"] = pd.to_numeric(sensors_df["lon"], errors="coerce")
sensors_df["lat"] = pd.to_numeric(sensors_df["lat"], errors="coerce")

# Drop rows with invalid coordinates
sensors_df.dropna(subset=["lon", "lat"], inplace=True)

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(sensors_df["lon"], sensors_df["lat"])]
gdf_sensors = gpd.GeoDataFrame(sensors_df, geometry=geometry, crs="EPSG:4326")

# Load ward shapefile
wards_gdf = gpd.read_file("Wards/WardsPolygon.shp").to_crs("EPSG:4326")
wards_geojson = json.loads(wards_gdf.to_json())

# Set Mapbox style and colors
map_style = "carto-darkmatter"
color_schemes = {
    "pm1": "cyan",
    "pm25": "purple",
    "pm10": "aqua"
}

# Function to generate map
def plot_pollution_map(param, color):
    fig = px.scatter_mapbox(
        gdf_sensors,
        lat=gdf_sensors.geometry.y,
        lon=gdf_sensors.geometry.x,
        color=param,
        color_continuous_scale=[[0, color], [1, color]],
        size_max=15,
        zoom=11,
        height=600,
        hover_name="sensor_id",
        mapbox_style=map_style
    )

    # Overlay ward boundaries
    fig.update_layout(
        mapbox_layers=[{
            "source": wards_geojson,
            "type": "line",
            "color": "#999999",
            "opacity": 0.3
        }]
    )
    return fig

# --- PM1 Map ---
st.subheader("🌫️ PM1 Concentration Map")
st.write("This map shows the concentration of PM1 (particles ≤ 1µm), which are extremely fine particles that can penetrate deep into lung tissue and potentially enter the bloodstream.")
st.plotly_chart(plot_pollution_map("pm1", color_schemes["pm1"]), use_container_width=True)

# --- PM2.5 Map ---
st.subheader("🌁 PM2.5 Concentration Map")
st.write("This map shows PM2.5 concentrations. PM2.5 particles are a common air quality metric and can have severe health impacts due to their ability to reach the respiratory system.")
st.plotly_chart(plot_pollution_map("pm25", color_schemes["pm25"]), use_container_width=True)

# --- PM10 Map ---
st.subheader("🏭 PM10 Concentration Map")
st.write("This map shows PM10 levels, which include larger particles like dust and pollen that may cause respiratory issues when inhaled over time.")
st.plotly_chart(plot_pollution_map("pm10", color_schemes["pm10"]), use_container_width=True)

# --- Sensor Data Table ---
st.subheader("📊 Sensor Data Preview")
st.dataframe(sensors_df.head(20))

# --- Download Option ---
st.download_button("📥 Download Sensor Data", sensors_df.to_csv(index=False), file_name="sensors_export.csv", mime="text/csv")

# --- About Section ---
st.markdown("""
---

# **About the Data**

Data was sourced from the Geographic Data Service, part of Smart Data Research UK and based at UCL, the University of Liverpool, the University of Oxford and the University of Edinburgh.

The data presents the location of and readings from sensors, generally at half-hour intervals, for various locations, generally road-side, in the City of Liverpool. They sense temperature and humidity, as well as PM1, PM2.5 and PM10 particulate matter concentration measurements. Each sensor has been professionally installed and calibrated by Aeternum Innovations. The raw data is obtained by Professor Jonny Higham from the School of Environmental Sciences at the University of Liverpool, who has cleaned and interpolated the raw data, to fit it in to the regular time intervals, also removing or correcting obviously faulty data, and making it available via a web portal.

| **Last Updated** | May 8, 2025, 4:25 PM (UTC+01:00) |
|------------------|----------------------------------|

🔗 [Dataset Link](https://data.geods.ac.uk/dataset/air-pollution-sensors-in-liverpool)
""")
