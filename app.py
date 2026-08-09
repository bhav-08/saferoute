import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2

# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="SafeRoute",
    page_icon="🛡️",
    layout="wide"
)

REPORT_FILE = "safety_reports.csv"


# =====================================================
# DATABASE FUNCTIONS
# =====================================================

def load_reports():

    if os.path.exists(REPORT_FILE):
        return pd.read_csv(REPORT_FILE)

    return pd.DataFrame(
        columns=[
            "Issue",
            "Location",
            "Severity",
            "Description",
            "Latitude",
            "Longitude"
        ]
    )


def save_report(
    issue,
    location,
    severity,
    description,
    latitude,
    longitude
):

    new_report = pd.DataFrame([
        {
            "Issue": issue,
            "Location": location,
            "Severity": severity,
            "Description": description,
            "Latitude": latitude,
            "Longitude": longitude
        }
    ])

    if os.path.exists(REPORT_FILE):

        new_report.to_csv(
            REPORT_FILE,
            mode="a",
            header=False,
            index=False
        )

    else:

        new_report.to_csv(
            REPORT_FILE,
            index=False
        )


# =====================================================
# GEOCODING
# =====================================================

def get_coordinates(place):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "SafeRoute Student Project"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return (
        float(data[0]["lat"]),
        float(data[0]["lon"])
    )


# =====================================================
# DISTANCE FUNCTION
# =====================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


# =====================================================
# SAFETY SCORE
# =====================================================

def calculate_safety_score(
    route_points,
    reports
):

    score = 100

    if reports.empty:
        return score

    for _, report in reports.iterrows():

        try:

            report_lat = float(
                report["Latitude"]
            )

            report_lon = float(
                report["Longitude"]
            )

        except:
            continue

        closest_distance = min(
            calculate_distance(
                point[0],
                point[1],
                report_lat,
                report_lon
            )
            for point in route_points
        )

        # Only consider reports within
        # approximately 1 km of the route

        if closest_distance <= 1:

            severity = report["Severity"]

            if severity == "High":
                score -= 20

            elif severity == "Medium":
                score -= 10

            else:
                score -= 5

    return max(0, score)


# =====================================================
# PAGE TITLE
# =====================================================

st.title("🛡️ SafeRoute")

st.write(
    "### Navigate Smarter. Choose Safer."
)

st.write(
    "Find routes, view safety information, "
    "and help your community report safety concerns."
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🛡️ SafeRoute")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "🗺️ Find Route",
        "🚨 Report Issue",
        "📊 Safety Reports"
    ]
)


# =====================================================
# HOME
# =====================================================

if page == "🏠 Home":

    st.header("Welcome to SafeRoute 👋")

    st.write(
        "SafeRoute combines route information "
        "with community safety reports."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("🗺️ Find Routes")

        st.write(
            "Find an actual road route between "
            "your starting point and destination."
        )

    with col2:

        st.subheader("🛡️ Safety Score")

        st.write(
            "Get a safety score based on "
            "reported issues near the route."
        )

    with col3:

        st.subheader("🚨 Report Issues")

        st.write(
            "Report poor lighting, road hazards "
            "and other safety concerns."
        )

    st.divider()

    reports = load_reports()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🚨 Community Reports",
            len(reports)
        )

    with col2:

        st.metric(
            "🛡️ Safety System",
            "Active"
        )


# =====================================================
# FIND ROUTE
# =====================================================

elif page == "🗺️ Find Route":

    st.header("🗺️ Find a Route")

    start = st.text_input(
        "Starting Location",
        placeholder="Example: Chennai"
    )

    destination = st.text_input(
        "Destination",
        placeholder="Example: Tambaram"
    )

    if "route_data" not in st.session_state:
        st.session_state.route_data = None

    if "route_start" not in st.session_state:
        st.session_state.route_start = None

    if "route_destination" not in st.session_state:
        st.session_state.route_destination = None

    if st.button("🔎 Find Route"):

        if not start or not destination:

            st.warning(
                "Please enter both locations."
            )

        else:

            try:

                start_coords = get_coordinates(start)

                destination_coords = get_coordinates(
                    destination
                )

                if start_coords is None:

                    st.error(
                        "Starting location not found."
                    )

                    st.stop()

                if destination_coords is None:

                    st.error(
                        "Destination not found."
                    )

                    st.stop()

                start_lat, start_lon = start_coords

                dest_lat, dest_lon = destination_coords

                # -------------------------------------
                # ROUTING
                # -------------------------------------

                route_url = (
                    "https://router.project-osrm.org/"
                    "route/v1/driving/"
                    f"{start_lon},{start_lat};"
                    f"{dest_lon},{dest_lat}"
                )

                params = {
                    "overview": "full",
                    "geometries": "geojson"
                }

                response = requests.get(
                    route_url,
                    params=params,
                    timeout=20
                )

                response.raise_for_status()

                data = response.json()

                if data.get("code") != "Ok":

                    st.error(
                        "Could not find a road route."
                    )

                    st.stop()

                route = data["routes"][0]

                st.session_state.route_data = route

                st.session_state.route_start = (
                    start_lat,
                    start_lon
                )

                st.session_state.route_destination = (
                    dest_lat,
                    dest_lon
                )

                st.session_state.route_start_name = start

                st.session_state.route_destination_name = (
                    destination
                )

                st.success(
                    "✅ Route found successfully!"
                )

            except Exception as e:

                st.error(
                    "Unable to find the route."
                )

                st.write(
                    "Error:",
                    str(e)
                )

    # =================================================
    # DISPLAY ROUTE
    # =================================================

    if st.session_state.route_data is not None:

        route = st.session_state.route_data

        start_lat, start_lon = (
            st.session_state.route_start
        )

        dest_lat, dest_lon = (
            st.session_state.route_destination
        )

        # ---------------------------------------------
        # ROUTE COORDINATES
        # ---------------------------------------------

        route_points = []

        for point in route["geometry"]["coordinates"]:

            longitude = point[0]

            latitude = point[1]

            route_points.append(
                [latitude, longitude]
            )

        # ---------------------------------------------
        # SAFETY SCORE
        # ---------------------------------------------

        reports = load_reports()

        safety_score = calculate_safety_score(
            route_points,
            reports
        )

        # ---------------------------------------------
        # ROUTE DETAILS
        # ---------------------------------------------

        distance = route["distance"] / 1000

        duration = route["duration"] / 60

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📏 Distance",
                f"{distance:.2f} km"
            )

        with col2:

            st.metric(
                "⏱️ Estimated Time",
                f"{duration:.0f} min"
            )

        with col3:

            st.metric(
                "🛡️ Safety Score",
                f"{safety_score}/100"
            )

        # ---------------------------------------------
        # SAFETY STATUS
        # ---------------------------------------------

        if safety_score >= 80:

            st.success(
                f"🟢 Safer Route — {safety_score}/100"
            )

        elif safety_score >= 60:

            st.warning(
                f"🟡 Moderate Risk — {safety_score}/100"
            )

        else:

            st.error(
                f"🔴 Higher Risk — {safety_score}/100"
            )

        # ---------------------------------------------
        # CREATE MAP
        # ---------------------------------------------

        center_lat = (
            start_lat + dest_lat
        ) / 2

        center_lon = (
            start_lon + dest_lon
        ) / 2

        route_map = folium.Map(
            location=[
                center_lat,
                center_lon
            ],
            zoom_start=11
        )

        # ---------------------------------------------
        # START MARKER
        # ---------------------------------------------

        folium.Marker(
            [start_lat, start_lon],
            tooltip="🟢 Start",
            popup="Starting Location",
            icon=folium.Icon(
                color="green"
            )
        ).add_to(route_map)

        # ---------------------------------------------
        # DESTINATION MARKER
        # ---------------------------------------------

        folium.Marker(
            [dest_lat, dest_lon],
            tooltip="🔴 Destination",
            popup="Destination",
            icon=folium.Icon(
                color="red"
            )
        ).add_to(route_map)

        # ---------------------------------------------
        # ROUTE
        # ---------------------------------------------

        folium.PolyLine(
            route_points,
            weight=6,
            opacity=0.8,
            tooltip="SafeRoute"
        ).add_to(route_map)

        # ---------------------------------------------
        # REPORT MARKERS
        # ---------------------------------------------

        for _, report in reports.iterrows():

            try:

                lat = float(
                    report["Latitude"]
                )

                lon = float(
                    report["Longitude"]
                )

                if report["Severity"] == "High":

                    color = "red"

                elif report["Severity"] == "Medium":

                    color = "orange"

                else:

                    color = "blue"

                folium.Marker(
                    [lat, lon],
                    tooltip="🚨 Safety Report",
                    popup=(
                        f"Issue: {report['Issue']}<br>"
                        f"Severity: {report['Severity']}<br>"
                        f"Location: {report['Location']}"
                    ),
                    icon=folium.Icon(
                        color=color,
                        icon="warning-sign"
                    )
                ).add_to(route_map)

            except:
                pass

        # ---------------------------------------------
        # DISPLAY MAP
        # ---------------------------------------------

        st.subheader("🗺️ Your Route")

        st_folium(
            route_map,
            width=1200,
            height=600,
            key="safe_route_map"
        )


# =====================================================
# REPORT ISSUE
# =====================================================

elif page == "🚨 Report Issue":

    st.header("🚨 Report a Safety Issue")

    st.write(
        "Your report helps other people understand "
        "potential safety concerns."
    )

    issue = st.selectbox(
        "Issue Type",
        [
            "Poor Lighting",
            "Road Hazard",
            "Accident-Prone Area",
            "Isolated Area",
            "Other"
        ]
    )

    location = st.text_input(
        "Location",
        placeholder="Example: College Main Gate"
    )

    description = st.text_area(
        "Description",
        placeholder="Describe the safety concern..."
    )

    severity = st.selectbox(
        "Severity",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    if st.button("🚨 Submit Report"):

        if not location or not description:

            st.warning(
                "Please enter the location and description."
            )

        else:

            try:

                coords = get_coordinates(location)

                if coords is None:

                    st.error(
                        "Could not find this location. "
                        "Try adding the city name."
                    )

                else:

                    latitude, longitude = coords

                    save_report(
                        issue,
                        location,
                        severity,
                        description,
                        latitude,
                        longitude
                    )

                    st.success(
                        "✅ Safety report saved successfully!"
                    )

                    st.info(
                        "Your report will now be considered "
                        "when calculating route safety."
                    )

            except Exception as e:

                st.error(
                    "Could not save the report."
                )

                st.write(
                    "Error:",
                    str(e)
                )


# =====================================================
# SAFETY REPORTS
# =====================================================

elif page == "📊 Safety Reports":

    st.header("📊 Community Safety Reports")

    reports = load_reports()

    if reports.empty:

        st.info(
            "No safety reports have been submitted yet."
        )

    else:

        st.success(
            f"📊 {len(reports)} community report(s) found."
        )

        # ---------------------------------------------
        # SUMMARY
        # ---------------------------------------------

        high_count = len(
            reports[
                reports["Severity"] == "High"
            ]
        )

        medium_count = len(
            reports[
                reports["Severity"] == "Medium"
            ]
        )

        low_count = len(
            reports[
                reports["Severity"] == "Low"
            ]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🔴 High",
                high_count
            )

        with col2:
            st.metric(
                "🟠 Medium",
                medium_count
            )

        with col3:
            st.metric(
                "🔵 Low",
                low_count
            )

        st.divider()

        # ---------------------------------------------
        # REPORT TABLE
        # ---------------------------------------------

        st.subheader(
            "🚨 Reported Safety Issues"
        )

        st.dataframe(
            reports[
                [
                    "Issue",
                    "Location",
                    "Severity",
                    "Description"
                ]
            ],
            use_container_width=True
        )

        # ---------------------------------------------
        # REPORT MAP
        # ---------------------------------------------

        st.subheader(
            "🗺️ Report Locations"
        )

        report_map = folium.Map(
            location=[
                13.0827,
                80.2707
            ],
            zoom_start=11
        )

        for _, report in reports.iterrows():

            try:

                lat = float(
                    report["Latitude"]
                )

                lon = float(
                    report["Longitude"]
                )

                if report["Severity"] == "High":

                    color = "red"

                elif report["Severity"] == "Medium":

                    color = "orange"

                else:

                    color = "blue"

                folium.Marker(
                    [lat, lon],
                    tooltip=report["Issue"],
                    popup=(
                        f"<b>Issue:</b> {report['Issue']}<br>"
                        f"<b>Location:</b> {report['Location']}<br>"
                        f"<b>Severity:</b> {report['Severity']}"
                    ),
                    icon=folium.Icon(
                        color=color,
                        icon="warning-sign"
                    )
                ).add_to(report_map)

            except:
                pass

        st_folium(
            report_map,
            width=1200,
            height=500,
            key="report_map"
        )

        # ---------------------------------------------
        # DELETE ALL REPORTS
        # ---------------------------------------------

        st.divider()

        if st.button(
            "🗑️ Clear All Reports"
        ):

            if os.path.exists(REPORT_FILE):

                os.remove(REPORT_FILE)

                st.success(
                    "All reports have been cleared."
                )

                st.rerun()