# 📖 User Guide — Himeji Planner

Welcome to **Himeji Planner**! This guide explains how to use the web application to organize places, compute optimized routes, manage advanced constraints, and share your travel itineraries.

> [!TIP]
> **Not sure how to run the application?**  
> If you need to set up or run the application locally, please consult the installation and execution steps in the [README.md](file:///home/robyn/Documents/Programmation/box-certificative-himeji/README.md) file first.

---

## 🔑 1. Authentication (Guest View)

When you are not logged in, you only have access to public itineraries and pages. To use all the features of the platform, you must authenticate:
* **Register**: Create a new account with a unique username, a valid email address, and a secure password.
* **Login**: Sign in with your registered credentials. Your session is securely preserved so you remain logged in even after closing your browser.

---

## 📊 2. Dashboard

Once logged in, the Dashboard serves as your personal workspace and displays a **complete summary of your account activity**:
* **Itineraries Created (Itineraries published)**: The total number of tours you have saved.
* **Kilometers Calculated (Total optimized km)**: The cumulative distance of all your optimized routes.
* **Private Itineraries**: The number of tours configured with private visibility.
* **Quick Access Navigation**: Easy shortcuts to discover places, plan new trips, or check your saved tours.

---

## 📍 3. Places to Visit

This section is dedicated to managing and exploring destinations:
* **Public Places List**: A list of public interest points and landmarks available to all users on the platform.
* **My Private Places List (when logged in)**: A personal, private list of landmarks that only you can see and include in your itineraries.
* **Adding a New Place**:
  * Enter a place name.
  * If you leave the coordinates blank, the system automatically resolves the **Latitude**, **Longitude** using the **OpenStreetMap Nominatim Geocoding API**.
  * Choose whether the place should be public or private.
* **Editing Owned Places (when logged in)**: You can edit the name, coordinates, city, or visibility of any place you created.
* **Robust Place Deletion**: If you delete a place that is currently referenced by one of your tours, the backend handles the deletion gracefully via cascades. The place will be removed from your tours without corrupting or crashing the itineraries.

---

## 🎒 4. Planify Travel (Creating an Itinerary)

The **Planify Travel** view allows you to dynamically build and preview optimized routes:
1. **Selecting Places**: Choose the locations you want to include in your trip by checking them in the list.
2. **Filtering**: You can search and filter the list of places by name or city to quickly locate your desired stops.
3. **Initial Route Generation (Preview)**: Click **Generate Tour**. The system solves the **Traveling Salesperson Problem (TSP)** using **Google OR-Tools** and calculates the shortest route starting and ending at your first chosen location.
4. **Validation (Save)**: Inspect the optimized path on the interactive map and review the step-by-step distance breakdown. If you are satisfied with the result, click the **Save** or **Validate** button to permanently save the tour to your account.

---

## 🗺️ 5. Tours

The **Tours** view lists all itineraries:
* **My Itineraries (when logged in)**: Lists all routes created by you (both private and public).
* **Public Itineraries**: Browse routes published publicly by other travelers.
* **Viewing a Tour**: Clicking on any tour opens the detailed view showing:
  * An **Interactive Leaflet Map** with numbered pins and animated flow polylines displaying the direction of travel.
  * A step-by-step list of stops with individual segment distances.
* **Editing a Tour (when logged in)**: Click edit on a tour you own to modify:
  * **Name**: Change the tour name.
  * **Visibility**: Toggle between *Public* and *Private*.
  * **Order of Stops**: Rearrange the stops manually, or lock/unlock specific stops at fixed indexes.
  * **Add New Steps**: Select more places to append to your tour.
  * **Re-optimize Route**: Request the optimizer to recalculate the shortest route after modifying the steps.
  * **Hotel layovers constraint**: Adjust the maximum distance parameter to group nearby destinations around hotel hubs (stops serving as hotels are highlighted with a red **H** on the map/itinerary and do not increment numerical step numbers).
