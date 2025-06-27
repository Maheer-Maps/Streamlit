import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from shapely.geometry import Point

st.set_page_config(page_title="Liverpool Sensor Map", layout="wide")

st.title("🌍 Liverpool Environmental Sensor Dashboard")

# Load sensor data
sensors_df = pd.read_csv("sensors.csv")

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

# Filter selection
param = st.sidebar.selectbox("Parameter to View", ["temp", "humid", "pm1", "pm25", "pm10"])
color = st.sidebar.color_picker("Select Marker Color", "#FF5733")
show_wards = st.sidebar.checkbox("Show Ward Boundaries", value=True)

# Plot using Plotly
fig = px.scatter_mapbox(
    gdf_sensors,
    lat=gdf_sensors.geometry.y,
    lon=gdf_sensors.geometry.x,
    color=param,
    color_continuous_scale="Viridis",
    size_max=15,
    zoom=11,
    height=600,
    hover_name="sensor_id" if "sensor_id" in gdf_sensors.columns else None,
    mapbox_style="carto-positron"
)

# Overlay ward boundaries (optional)
if show_wards:
    for _, ward in wards_gdf.iterrows():
        geojson = ward.geometry.__geo_interface__
        fig.add_trace(px.choropleth_mapbox(
            gpd.GeoDataFrame([ward]), 
            geojson=geojson, 
            locations=[0], 
            color_discrete_sequence=["#cccccc"],
            opacity=0.1
        ).data[0])

st.plotly_chart(fig, use_container_width=True)

# Optional: Expandable info
with st.expander("ℹ️ About this map"):
    st.write("""
        - Sensors represent real-time or recorded environmental data.
        - Hover over a point to see its values.
        - Toggle ward boundaries on or off via the sidebar.
    """)

# Data Table Viewer
st.subheader("📊 Sensor Data Preview")
st.dataframe(sensors_df.head(20))

# Download option
st.download_button("📥 Download Sensor Data", sensors_df.to_csv(index=False), file_name="sensors_export.csv", mime="text/csv")
