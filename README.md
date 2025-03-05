# 🚪 Door Knock Route Optimizer

The **Door Knock Route Optimizer** is a **Python-based Streamlit web app** that helps real estate professionals and sales agents **optimize their door-knocking routes**. It automatically processes a list of addresses, generates the most **efficient route**, and **avoids cemeteries, railway areas, and other non-preferred locations**, ensuring time and effort are spent in high-potential neighborhoods.

---

## 🔗 Try the Live App
🚀 **Live Demo:** [Door Knock Route Optimizer](https://cindyxiao1-door-knock-route-optimizer-readaddress-za7diy.streamlit.app/)

---

## 🌟 Features

### ✅ **Core Functionality**
- **🚀 Route Optimization:** Computes the shortest path for door-knocking, reducing travel time and effort.
- **📌 Custom Address Filtering:** Users can exclude specific areas that are not hotspots for selling houses.
- **📂 Multi-format Address Input Support:** Supports both `.csv` and `.txt` address files.

### 🚫 **Avoidance Zones**
- **⚰️ Cemeteries and 🚂 Railway Areas:** Automatically detects and avoids these areas to focus on more relevant locations.
- **🔍 Non-Hotspot Areas:** Users can configure the system to skip locations unlikely to generate sales.

### 🗺 **Map Visualization**
- **📍 Marking Excluded Areas:** Cemeteries and railway zones are visually highlighted on the map.
- **🚶 Optimized Route Display:** Generates a mapped route that **avoids unnecessary regions while maximizing efficiency**.

---


## 📂 Project Structure
- **README.md** - Documentation (this file)
- **addresses.csv** - List of addresses in CSV format
- **addresses.txt** - Alternative list of addresses
- **readAddress.py** - Python script for processing and optimizing routes
- **map_visualization.py** - Generates and displays the optimized map
- **route_optimizer.py** - Core logic for route calculation
- **config.json** - Configurable parameters (e.g., excluded areas)


👤 Contributors
Cindy Xiao - Developer & Maintainer 👩‍💻
🔗 GitHub: @CindyXiao1