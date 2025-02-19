import streamlit as st
import pandas as pd
import requests
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
from streamlit_folium import folium_static

API_KEY = 'AIzaSyAy_hqapYwf5RNEO-xwuLdOvphVzTAzSSA'  # Replace with your actual API key

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
            distance = response['routes'][0]['legs'][0]['distance']['value']
            return distance
        else:
            st.warning(f"Distance API failed for {origin} -> {destination}: {response['status']} - {response.get('error_message')}")
            return float('inf')
    except Exception as e:
        st.error(f"Error getting distance for {origin} -> {destination}: {e}")
        return float('inf')

# Step 4: Build Distance Matrix
def build_distance_matrix(coordinates):
    n = len(coordinates)
    distance_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                origin = f"{coordinates[i][0]},{coordinates[i][1]}"
                destination = f"{coordinates[j][0]},{coordinates[j][1]}"
                distance_matrix[i][j] = get_distance(origin, destination)
                time.sleep(0.5)  # Prevent rate limit
    return distance_matrix

# Step 5: Solve TSP
def solve_tsp(distance_matrix):
    n = len(distance_matrix)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

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

# Step 6: Build Google Maps URL
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
            coordinates.append(coords)
            valid_addresses.append(address)
            st.write(f"✅ {address} -> {coords}")
        else:
            st.write(f"❌ Skipped {address}")
        time.sleep(0.5)

    if len(coordinates) < 2:
        st.error("❌ Not enough valid addresses.")
    else:
        st.write("🗺️ **Plotting Addresses on Map...**")
        m = folium.Map(location=coordinates[0], zoom_start=14)
        for i, (lat, lng) in enumerate(coordinates):
            folium.Marker([lat, lng], popup=valid_addresses[i]).add_to(m)
        folium_static(m)

        st.write("📏 **Building Distance Matrix...**")
        distance_matrix = build_distance_matrix(coordinates)

        st.write("🧠 **Solving Optimal Route (TSP)...**")
        optimal_order = solve_tsp(distance_matrix)

        if optimal_order:
            st.write("🚶‍♀️ **Optimal Route Order:**")
            optimal_route_addresses = [valid_addresses[i] for i in optimal_order]
            for addr in optimal_route_addresses:
                st.write(addr)

            st.write("🌍 **Open Route in Google Maps:**")
            url = build_google_maps_url(coordinates, optimal_order)
            st.markdown(f"[📍 View Route in Google Maps]({url})", unsafe_allow_html=True)
        else:
            st.error("❌ Could not solve TSP problem.")

