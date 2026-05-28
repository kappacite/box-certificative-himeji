# AGENTS.md — Travel Planner API
> Back-end specification for AI agents and contributors.
> Stack: Python 3.11+ · Flask · REST · JWT

---

## Project Overview

This document defines the architecture, conventions, and rules for the **Travel Planner** back-end API.  
The goal is to generate an optimal tour (TSP-like problem) across a list of user-defined places, exposed via a RESTful Flask API.

---

## Package Structure

```
backend/
├── app.py                  # App factory (create_app)
├── config.py               # Configuration classes (Dev, Prod, Test)
├── requirements.txt
│
├── dataobject/             # Pure data models — no logic, no DB access
│   ├── __init__.py
│   ├── user.py             # User dataclass / schema
│   ├── place.py            # Place dataclass (lat, lon, name…)
│   └── tour.py             # Tour dataclass (ordered list of Places + total distance)
│
├── dao/                    # Data Access Objects — only DB/persistence logic
│   ├── __init__.py
│   ├── base_dao.py         # Abstract base DAO (CRUD interface)
│   ├── user_dao.py
│   ├── place_dao.py
│   └── tour_dao.py
│
├── services/               # Business logic — orchestrates DAOs and algorithms
│   ├── __init__.py
│   ├── auth_service.py     # Registration, login, JWT generation/validation
│   ├── place_service.py    # Geocoding API calls, place management
│   ├── tour_service.py     # Tour generation, distance calculation, sharing logic
│   └── algorithm/
│       ├── __init__.py
│       ├── distance.py     # Haversine formula (exact spec from subject)
│       └── optimizer.py    # TSP heuristic (e.g. nearest-neighbour + 2-opt)
│
├── routes/                 # Flask Blueprints — HTTP layer only, no business logic
│   ├── __init__.py
│   ├── auth_routes.py      # /api/auth/*
│   ├── place_routes.py     # /api/places/*
│   └── tour_routes.py      # /api/tours/*
│
├── middleware/             # Cross-cutting concerns
│   ├── __init__.py
│   ├── auth_middleware.py  # JWT decode + inject current_user
│   └── error_handler.py    # Global error → JSON response mapping
│
├── exceptions/             # Custom exception classes
│   ├── __init__.py
│   ├── auth_exceptions.py  # UnauthorizedException, ForbiddenException…
│   └── app_exceptions.py   # NotFoundException, ValidationException…
│
└── tests/
    ├── unit/
    │   ├── test_distance.py
    │   ├── test_optimizer.py
    │   └── test_auth_service.py
    └── integration/
        ├── test_auth_routes.py
        ├── test_place_routes.py
        └── test_tour_routes.py
```

---

## Layered Architecture — Rules

```
routes  →  services  →  dao  →  DB
               ↕
          dataobject (shared across all layers)
          algorithm  (called exclusively from services)
```

| Layer | Responsibility | Forbidden |
|---|---|---|
| `routes` | Parse request, validate input shape, call service, return HTTP response | DB access, business logic |
| `services` | Business rules, orchestration, external API calls | Direct DB queries, HTTP concerns |
| `dao` | SQL/ORM queries, persistence only | Business logic, HTTP concerns |
| `dataobject` | Data containers (dataclasses or Pydantic models) | Any logic or I/O |
| `algorithm` | Pure computation (distance, optimization) | I/O, DB, HTTP |

> **One-way dependency rule**: upper layers may call lower layers, never the reverse.

---

## REST API Conventions

### URL Design

```
/api/auth/register       POST
/api/auth/login          POST
/api/auth/logout         POST
/api/auth/me             GET

/api/places              GET, POST
/api/places/<id>         GET, PUT, PATCH, DELETE
/api/places/search       GET
/api/places/geocode      POST

/api/tours               GET, POST
/api/tours/<id>          GET, PATCH, DELETE
/api/tours/preview       POST
/api/tours/<id>/share    PATCH
/api/tours/shared/<token> GET    ← public access, no auth required
```

### HTTP Status Codes

| Situation | Code |
|---|---|
| Successful GET / read | `200 OK` |
| Successful creation (POST) | `201 Created` |
| Successful update with no body | `204 No Content` |
| Bad request / validation error | `400 Bad Request` |
| Missing or invalid JWT | `401 Unauthorized` |
| Valid auth but insufficient rights | `403 Forbidden` |
| Resource not found | `404 Not Found` |
| Unhandled server error | `500 Internal Server Error` |

### Response Envelope

All responses use a consistent JSON structure:

```json
// Success
{
  "status": "success",
  "data": { ... }
}

// Error
{
  "status": "error",
  "message": "Human-readable description",
  "code": "SNAKE_CASE_ERROR_CODE"
}
```

---

## Authentication & Authorization

- Use **JWT** (PyJWT library). Store only `user_id` and `exp` in the token payload.
- Tokens are sent via `Authorization: Bearer <token>` header.
- `auth_middleware.py` exposes a `@require_auth` decorator injecting `g.current_user`.
- A second decorator `@require_owner(resource)` checks that `current_user.id == resource.owner_id` — use it on all `PUT`/`DELETE`/`PATCH` routes.
- Passwords are hashed with **bcrypt** (never store plaintext).
- Token expiry: 24h for access token. Refresh tokens are optional (bonus).

```python
# Usage in routes
@tour_bp.route("/<int:tour_id>", methods=["DELETE"])
@require_auth
def delete_tour(tour_id):
    tour_service.delete(tour_id, owner_id=g.current_user.id)
    return jsonify({"status": "success"}), 204
```

---

## Algorithm Package

### Distance Formula (from subject specification)

```python
import math

R_EARTH = 6378.197
PI = 3.141592

def to_rad(deg: float) -> float:
    return deg * (PI / 180.0)

def haversine(place_a, place_b) -> float:
    """Returns great-circle distance in km between two Places."""
    lat_a, lon_a = to_rad(place_a.latitude), to_rad(place_a.longitude)
    lat_b, lon_b = to_rad(place_b.latitude), to_rad(place_b.longitude)
    return R_EARTH * math.acos(
        math.sin(lat_a) * math.sin(lat_b)
        + math.cos(lat_a) * math.cos(lat_b) * math.cos(lon_b - lon_a)
    )
```

### Optimizer

Implement at minimum a **Nearest Neighbour heuristic** followed by a **2-opt local search** pass. This clearly exceeds a naive/random solution and is explainable in the oral defence.

```
1. Nearest Neighbour  →  O(n²)  →  builds an initial tour greedily
2. 2-opt              →  O(n²)  →  iteratively reverses segments to reduce total distance
```

The `optimizer.py` module must expose a single entry point:

```python
def optimize(places: list[Place]) -> list[Place]:
    """Returns an ordered list of Places representing the optimal tour."""
```

---

## Tour Sharing

A tour has a `visibility` field: `"private"` | `"public"`.

- `private`: route `/api/tours/<id>` requires `@require_auth` + owner check.
- `public`: route `/api/tours/shared/<share_token>` is open, no auth needed.

`share_token` is a UUID generated at creation time, stored alongside the tour. It is the only key needed for public access — never expose internal `id` on the public endpoint.

---

## External API — Geocoding

Use the **OpenStreetMap Nominatim** API (free, no key required) to resolve place names to coordinates.

```
GET https://nominatim.openstreetmap.org/search?q=<name>&format=json&limit=1
```

This call lives exclusively in `place_service.py`. Never call external APIs from routes or DAOs.

---

## Configuration (`config.py`)

```python
class Config:
    SECRET_KEY: str          # JWT signing key — load from env var, never hardcode
    DATABASE_URI: str        # SQLite for dev, easily swappable for prod
    GEOCODING_API_URL: str
    TOKEN_EXPIRY_HOURS: int = 24

class DevelopmentConfig(Config): ...
class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = "sqlite:///:memory:"
class ProductionConfig(Config): ...
```

Load the right config via the `APP_ENV` environment variable in `create_app()`.

---

## Error Handling

All exceptions must be caught by `error_handler.py` and returned as the standard JSON envelope. Never let a stack trace reach the client.

```python
# exceptions/app_exceptions.py
class NotFoundException(Exception):
    status_code = 404
    code = "NOT_FOUND"

class ForbiddenException(Exception):
    status_code = 403
    code = "FORBIDDEN"
```

---

## Testing

- Use **pytest** + **Flask test client**.
- Unit tests for: `distance.py`, `optimizer.py`, `auth_service.py` (password hash, token generation).
- Integration tests for: at minimum one happy path + one error path per route group.
- Run tests with `pytest tests/ -v`.

---

## Coding Standards

- Language: **English only** — all code, comments, docstrings, commit messages.
- Docstrings: **Google style** for all public functions and classes.
- Formatting: **black** + **flake8** (PEP8).
- No magic numbers — use named constants or config values.
- Never commit secrets or API keys — use a `.env` file (add to `.gitignore`).

---

## Git Conventions

```
feat: add 2-opt optimization pass
fix: handle missing coordinates in place creation
docs: update AGENTS.md with sharing endpoints
test: add unit tests for haversine distance
refactor: extract token logic into auth_service
```

Commit after each meaningful unit of work. At minimum one commit per feature, per bug fix, per test suite.

---

## Suggested Tooling

| Purpose | Library |
|---|---|
| HTTP framework | Flask |
| ORM | SQLAlchemy (via Flask-SQLAlchemy) |
| JWT | PyJWT |
| Password hashing | bcrypt |
| Validation | marshmallow or pydantic |
| Testing | pytest + Flask test client |
| Environment variables | python-dotenv |
| Code formatting | black, flake8 |
