import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from shapely.geometry import Point

# --- Streamlit page config ---
st.set_page_config(page_title="Liverpool Sensor Map", layout="wide")
st.title("🌍 Liverpool Environmental Sensor Dashboard")

# --- Load sensor data ---
try:
    sensors_df = pd.read_csv("sensors.csv")
except FileNotFoundError:
    st.error("🚫 sensors.csv not found. Please upload it or check the file path.")
    st.stop()

# Ensure coordinates are numeric
sensors_df["lon"] = pd.to_numeric(sensors_df["lon"], errors="coerce")
sensors_df["lat"] = pd.to_numeric(sensors_df["lat"], errors="coerce")
sensors_df.dropna(subset=["lon", "lat"], inplace=True)

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(sensors_df["lon"], sensors_df["lat"])]
gdf_sensors = gpd.GeoDataFrame(sensors_df, geometry=geometry, crs="EPSG:4326")

# --- Load ward shapefile ---
try:
    wards_gdf = gpd.read_file("Wards/WardsPolygon.shp").to_crs("EPSG:4326")
except Exception as e:
    wards_gdf = None
    st.warning("⚠️ Could not load ward shapefile. Check the path or format.")

# --- Sidebar controls ---
param = st.sidebar.selectbox("Parameter to View", ["temp", "humid", "pm1", "pm25", "pm10"])
color = st.sidebar.color_picker("Select Marker Color", "#FF5733")
show_wards = st.sidebar.checkbox("Show Ward Boundaries", value=True)

# --- Create Plotly map ---
fig = px.scatter_mapbox(
    gdf_sensors,
    lat=gdf_sensors.geometry.y,
    lon=gdf_sensors.geometry.x,
    color=param,
    color_continuous_scale="Viridis",
    zoom=11,
    height=600,
    hover_name="sensor_id" if "sensor_id" in gdf_sensors.columns else None,
    mapbox_style="open-street-map",
)

# --- Add ward boundaries if available ---
if show_wards and wards_gdf is not None:
    for _, ward in wards_gdf.iterrows():
        x, y = ward.geometry.exterior.xy
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=x,
            lat=y,
            line=dict(width=1, color="gray"),
            name=str(ward.get("ward_name", "Ward"))
        ))

# --- Display the map ---
st.plotly_chart(fig, use_container_width=True)

# --- Expandable info ---
with st.expander("ℹ️ About this map"):
    st.markdown("""
    - Sensors show live or recorded environmental data like temperature and particulates.
    - Use the sidebar to change the data shown and toggle ward boundaries.
    - Hover over points to see sensor ID and values.
    """)

# --- Data Table ---
st.subheader("📊 Sensor Data Preview")
st.dataframe(sensors_df.head(20))

# --- Download Button ---
st.download_button(
    "📥 Download Sensor Data",
    sensors_df.to_csv(index=False),
    file_name="sensors_export.csv",
    mime="text/csv"
)
