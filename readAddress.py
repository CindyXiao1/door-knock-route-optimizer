import streamlit as st
import pandas as pd
import requests
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
from streamlit_folium import folium_static
from shapely.geometry import Polygon, Point
import toml


# Debugging: Print loaded secrets
st.write("Secrets Loaded: ", st.secrets)

# Load API Key from Streamlit Secrets Manager
API_KEY = st.secrets.get("API_KEY", "MISSING_API_KEY")

# Debugging: Check if API key is retrieved
st.write("API Key Used: ", API_KEY)
# Step 2: Convert Address to Coordinates
def get_coordinates(address):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'
    try:
        response = requests.get(url).json()
        if response['status'] == 'OK':
            location = response['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            st.warning(f"Geocoding failed for {address}: {response['status']} - {response.get('error_message')}")
            return None
    except Exception as e:
        st.error(f"Error during geocoding {address}: {e}")
        return None

# Step 3: Get Distance (Directions API)
def get_distance(origin, destination, mode='walking'):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode={mode}&key={API_KEY}"
    try:
        response = requests.get(url).json()
        if response['status'] == 'OK':
            return response['routes'][0]['legs'][0]['distance']['value']
        else:
            st.warning(f"Distance API failed for {origin} -> {destination}: {response['status']} - {response.get('error_message')}")
            return float('inf')
    except Exception as e:
        st.error(f"Error getting distance for {origin} -> {destination}: {e}")
        return float('inf')

# Step 4: Fetch Nearby Railways & Cemeteries (Google Places API)
def get_places_nearby(location, place_type, radius=5000):
    """Fetches railways or cemeteries near a given location."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{location[0]},{location[1]}",
        "radius": radius,
        "type": place_type,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    if response.get("status") == "OK":
        return [(p["geometry"]["location"]["lat"], p["geometry"]["location"]["lng"]) for p in response["results"]]
    elif response.get("status") == "ZERO_RESULTS":
        return []  # No need to display a warning, just return an empty list
    else:
        st.warning(f"⚠️ API Error fetching {place_type}: {response.get('status')} - {response.get('error_message')}")
        return []

# Step 5: Check if Address is in Avoid Zone
def is_in_avoid_zone(lat, lng, polygon):
    """Checks if a location is inside a given Polygon avoid zone."""
    if polygon:
        return polygon.contains(Point(lat, lng))
    return False

# Step 6: Build Distance Matrix
def build_distance_matrix(coordinates):
    n = len(coordinates)
    distance_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                origin = f"{coordinates[i][0]},{coordinates[i][1]}"
                destination = f"{coordinates[j][0]},{coordinates[j][1]}"
                distance_matrix[i][j] = get_distance(origin, destination)
                time.sleep(0.5)  # Prevent API rate limit issues
    return distance_matrix

# Step 7: Solve TSP (Find Shortest Route)
def solve_tsp(distance_matrix):
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        return route
    else:
        return None

# Step 8: Build Google Maps URL
def build_google_maps_url(coords, optimal_order):
    base_url = "https://www.google.com/maps/dir/"
    ordered_coords = [coords[i] for i in optimal_order]
    waypoints = "/".join(f"{lat},{lng}" for lat, lng in ordered_coords)
    return base_url + waypoints

# --- Streamlit App ---
st.title("🚪 Door Knock Route Optimizer")

uploaded_file = st.file_uploader("📤 Upload Addresses TXT File", type="txt")

if uploaded_file is not None:
    addresses = uploaded_file.read().decode('utf-8').splitlines()
    st.write("📍 **Geocoding Addresses...**")

    coordinates = []
    valid_addresses = []

    for address in addresses:
        coords = get_coordinates(address)
        if coords:
            # Get nearby railways & cemeteries
            railways = get_places_nearby(coords, "train_station")
            cemeteries = get_places_nearby(coords, "cemetery")

            # Create polygons if locations exist
            railway_polygon = Polygon(railways) if railways else None
            cemetery_polygon = Polygon(cemeteries) if cemeteries else None

            # Check if address is too close to railway or cemetery
            too_close = is_in_avoid_zone(coords[0], coords[1], railway_polygon) or \
                        is_in_avoid_zone(coords[0], coords[1], cemetery_polygon)

            if too_close:
                st.write(f"🚫 Skipped {address} (Near Railway or Cemetery)")
            else:
                coordinates.append(coords)
                valid_addresses.append(address)
                st.write(f"✅ {address} -> {coords}")
        else:
            st.write(f"❌ Skipped {address} (Invalid Location)")

        time.sleep(0.5)

    if len(coordinates) < 2:
        st.error("❌ Not enough valid addresses.")
    else:
        st.write("🗺️ **Plotting Addresses on Map...**")
        m = folium.Map(location=coordinates[0], zoom_start=14)

        # Add valid addresses to map
        for i, (lat, lng) in enumerate(coordinates):
            folium.Marker([lat, lng], popup=valid_addresses[i]).add_to(m)

        # Mark railways & cemeteries
        for lat, lng in get_places_nearby(coordinates[0], "train_station"):
            folium.Marker([lat, lng], icon=folium.Icon(color="blue", icon="train"), popup="Railway").add_to(m)

        for lat, lng in get_places_nearby(coordinates[0], "cemetery"):
            folium.Marker([lat, lng], icon=folium.Icon(color="black", icon="cross"), popup="Cemetery").add_to(m)

        folium_static(m)

        st.write("📏 **Building Distance Matrix...**")
        distance_matrix = build_distance_matrix(coordinates)

        st.write("🧠 **Solving Optimal Route (TSP)...**")
        optimal_order = solve_tsp(distance_matrix)

        if optimal_order:
            st.write("🚶‍♀️ **Optimal Route Order:**")
            for addr in [valid_addresses[i] for i in optimal_order]:
                st.write(addr)

            st.write("🌍 **Open Route in Google Maps:**")
            url = build_google_maps_url(coordinates, optimal_order)
            st.markdown(f"[📍 View Route in Google Maps]({url})", unsafe_allow_html=True)
        else:
            st.error("❌ Could not solve TSP problem.")
