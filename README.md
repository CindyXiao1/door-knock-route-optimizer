# 🚪 Door Knock Route Optimizer

The **Door Knock Route Optimizer** is a Python-based tool that helps real estate professionals and sales agents optimize their door-knocking routes. The system processes a list of addresses and generates an efficient path while **avoiding cemeteries and railway areas**, ensuring time and effort are spent in high-potential neighborhoods.

## 🌟 Features

### ✅ **Core Functionality**
- **Efficient Route Optimization:** Computes the shortest path for door-knocking, reducing travel time and effort.
- **Custom Address Filtering:** Users can **exclude specific areas** that are **not hotspots** for selling houses.
- **Multi-format Address Input Support:** Supports both `.csv` and `.txt` address files.

### 🚫 **Avoidance Zones**
- **Cemeteries and Railway Areas:** Automatically detects and avoids these areas to focus on more relevant locations.
- **Non-Hotspot Areas:** Users can configure the system to skip locations that are unlikely to generate sales.

### 🗺 **Map Visualization**
- **Marking Excluded Areas:** Cemeteries and railway zones are visually highlighted on the map.
- **Optimized Route Display:** Generates a mapped route that avoids unnecessary regions while maximizing efficiency.

## 📂 Project Structure
- **README.md** - Documentation (this file)
- **addresses.csv** - List of addresses in CSV format
- **addresses.txt** - Alternative list of addresses
- **readAddress.py** - Python script for processing and optimizing routes
- **map_visualization.py** - Generates and displays the optimized map
- **route_optimizer.py** - Core logic for route calculation
- **config.json** - Configurable parameters (e.g., excluded areas)
