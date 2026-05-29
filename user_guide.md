# 📖 User Guide — Travel Planner Web Application

Welcome to the **Travel Planner**! This guide explains how to use the web application to organize places, compute optimized routes, manage advanced constraints (locked stops, hotel clustering), and share your travel itineraries.

---

## 🏛️ Getting Started & Authentication

To start planning your trips, you need to register and authenticate.

1. **Register**: Go to the **Register** page from the navigation bar. Enter a unique username, a valid email address, and a secure password.
2. **Log In**: Enter your credentials on the **Login** page. Upon successful login, you will be redirected to your **Dashboard**.
3. **Session Persistence**: The application securely remembers your session. If you close your browser, you will remain logged in until you explicitly click **Logout** in the navigation bar.

> [!NOTE]
> When you log out, your authentication token is revoked on the server for security.

---

## 📍 Managing Places & Landmarks

Before building a tour, you need a list of places you want to visit. You can manage them in the **Places** section.

### 1. Adding a Place
Click on **Places** in the navigation bar, and fill in the creation form:
* **Name**: The name of the landmark or location (e.g., `"Eiffel Tower"`, `"Louvre Museum"`).
* **Coordinates (Optional)**:
  * If you know the **Latitude** and **Longitude**, you can enter them manually.
  * If you leave them blank, the backend will **automatically resolve the coordinates** and city name using the **OpenStreetMap Nominatim Geocoding service** based on the name you entered.
* **Visibility**:
  * **Private**: Only visible to you.
  * **Public**: Available for other users to include in their own tours (useful for sharing common landmarks).

### 2. Viewing & Deleting Places
* All your created places and public places are listed in the Places view.
* You can search, filter, or delete places you own.
* **Database Cascade Safety**: If you delete a place that is currently part of an active tour, the system safely handles the cascade. The deleted place will be removed from your tours without crashing or corrupting the tour data.

---

## 🗺️ Creating & Optimizing Tours

A tour is an optimized route that connects at least 2 places in the shortest possible distance, returning to the starting point.

### 1. Generating a New Tour
1. From your **Dashboard**, click on the **Create Tour** button.
2. Enter a **Name** for your trip.
3. Select at least **2 places** from the list of available places.
4. Click **Generate Tour**.

The system will automatically solve the **Traveling Salesperson Problem (TSP)** using **Google OR-Tools** and display your optimized tour page.

### 2. Reading the Route & Map
On the tour details page, you will see two main sections:
* **Interactive Leaflet Map**: Displays markers for all stops. Animated flow lines (polylines) show the travel direction.
* **Step-by-Step Itinerary Card**: Displays the ordered list of stops, step numbers, and the distance between each segment.
  * **Unified Stop IDs**: The step numbers on the map correspond exactly to the steps shown in the drop-down list and itinerary cards.

---

## ⚙️ Advanced Route Constraints

Travel Planner offers powerful options to customize your itineraries:

### 1. Locked Positions (Fixed Stops)
If you have a fixed appointment (e.g., a flight at the start, or a booked museum slot at a specific index), you can **lock** places at specific stop numbers:
1. In the tour configuration or edit screen, specify the index position you want to lock for a place.
2. Click **Optimize**.
3. The solver will keep the locked place exactly at that step and calculate the shortest possible route for the remaining stops around it.

### 2. Clustered Hotel Layovers (Day-by-Day Loops)
When planning a multi-day trip over long distances, you may not want to travel continuously. You can set a **Max Distance** constraint to group visits into loops around hotel hubs:
* **Max Distance = 0 (Disabled)**: The route is a single continuous loop connecting all places.
* **Max Distance > 0 (Enabled)**:
  1. The starting point of your tour automatically becomes the first **Hotel**.
  2. The algorithm clusters other places. Any place further than your configured `Max Distance` (in kilometers) triggers the election of a new nearby place as a secondary hotel hub.
  3. The itinerary is split into **round-trips**: you start at the nearest hotel, travel to a landmark, and return to that hotel before visiting the next area.
  4. **Hotel Markers**: Passages to/from hotels are designated with an **`H`** badge instead of a step number, and do not increment the numerical step count.

---

## 👥 Public Sharing

You can share your optimized itineraries with friends or family:

1. On the tour page, locate the **Share Controls** section.
2. Toggle the visibility of the tour from **Private** to **Public**.
3. Click **Copy Share Link**.
4. Send the link to anyone! They will be able to view the interactive map and step-by-step itinerary on the public **Shared Tour** page **without needing to register or log in**.

> [!WARNING]
> If you set a public tour back to **Private**, any external users attempting to access the shared link will receive a `404 Not Found` page.
