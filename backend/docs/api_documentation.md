# 📖 Public API Guide & Route Manual — Travel Planner

Welcome to the **Travel Planner REST API** manual. This public guide provides developers and API consumers with everything they need to integrate, query, and command our route optimization engine. 

---

## 🚀 Getting Started

All requests to the Travel Planner API are served in JSON format. The default base URL for local development is:
`http://localhost:5000/api`

### 🔑 Authentication Header
Most actions (managing private places, planning tours) require authenticating via a **JSON Web Token (JWT)**.
1. Obtain a token by calling `/api/auth/register` or `/api/auth/login`.
2. Include the token in the headers of all subsequent requests:
   ```http
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

## 🗺️ Quick Reference Table

| Module | Method | Endpoint | Auth? | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Authentication** | `POST` | `/api/auth/register` | ❌ | Create a new traveler account |
| | `POST` | `/api/auth/login` | ❌ | Authenticate and obtain JWT token |
| | `POST` | `/api/auth/logout` | 🔑 | Revoke session & blacklist JWT token |
| | `GET` | `/api/auth/me` | 🔑 | Get current user's profile and session info |
| **Places** | `GET` | `/api/places` | 🔑/❌| List visible places (with search `q` / `visibility`) |
| | `POST` | `/api/places` | 🔑 | Add a new place (resolves coordinates via Nominatim if needed) |
| | `GET` | `/api/places/search` | ❌ | Geocode place name search query without saving (GET `?q=`) |
| | `POST` | `/api/places/geocode` | ❌ | Geocode place name query without saving (POST JSON) |
| | `GET` | `/api/places/public` | ❌ | List all public places (global directory) |
| | `GET` | `/api/places/public/<id>` | ❌ | Get details of a public place (no auth required) |
| | `GET` | `/api/places/<id>` | 🔑/❌| Get details of a specific place |
| | `PUT` | `/api/places/<id>` | 🔑 | Full update of a place (owner only) |
| | `PATCH` | `/api/places/<id>` | 🔑 | Partial update of a place (owner only) |
| | `DELETE` | `/api/places/<id>` | 🔑 | Delete a place (owner only) |
| **Tours** | `GET` | `/api/tours` | 🔑 | List your private and public tours |
| | `POST` | `/api/tours` | 🔑 | Create a new tour (triggers TSP solver) |
| | `POST` | `/api/tours/preview` | 🔑 | Optimize a list of places and returns route preview without saving |
| | `GET` | `/api/tours/<id>` | 🔑 | Get details of a specific tour (owner only) |
| | `PATCH` | `/api/tours/<id>` | 🔑 | Update tour properties/stops (owner only) |
| | `DELETE` | `/api/tours/<id>` | 🔑 | Delete a tour (owner only) |
| | `PATCH` | `/api/tours/<id>/share` | 🔑 | Toggle visibility level (public/private) |
| | `GET` | `/api/tours/public` | ❌ | Browse public tours by other users |
| | `GET` | `/api/tours/shared/<token>` | ❌ | Public access to a shared tour via token |
| | `POST` | `/api/tours/<id>/recalculate` | 🔑 | Force recalculation of an existing tour (owner only) |
| | `POST` | `/api/tours/optimize` | 🔑 | Optimize a list of places and returns raw sequence and distance |
| **Health Checks** | `GET` | `/api/health` | ❌ | General health check for service runtime |
| | `GET` | `/api/health/ready` | ❌ | Database connection readiness check |

---

## 🚦 HTTP Status Codes

The Travel Planner API uses standard HTTP response codes to indicate the success or failure of requests:

| Code | Status | Meaning |
| :--- | :--- | :--- |
| **`200 OK`** | Success | Request succeeded and data is returned. |
| **`201 Created`** | Success | Entity (user, place, tour) was successfully created. |
| **`204 No Content`** | Success | Request succeeded and no body is returned (e.g. on DELETE). |
| **`400 Bad Request`** | Error | Missing parameters, validation failure, or bad JSON format. |
| **`401 Unauthorized`** | Error | Missing token, invalid token, or expired session. |
| **`403 Forbidden`** | Error | You do not own the resource you are trying to modify or delete. |
| **`404 Not Found`** | Error | The requested place, tour, or user does not exist. |
| **`409 Conflict`** | Error | Resource conflict (e.g., trying to register an email already in use). |
| **`500 Internal Error`**| Error | Server crashed or Nominatim geocoding failed. Check logs. |

---

## 🔐 1. Authentication Layer (`/api/auth/*`)

### Register Account
* **URL**: `/api/auth/register`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "username": "traveler1",
    "email": "traveler@example.com",
    "password": "securepassword123"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "status": "success",
    "data": {
      "user": {
        "id": 2,
        "username": "traveler1",
        "email": "traveler@example.com"
      }
    }
  }
  ```

### Log In
* **URL**: `/api/auth/login`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "email": "traveler@example.com",
    "password": "securepassword123"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 2,
        "username": "traveler1",
        "email": "traveler@example.com"
      }
    }
  }
  ```

### Log Out
* **URL**: `/api/auth/logout`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "message": "Logged out successfully"
    }
  }
  ```

### Get My Session Profile (`/me`)
Retrieves the logged-in user profile from the active JWT token.
* **URL**: `/api/auth/me`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "user": {
        "id": 2,
        "username": "traveler1",
        "email": "traveler@example.com"
      }
    }
  }
  ```

---

## 📍 2. Places Management (`/api/places/*`)

Places are landmarks with geographical coordinates. If coordinates (`latitude`/`longitude`) are omitted, the API automatically geocodes the place name using the Nominatim API.

### Add a Place
* **URL**: `/api/places`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "name": "Château de Versailles",
    "city": "Versailles",
    "latitude": 48.8049,
    "longitude": 2.1204,
    "visibility": "public"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "status": "success",
    "data": {
      "place": {
        "id": 35,
        "name": "Château de Versailles, Versailles",
        "city": "Versailles",
        "latitude": 48.8049,
        "longitude": 2.1204,
        "owner_id": 2,
        "visibility": "public"
      }
    }
  }
  ```

### List Visible Places
Lists places based on optional visibility and search filters.
* **URL**: `/api/places`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token>` (Optional)
* **Query Parameters**:
  * `visibility`: `private` (default, requires auth) or `public`.
  * `q`: Filter string for search match.
  * `page` / `limit`: Pagination integers.
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "places": [
        {
          "id": 42,
          "name": "Mon Hôtel Favori, Paris",
          "city": "Paris",
          "latitude": 48.8566,
          "longitude": 2.3522,
          "owner_id": 2,
          "visibility": "private"
        }
      ]
    }
  }
  ```

### Search Places (Geocoding GET)
Geocodes a query string without persisting the landmark.
* **URL**: `/api/places/search?q=Tour Eiffel`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "latitude": 48.8584,
      "longitude": 2.2945,
      "city": "Paris"
    }
  }
  ```

### Search Places (Geocoding POST)
Geocodes a query string sent in a JSON body.
* **URL**: `/api/places/geocode`
* **Method**: `POST`
* **Payload**:
  ```json
  {
    "name": "Musée du Louvre"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "latitude": 48.8606,
      "longitude": 2.3376,
      "city": "Paris"
    }
  }
  ```

### Browse Public Places
Lists all public places.
* **URL**: `/api/places/public`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "places": [
        {
          "id": 1,
          "name": "Tour Eiffel, Paris",
          "latitude": 48.8584,
          "longitude": 2.2945,
          "owner_id": 1,
          "visibility": "public"
        }
      ]
    }
  }
  ```

### Get Public Place Details
* **URL**: `/api/places/public/<place_id>`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "place": {
        "id": 1,
        "name": "Tour Eiffel, Paris",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "owner_id": 1,
        "visibility": "public"
      }
    }
  }
  ```

### Get Specific Place Details
* **URL**: `/api/places/<place_id>`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token>` (Optional)
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "place": {
        "id": 42,
        "name": "Mon Hôtel Favori, Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": 2,
        "visibility": "private"
      }
    }
  }
  ```

### Full Update of a Place
* **URL**: `/api/places/<place_id>`
* **Method**: `PUT`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "name": "Château de Versailles Renommé",
    "city": "Versailles",
    "latitude": 48.8049,
    "longitude": 2.1204,
    "visibility": "private"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "place": {
        "id": 35,
        "name": "Château de Versailles Renommé, Versailles",
        "city": "Versailles",
        "latitude": 48.8049,
        "longitude": 2.1204,
        "owner_id": 2,
        "visibility": "private"
      }
    }
  }
  ```

### Partial Update of a Place
* **URL**: `/api/places/<place_id>`
* **Method**: `PATCH`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "visibility": "public"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "place": {
        "id": 35,
        "name": "Château de Versailles Renommé, Versailles",
        "city": "Versailles",
        "latitude": 48.8049,
        "longitude": 2.1204,
        "owner_id": 2,
        "visibility": "public"
      }
    }
  }
  ```

### Delete a Place
* **URL**: `/api/places/<place_id>`
* **Method**: `DELETE`
* **Headers**: `Authorization: Bearer <token>`
* **Response (204 No Content)**: *(Empty body)*

---

## 🧠 3. Tour Optimization & Planning (`/api/tours/*`)

Tours link places together. When generating a tour, the optimizer sorts the list of place IDs into the shortest route possible.

### Create and Optimize a Tour
* **URL**: `/api/tours`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "name": "My Paris Adventure",
    "place_ids": [1, 5, 8],
    "visibility": "private",
    "max_distance": 25.0
  }
  ```
  * `place_ids`: Array of places to visit. The first place is always the start/end point.
  * `max_distance` (Optional): If set (in km), enables hotel routing. The solver automatically elects hotel stops and generates round-trips from them.

* **Response (201 Created)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My Paris Adventure",
        "owner_id": 2,
        "visibility": "private",
        "share_token": "a1b2c3d4e5f6g7h8",
        "total_distance": 18.42,
        "max_distance": 25.0,
        "places": [
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false },
          { "id": 5, "name": "Louvre Museum", "is_hotel": false, "locked": false },
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false }
        ]
      }
    }
  }
  ```

### Preview Route (No Saving)
Runs the TSP optimizer and returns the calculated sequence of stops without persisting the tour in the database.
* **URL**: `/api/tours/preview`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "place_ids": [1, 5, 8],
    "locked_positions": {
      "5": 1
    },
    "max_distance": 0.0
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": null,
        "name": "Preview",
        "owner_id": 2,
        "visibility": "private",
        "share_token": "",
        "total_distance": 12.18,
        "max_distance": 0.0,
        "places": [
          { "id": 1, "name": "Hôtel de Ville, Paris", "is_hotel": false, "locked": false },
          { "id": 5, "name": "Louvre Museum, Paris", "is_hotel": false, "locked": true },
          { "id": 8, "name": "Notre Dame, Paris", "is_hotel": false, "locked": false },
          { "id": 1, "name": "Hôtel de Ville, Paris", "is_hotel": false, "locked": false }
        ]
      }
    }
  }
  ```

### List My Tours
* **URL**: `/api/tours`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tours": [
        {
          "id": 14,
          "name": "My Paris Adventure",
          "owner_id": 2,
          "visibility": "private",
          "share_token": "a1b2c3d4e5f6g7h8",
          "total_distance": 18.42
        }
      ]
    }
  }
  ```

### Get Specific Tour Details
Retrieves full details of a specific tour owned by the user, including all its ordered stops.
* **URL**: `/api/tours/<tour_id>`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My Paris Adventure",
        "owner_id": 2,
        "visibility": "private",
        "share_token": "a1b2c3d4e5f6g7h8",
        "total_distance": 18.42,
        "max_distance": 25.0,
        "places": [
          {
            "id": 1,
            "name": "Hôtel de Ville, Paris",
            "city": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": 2,
            "visibility": "private",
            "locked": false,
            "is_hotel": true
          },
          {
            "id": 5,
            "name": "Louvre Museum, Paris",
            "city": "Paris",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "owner_id": 2,
            "visibility": "private",
            "locked": false,
            "is_hotel": false
          },
          {
            "id": 1,
            "name": "Hôtel de Ville, Paris",
            "city": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": 2,
            "visibility": "private",
            "locked": false,
            "is_hotel": true
          }
        ]
      }
    }
  }
  ```

### Update Tour (Manual Re-ordering or Re-optimization)
* **URL**: `/api/tours/<tour_id>`
* **Method**: `PATCH`
* **Headers**: `Authorization: Bearer <token>`
* **Payload (Manual Save)**:
  ```json
  {
    "name": "My New Paris Title",
    "place_ids": [1, 8, 5, 1],
    "optimize": false
  }
  ```
* **Payload (Re-run Solver with Fixed Locks)**:
  ```json
  {
    "place_ids": [1, 5, 8, 1],
    "locked_positions": {
      "8": 2
    },
    "optimize": true
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My New Paris Title",
        "owner_id": 2,
        "visibility": "private",
        "share_token": "a1b2c3d4e5f6g7h8",
        "total_distance": 18.42,
        "max_distance": 25.0,
        "places": [
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false },
          { "id": 5, "name": "Louvre Museum", "is_hotel": false, "locked": false },
          { "id": 8, "name": "Notre Dame", "is_hotel": false, "locked": true },
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false }
        ]
      }
    }
  }
  ```

### Delete a Tour
Deletes a specific tour owned by the user.
* **URL**: `/api/tours/<tour_id>`
* **Method**: `DELETE`
* **Headers**: `Authorization: Bearer <token>`
* **Response (204 No Content)**: *(Empty body)*

### Toggle Sharing Visibility
* **URL**: `/api/tours/<tour_id>/share`
* **Method**: `PATCH`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "visibility": "public"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My Paris Adventure",
        "visibility": "public",
        "share_token": "a1b2c3d4e5f6g7h8"
      }
    }
  }
  ```

### Get Public Tours list
* **URL**: `/api/tours/public`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tours": [
        {
          "id": 9,
          "name": "Historic Paris Route",
          "owner_id": 1,
          "visibility": "public",
          "total_distance": 8.12
        }
      ]
    }
  }
  ```

### Get Shared Tour Details (Public Link)
Allows any guest user to retrieve the full stops list and path of a tour using its sharing token.
* **URL**: `/api/tours/shared/<share_token>`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My Paris Adventure",
        "visibility": "public",
        "total_distance": 18.42,
        "places": [
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false },
          { "id": 5, "name": "Louvre Museum", "is_hotel": false, "locked": false },
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false }
        ]
      }
    }
  }
  ```

### Force Recalculate Existing Tour
* **URL**: `/api/tours/<tour_id>/recalculate`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "tour": {
        "id": 14,
        "name": "My Paris Adventure",
        "owner_id": 2,
        "visibility": "private",
        "share_token": "a1b2c3d4e5f6g7h8",
        "total_distance": 17.84,
        "max_distance": 25.0,
        "places": [
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false },
          { "id": 5, "name": "Louvre Museum", "is_hotel": false, "locked": false },
          { "id": 1, "name": "Hôtel de Ville", "is_hotel": true, "locked": false }
        ]
      }
    }
  }
  ```

### Optimize Place Sequence (No Saving)
Runs the core algorithm to optimize a list of place IDs and returns the sorted sequence of places and total distance directly.
* **URL**: `/api/tours/optimize`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token>`
* **Payload**:
  ```json
  {
    "place_ids": [1, 5, 8],
    "locked_positions": {
      "5": 1
    },
    "max_distance": 0.0
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "total_distance": 12.18,
      "places": [
        {
          "id": 1,
          "name": "Hôtel de Ville, Paris",
          "city": "Paris",
          "latitude": 48.8566,
          "longitude": 2.3522,
          "owner_id": 2,
          "visibility": "private",
          "locked": false,
          "is_hotel": false
        },
        {
          "id": 5,
          "name": "Louvre Museum, Paris",
          "city": "Paris",
          "latitude": 48.8606,
          "longitude": 2.3376,
          "owner_id": 2,
          "visibility": "private",
          "locked": true,
          "is_hotel": false
        },
        {
          "id": 8,
          "name": "Notre Dame, Paris",
          "city": "Paris",
          "latitude": 48.8529,
          "longitude": 2.3500,
          "owner_id": 2,
          "visibility": "private",
          "locked": false,
          "is_hotel": false
        },
        {
          "id": 1,
          "name": "Hôtel de Ville, Paris",
          "city": "Paris",
          "latitude": 48.8566,
          "longitude": 2.3522,
          "owner_id": 2,
          "visibility": "private",
          "locked": false,
          "is_hotel": false
        }
      ]
    }
  }
  ```

---

## 🏥 4. System Health Checks (`/api/health*`)

These endpoints provide service health and database availability checks. They do not require authentication and are suitable for uptime monitoring, deployment checks, or container orchestration health probes (e.g., Kubernetes liveness/readiness).

### Service Health Status
Checks if the application server is running and accepting HTTP requests.
* **URL**: `/api/health`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "message": "Service is healthy"
    }
  }
  ```

### Database Readiness Status
Checks both the application server and its database connection to verify if queries can be successfully executed.
* **URL**: `/api/health/ready`
* **Method**: `GET`
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "message": "Database and service are ready"
    }
  }
  ```
* **Response (500 Internal Server Error)**:
  Returned if the database is unreachable, locked, or failing to respond.
  ```json
  {
    "status": "error",
    "message": "Database is not ready: <error_message_details>",
    "code": "DATABASE_ERROR"
  }
  ```

---

## 🛠️ Step-by-Step Developer Workflow

To test the full API workflow using tools like Curl or Postman, follow this sequence:

```mermaid
graph LR
    Reg["1. POST /auth/register"] --> Log["2. POST /auth/login<br>(Get Token)"]
    Log --> Add["3. POST /places<br>(Add stops)"]
    Add --> Plan["4. POST /tours<br>(Optimize Route)"]
    Plan --> Share["5. PATCH /tours/:id/share<br>(Make Public)"]
```

### 1. Register & Login
Create your session:
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"devuser","email":"dev@example.com","password":"mypassword"}'

# Login to get JWT
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"mypassword"}'
```
Save the returned token: `export JWT="<YOUR_TOKEN>"`

### 2. Save a few Locations
```bash
# Save Eiffel Tower (will geocode coordinates automatically)
curl -X POST http://localhost:5000/api/places \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"name":"Tour Eiffel", "city":"Paris", "visibility":"public"}'
```

### 3. Generate and Fetch the Optimal Path
```bash
# Optimize tour connecting places
curl -X POST http://localhost:5000/api/tours \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"name":"Paris Trip", "place_ids":[1, 2, 3], "visibility":"public"}'
```

---

## ❌ Error Code Reference

When an error occurs, the API returns a structured object containing a human-readable `message` and an exact `code` to allow programmatic error mapping on client sides:

| Error Code | HTTP Status | Meaning | Resolution |
| :--- | :--- | :--- | :--- |
| `VALIDATION_ERROR` | 400 | Data parameters failed model validation check. | Ensure email format is valid, pseudo is non-empty, and password has min 6 chars. |
| `UNAUTHORIZED` | 401 | Missing or invalid Authorization Bearer token. | Prompt the user to log in again. Set valid headers. |
| `FORBIDDEN` | 403 | Attempt to edit or delete another user's place/tour. | Verify ownership before performing mutations. |
| `NOT_FOUND` | 404 | The requested entity ID does not exist in SQLite database. | Verify the target ID parameters in the URL path. |
| `CONFLICT_ERROR` | 409 | Duplicate resource (e.g. email already registered). | Choose a different email address or request password recovery. |
| `DATABASE_ERROR` | 500 | Database connection timeout or SQLite lock occurred. | Verify database write volume permissions or retry request. |
