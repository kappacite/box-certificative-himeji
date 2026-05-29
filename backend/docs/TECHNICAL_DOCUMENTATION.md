# Technical Documentation — Travel Planner Backend API

This document provides a comprehensive technical overview of the backend REST API for the **Travel Planner** application. It details the layered architecture, design patterns, SOLID principles conformance, Traveling Salesperson Problem (TSP) optimization engine, and testing strategy.

---

## 🏛️ System Architecture

The backend is built as a modular **Layered Architecture** using Flask (Python 3.11) and Flask-SQLAlchemy (SQLite). Each layer has a strict boundary of responsibility, promoting testability, maintainability, and clean separation of concerns.

```mermaid
graph TD
    Client["Client (Frontend Vue 3 SPA)"]
    
    subgraph "Backend API Layer"
        Routes["API Controllers (routes/)"]
        Middleware["Middlewares & Auth (middleware/)"]
        Exceptions["Error Handling (exceptions/)"]
    end
    
    subgraph "Business Logic Layer"
        Services["Business Services (services/)"]
        Algorithms["Core Algorithms (services/algorithm/)"]
    end
    
    subgraph "Data Access Layer (DAO)"
        DAO["DAO Objects (dao/)"]
        Models["SQLAlchemy Models (dao/models.py)"]
        DO["Data Objects (dataobject/)"]
    end
    
    Database[(SQLite Database /app/data/travel.db)]

    %% Connections
    Client <-->|HTTP REST / JSON| Routes
    Routes --> Middleware
    Routes --> Exceptions
    Routes --> Services
    Services --> Algorithms
    Services --> DAO
    DAO --> Models
    DAO --> DO
    Models <--> Database
    
    classDef layerStyle fill:#f8fafc,stroke:#e2e8f0,stroke-width:2px;
    class Routes,Services,DAO layerStyle;
```

### Architectural Layers

| Layer | Directories | Responsibility | Rules & Boundaries |
| :--- | :--- | :--- | :--- |
| **API / Presentation** | `routes/`<br>`middleware/`<br>`exceptions/` | Processes HTTP requests, deserializes JSON, handles JWT auth, handles routing, and formats responses / errors. | Forbidden to write database queries or raw algorithm logic here. Delegates to **Services**. |
| **Business Logic** | `services/`<br>`services/algorithm/` | Core business logic, coordinate multiple database updates, interface with Nominatim Geocoding, and execute TSP optimizations. | Autonomously orchestrates data flows. Interacts with the database only through **DAOs**. |
| **Data Access (DAO)** | `dao/`<br>`dataobject/` | Defines tables and schemas via SQLAlchemy models. Maps database records to pure Python Data Transfer Objects (DTOs) for the service layer. | Zero knowledge of HTTP. No business validation or network communication. |

---

## 🛠️ SOLID Principles Conformance Audit

The codebase was designed to adhere closely to object-oriented software engineering best practices.

### 1. Single Responsibility Principle (SRP)
Each module has one reason to change:
* **`config.py`** and **`app.py`** configure environment variables and orchestrate initializations, completely decoupled from runtime request processing.
* **`dataobject/`** contains pure Python dataclasses mapping directly to domains.
* **`services/algorithm/distance.py`** performs raw Haversine computations without dependency on network or persistence.
* **`services/algorithm/optimizer.py`** solves the Traveling Salesperson Problem and does not interact with HTTP requests.

### 2. Open/Closed Principle (OCP)
The system is open for extension but closed for modification:
* **Configuration Classes**: `Config` serves as a base class. Environment configurations (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`) extend it without mutating the parent behavior.
* **TSP Optimizer**: The optimization interface exposes `optimize(places, locked_positions)`. Supporting fixed/locked stops was implemented within the solver without breaking existing signatures or endpoint contracts in the services layer.

### 3. Liskov Substitution Principle (LSP)
Abstractions are interchangeable:
* The generic base DAO (`BaseDAO`) implements generic CRUD workflows (`get_by_id`, `create`, `update`, `delete`). Specialized DAOs (`UserDAO`, `PlaceDAO`, `TourDAO`) subclass it and are substituted transparently in services.

### 4. Interface Segregation Principle (ISP)
Interfaces are lightweight and highly specialized:
* Flask blueprints isolate route groups (`auth_bp`, `place_bp`, `tour_bp`) to prevent routes from importing or depending on unrelated controllers.
* Services expose exact methods corresponding to specific client use cases rather than exposing a broad, unsegregated state.

### 5. Dependency Inversion Principle (DIP)
Dependencies are injected rather than instantiated in-place:
* Services receive their corresponding DAOs via constructor injection, enabling seamless unit testing with mocked databases:
  ```python
  def __init__(self, user_dao: UserDAO = None):
      self.user_dao = user_dao or UserDAO()
  ```

---

## 🧠 Core Optimization Engine (TSP Solver)

The core feature of the Travel Planner is finding the optimal ordering of places to visit. This is mapped to the **Traveling Salesperson Problem (TSP)** with custom constraints.

```mermaid
graph TD
    Start["Request Optimization"] --> Extract["Extract Stops & Lock Positions"]
    Extract --> Decouple{"Any Locked Positions?"}
    
    Decouple -->|Yes| Split["1. Remove locked stops from list<br>2. Build a sub-tour of unlocked stops"]
    Decouple -->|No| SubTour["Optimize all stops directly"]
    
    Split --> SubTour
    SubTour --> Solver["Run Google OR-Tools Solver<br>(Local Search Heuristic, Time Limit: 3s)"]
    
    Solver --> CheckLock{"Any Locked Stops?"}
    CheckLock -->|Yes| Merge["Re-insert locked stops at their fixed indices"]
    CheckLock -->|No| Output["Format optimized Tour object"]
    
    Merge --> Output
    Output --> Return["Return Ordered Stops & Total Distance"]
```

### Haversine Distance Formula
To construct the cost matrix for the routing solver, we compute the exact distance between latitude and longitude coordinates on a sphere using the Haversine formula:

$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

Where:
* $\phi_1, \phi_2$ are latitudes in radians.
* $\lambda_1, \lambda_2$ are longitudes in radians.
* $r$ is the Earth's radius (6371 km).

#### Floating-point Safety Correction
In Python, rounding errors on identical points can produce value inputs to `math.acos` or `math.asin` slightly greater than `1.0` (e.g. `1.0000000002`), which crashes with a `ValueError: math domain error`. The solver explicitly bounds the input value before computations:
```python
# Bounded cosine value to prevent mathematical exceptions
cos_val = max(-1.0, min(1.0, cos_val))
```

### Google OR-Tools Routing Engine
The optimizer uses **Google OR-Tools**' routing solver.
* **First Solution Strategy**: Path cheapest arc (greedy starting path).
* **Local Search Metaheuristic**: Guided Local Search (GLS) or Tabu Search to escape local minima.
* **Time limit**: Constrained to a maximum of 3 seconds to guarantee prompt HTTP responses.

### Hybrid Fixed-Index (Lock) Insertion
To allow travelers to freeze/lock specific stops (e.g. reserving a museum at 2:00 PM), the optimizer runs a hybrid pipeline:
1. **Decoupling**: Locked stops are extracted from the list.
2. **Sub-tour Optimization**: OR-Tools calculates the optimal route sequence for the remaining unlocked stops.
3. **Linear Insertion**: Locked stops are re-inserted into the optimized sequence at their exact user-specified indexes. If multiple locks overlap, they are placed sequentially to maintain relative positions without breaking the sub-tour optimality.

---

## 🗄️ Database Schema & Persistence

The application uses SQLite as its default storage engine, configured for robustness and concurrency.

### Schema Relationships

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string email
        string password_hash
    }
    PLACES {
        int id PK
        string name
        float latitude
        float longitude
        string visibility
        int owner_id FK
        string city
    }
    TOURS {
        int id PK
        string name
        string visibility
        string share_token
        int owner_id FK
        float total_distance
        float max_distance
    }
    TOUR_PLACES {
        int tour_id PK, FK
        int place_id PK, FK
        int position
    }
    REVOKED_TOKENS {
        int id PK
        string token
        datetime blacklisted_at
    }

    USERS ||--o{ PLACES : "owns"
    USERS ||--o{ TOURS : "owns"
    TOURS ||--|{ TOUR_PLACES : "has"
    PLACES ||--|{ TOUR_PLACES : "belongs_to"
```

### Database Optimization & Local Persistence
* **Indices**: Index fields like `tours.share_token` and `places.owner_id` are indexed to speed up authorization and lookup checks.
* **Local Persistence**: The database file `travel.db` is stored inside the local filesystem (as defined by the `DATABASE_PATH` environment variable) to persist data between runs.

---

## 🧪 Testing & Verification

The backend code is covered by a test suite using `pytest`.

### Test Architecture

* **Isolated Database Config**: Tests use a separate `TestingConfig` pointing to a clean in-memory database (`sqlite:///:memory:`) or a temporary filesystem database.
* **Fixtures**: Initialized inside `conftest.py` to create the schema, mock third-party services (like Nominatim API geocoding), and register a default seed user and JWT token.
* **Teardown**: Database sessions are rolled back and dropped after every test run to ensure strict isolation.

### Running Tests
To run the test suite locally:
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest
```

---

## 🚀 Deployment & Local Execution

### Environment Variables
Configure these variables in a `.env` file at the root of the project:

```env
APP_ENV=development
SECRET_KEY=use-a-strong-random-key-in-production
DATABASE_PATH=backend/data/travel.db
```

### Launching the Application
Cross-platform startup scripts are provided at the root of the project to automatically set up virtual environments, install dependencies, seed the database, and launch both services in parallel.

* **Linux / macOS**:
  ```bash
  ./run.sh
  ```
* **Windows**:
  Double-click or run from command prompt:
  ```cmd
  run.bat
  ```

### Automated Startup Workflow
The scripts automate the complete local setup and execution pipeline:

1. **Python Virtual Environment (`.venv`)**:
   * Checks the `backend/` directory for an existing virtual environment.
   * Creates one automatically using `python3 -m venv .venv` (Linux/macOS) or `python -m venv .venv` (Windows) if not found.
2. **Dependency Management**:
   * Installs Python packages from `backend/requirements.txt` inside the virtual environment.
   * Runs `npm install` in `himeji-planner/` to fetch Node.js packages for the frontend SPA.
3. **Database Setup & Seeding**:
   * Runs the `seed_places.py` script. The database file (`travel.db`) is automatically initialized and loaded with 200 public landmarks in France. It skips already-existing places to avoid duplicate rows on subsequent launches.
4. **Parallel Process Orchestration**:
   * **Linux/macOS (`run.sh`)**: Starts the Flask API (port 5000) and Vite SPA (port 5173) as background processes. A trap listener captures `Ctrl+C` (SIGINT/SIGTERM) to kill both processes cleanly at exit.
   * **Windows (`run.bat`)**: Spawns two separate terminal windows (`start cmd /c`) for the frontend and backend, enabling independent logs view and lifecycle management.
