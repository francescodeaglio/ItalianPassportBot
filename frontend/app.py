import json
from datetime import datetime
import plotly.express as px

import streamlit as st
import os
import mysql.connector
import folium
import pandas as pd
from streamlit_folium import st_folium
import geopandas as gpd
import pydeck as pdk


st.set_page_config(layout="wide")

connection = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database="passport",
        port="3306"
    )
@st.cache_data(ttl=30)
def query_db_create_map():

    cursor = connection.cursor()
    av_map = {}
    cursor.execute(
        "SELECT province_shortcut, count(*) from availabilities as a, office as o where a.office_id = o.office_id and available='1' GROUP BY province_shortcut, province")

    for province, count in cursor.fetchall():
        av_map[province.upper()] = count

    return av_map


def get_data():

    with open("frontend/province_geo.json", "r") as f:
        df_data = json.load(f)

    df = pd.DataFrame(df_data)
    df.loc[df.name.str.contains("Carbonia"), "province"] = "SU"
    df.loc[df.name.str.contains("Iglesias"), "province"] = "SU"
    import pydeck as pdk

    # Initialize Folium Map
    m = folium.Map(location=[42.0646766, 12.1851513], zoom_start=5.5)

    # Add markers for each data point

    # Save the map as an HTML file
    return m
def map_avail(province):
    province = province.upper()
    if province in av_map:
        return 255
    else:
        return 0
def get_region_map():

    file = "frontend/limits_IT_provinces.geojson"
    with open("frontend/province_geo.json", "r") as f:
        df_data = json.load(f)

    df = pd.DataFrame(df_data)


    provinces = gpd.read_file(file)

    grouped_df = df.groupby("province").count()["name"]

    grouped_df = pd.DataFrame(grouped_df)
    grouped_df["join"] = grouped_df.index.str.upper().tolist()
    grouped_df["value"] = grouped_df["join"].apply(map_avail)
    result_df = pd.merge(provinces, grouped_df, left_on='prov_acr', right_on='join', how='inner')
    result_df = gpd.GeoDataFrame(result_df)

    INITIAL_VIEW_STATE = pdk.ViewState(latitude=43.4646766, longitude=9.1851513, zoom=4, bearing=0, pitch=0)

    m = folium.Map(location=[42.0646766, 12.1851513], zoom_start=5)

    # Convert GeoJSON data to a string

    # Add GeoJSON layer to Folium map
    folium.GeoJson(
        result_df,
        name='geojson_layer',
        style_function=lambda feature: {
            'fillColor': f'rgb({255 - feature["properties"]["value"]},{feature["properties"]["value"]},0)',
            'color': 'black',
            'weight': 0.5,
            'opacity': 0.8,
            'fillOpacity': 0.8
        },
        highlight_function=lambda x: {'weight': 3, 'color': 'black'},
        tooltip=folium.features.GeoJsonTooltip(fields=["prov_name", "prov_acr" ], aliases=["Provincia", "Shortcut"])
    ).add_to(m)

    for index, row in df.iterrows():
        folium.CircleMarker(
            location=[row['coordinates'][1], row['coordinates'][0]],
            radius=0.5,
            color='#000000',
            fill=True,
            fill_color='#FFFFFF',
            fill_opacity=0.8,
            popup=f"{row['name']}\n{row['address']}\nApertura: {row['open']}"
        ).add_to(m)

    return m


def temporal_group_by(result, office_id, name):
    timestamps = list(map(lambda x: (x["discovered_timestamp"], "ADD"),
                          filter(lambda x: x["office_id"] == office_id, result))) + list(
        map(lambda x: (x["ended_timestamp"], "REMOVE"), filter(lambda x: x["office_id"] == office_id, result)))
    counter = 0
    previous_ts = None
    times = []
    for ts, op in sorted(timestamps):
        if previous_ts is None:
            previous_ts = ts
            counter += 1
            continue

        if previous_ts != ts and counter > 0:
            times.append({
                "office_id": office_id,
                "Office Name": name,
                "start": previous_ts,
                "end": ts,
                "count": counter
            })

        if op == "ADD":
            counter += 1
        else:
            counter -= 1

        previous_ts = ts
    return times

def query_province(province):
    connection.commit()
    cursor = connection.cursor()
    query = f"""
    SELECT name, availability_id, a.office_id, discovered_timestamp, ended_timestamp, day, hour
    FROM availabilities as a, office as o
    WHERE a.office_id=o.office_id and o.province_shortcut="{province}"
    """
    cursor.execute(query)
    result = [{
        "name": entry[0],
        "availability_id": entry[1],
        "office_id": entry[2],
        "discovered_timestamp": datetime.utcfromtimestamp(entry[3]),
        "ended_timestamp": datetime.utcfromtimestamp(entry[4]) if entry[4] else datetime.now(),
        "day": entry[5],
        "hour": entry[6]
    } for entry in cursor.fetchall()]

    offices = set(map(lambda x: (x["office_id"], x["name"]), result))
    r = []
    for id, name in offices:
        name = name.split("-")[1]
        r += temporal_group_by(result, id, name)
    df = pd.DataFrame(r)
    return px.timeline(df, x_start="start", x_end="end", y="Office Name", color="count")

av_map = query_db_create_map()
m = get_region_map()
#m = get_data()

placeholder = st.empty()
col1, col2 = st.columns([0.3, 0.7])

with col1:
    st_data = st_folium(m)

shortcut = None
if st_data["last_object_clicked_tooltip"] is not None:
    province = st_data["last_object_clicked_tooltip"].split("Provincia")[1].split("Shortcut")[0].strip()
    shortcut = st_data["last_object_clicked_tooltip"].split("Provincia")[1].split("Shortcut")[1].strip()

if shortcut:
    placeholder.write("## Selected " + province)
else:
    placeholder.write("## Click on a province to see availability")


with col2:

    if shortcut:
        st.plotly_chart(query_province(shortcut), )