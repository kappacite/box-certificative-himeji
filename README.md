# 🌍 Travel Planner — Dynamic Route Optimizer

Travel Planner is a complete web application designed to help travelers plan, organize, and optimize their itineraries. The platform features an advanced routing engine that solves the **Traveling Salesperson Problem (TSP)** with support for fixed/locked stops and structured hotel layovers, presenting an interactive animated route map.

The project is structured as a decoupled application:
* 🛠️ **Backend API**: Flask (Python 3.11) with SQLite (SQLAlchemy) and Google OR-Tools routing solver.
* 💻 **Frontend SPA**: Vue 3 (Composition API), Pinia (Setup Stores), Vue Router 4, and Leaflet Maps.

---

## ✨ Key Features

* **🧠 Smart TSP Solver**: Calculates the shortest route linking places using the Haversine formula and the Google OR-Tools routing algorithm under a 3-second constraint.
* **🔒 Fixed-Position Constraints (Locks)**: Allows users to lock specific stops (e.g., a booked museum visit at a fixed hour) and re-optimize the remaining stops around them.
* **🏨 Clustered Hotel layovers**: Groups intermediate stops around elected hotel hubs based on a maximum custom coverage radius to generate optimal back-and-forth round-trips.
* **🗺️ Animated Interactive Maps**: Renders route stops on an interactive Leaflet map featuring animated flow polylines that illustrate the direction of the journey.
* **📍 Place Management**: Manage your private places and create public interest points. Includes live coordinates resolution using Nominatim Geocoding API.
* **👥 Public Sharing**: Toggle tour visibility (private or public) and share optimized paths with others via secure sharing tokens.
* **🚀 One-Click Startup**: Cross-platform startup scripts automatically initialize databases, install dependencies, seed initial landmarks, and launch the application.

---

## 🏗️ Project Architecture & Structure

```
.
├── backend/                       # Flask REST API Server
│   ├── dao/                       # SQLAlchemy models & database access objects
│   ├── dataobject/                # Pure Python DTO dataclasses
│   ├── docs/                      # Backend Technical Documentation & API Ref
│   │   └── TECHNICAL_DOCUMENTATION.md
│   ├── routes/                    # API endpoints & controller Blueprints
│   ├── scripts/                   # Migration & database seeding utilities
│   ├── services/                  # Business logic services & TSP Optimizer
│   └── tests/                     # Pytest suite (unit & integration)
│
├── himeji-planner/                # Vue 3 SPA Client
│   ├── docs/                      # Frontend Technical Documentation
│   │   └── TECHNICAL_DOCUMENTATION.md
│   ├── public/                    # Static assets
│   └── src/
│       ├── api/                   # HTTP client endpoints (Axios)
│       ├── components/            # Scoped UI elements & modal forms
│       ├── composables/           # Stateful logic wrappers
│       ├── router/                # Navigation guards & page routes
│       ├── stores/                # Global states management (Pinia)
│       └── views/                 # Route-level page layouts
│
├── run.sh                         # Linux / macOS automated startup script
└── run.bat                        # Windows automated startup script
```

---

## ⚡ Quick Start (Cross-Platform Startup)

To start the entire application (both frontend and backend) locally, use the provided automated startup scripts.

### 📋 Prerequisites
Ensure you have the following installed on your machine:
* **Python** (version 3.10 or higher)
* **Node.js** (version 18 or higher) & **npm**

### 🚀 Running the App

* **Linux / macOS**:
  1. Open a terminal at the project root.
  2. Run the script:
     ```bash
     ./run.sh
     ```
  3. Close or press `Ctrl+C` to stop all processes cleanly.

* **Windows**:
  1. Open a Command Prompt or PowerShell window at the project root, or simply double-click the file:
     ```cmd
     run.bat
     ```
  2. Two separate console windows will open to let you monitor frontend and backend logs independently. Close them to stop the services.

> [!NOTE]
> On the first launch, the scripts will automatically build a Python virtual environment, install node/python dependencies, and **seed the database** with 200 public landmarks in France via the `seed_places.py` utility.

---

## 🛠️ Local Environment Configurations

Configure environment variables by creating a `.env` file inside the `backend/` directory:

```env
APP_ENV=development
SECRET_KEY=change-this-to-a-secure-secret-in-production
DATABASE_PATH=backend/data/travel.db
```

* **Backend Dev API**: [http://localhost:5000](http://localhost:5000) (Health check: [http://localhost:5000/api/health](http://localhost:5000/api/health))
* **Frontend Dev Server**: [http://localhost:5173](http://localhost:5173)

---

## 📖 Deep-Dive Technical Documentation

For more granular details on algorithms, database design, SOLID principles compliance, state stores, and component models, please refer to the specific documentation files:

* 📄 **[Backend Technical Documentation](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md)**: Detail on TSP solver, set cover heuristics, Haversine computations, and SQLite persistence.
* 📄 **[Frontend Technical Documentation](file:///home/robyn/Documents/Programmation/box-certificative-himeji/himeji-planner/docs/TECHNICAL_DOCUMENTATION.md)**: Detail on drag-and-drop mechanics, Pinia stores layout, and Vue navigation guards.
* 📄 **[REST API Reference](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/api_documentation.md)**: Comprehensive endpoints list and JSON payload structures.
