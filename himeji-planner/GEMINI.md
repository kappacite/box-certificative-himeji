# AGENTS.md — Travel Planner Frontend
> Front-end specification for AI agents and contributors.
> Stack: Vue 3 · Composition API · Pinia · Vue Router · Axios

---

## Project Overview

This document defines the architecture, conventions, and rules for the **Travel Planner** front-end SPA.  
The app consumes the Flask REST API and provides a UI to authenticate, manage places, generate optimized tours, and share results.

---

## Package Structure

```
frontend/
├── index.html
├── vite.config.js
├── package.json
├── .env                        # VITE_API_BASE_URL=http://localhost:5000/api
├── .env.example
│
└── src/
    ├── main.js                 # App entry point — mounts Vue, registers plugins
    ├── App.vue                 # Root component, <RouterView> + global layout
    │
    ├── api/                    # All HTTP communication — one file per resource
    │   ├── client.js           # Axios instance + interceptors (auth header, errors)
    │   ├── authApi.js          # login(), register(), logout()
    │   ├── placesApi.js        # getPlaces(), createPlace(), updatePlace(), deletePlace()
    │   └── toursApi.js         # getTours(), createTour(), deleteTour(), shareTour(), getShared()
    │
    ├── stores/                 # Pinia stores — global reactive state
    │   ├── authStore.js        # currentUser, token, isAuthenticated, login/logout actions
    │   ├── placesStore.js      # places[], loading, error — CRUD actions
    │   └── toursStore.js       # tours[], activeTour, loading, error — CRUD + share actions
    │
    ├── router/
    │   └── index.js            # Vue Router — routes + navigation guards
    │
    ├── views/                  # Page-level components, one per route
    │   ├── LoginView.vue
    │   ├── RegisterView.vue
    │   ├── DashboardView.vue   # List of user's tours
    │   ├── PlacesView.vue      # Manage the place list
    │   ├── TourView.vue        # Display a generated tour + share controls
    │   └── SharedTourView.vue  # Public page — no auth required
    │
    ├── components/             # Reusable UI components
    │   ├── layout/
    │   │   ├── AppNavbar.vue
    │   │   └── AppFooter.vue
    │   ├── auth/
    │   │   └── AuthForm.vue
    │   ├── places/
    │   │   ├── PlaceList.vue
    │   │   ├── PlaceCard.vue
    │   │   └── PlaceSearchInput.vue  # Calls API, shows suggestions
    │   ├── tours/
    │   │   ├── TourList.vue
    │   │   ├── TourMap.vue           # Visual representation of the tour route
    │   │   └── ShareControls.vue     # Toggle visibility + copy share link
    │   └── ui/                       # Generic, stateless primitives
    │       ├── BaseButton.vue
    │       ├── BaseInput.vue
    │       ├── BaseModal.vue
    │       ├── BaseSpinner.vue
    │       └── AlertBanner.vue       # Displays error / success messages
    │
    ├── composables/            # Reusable stateful logic (Vue 3 Composition API)
    │   ├── useAuth.js          # Wraps authStore — login, logout, redirect logic
    │   ├── usePlaces.js        # Wraps placesStore — CRUD with loading/error state
    │   └── useTours.js         # Wraps toursStore — generate, share, copy link
    │
    └── utils/
        ├── formatters.js       # Distance formatting, date formatting
        └── validators.js       # Input validation helpers (email, non-empty, etc.)
```

---

## Layered Architecture — Rules

```
views / components
       ↓
  composables          ← coordinate store + API calls + local UI state
       ↓
    stores             ← reactive global state (Pinia)
       ↓
    api/               ← HTTP calls via Axios, returns raw data or throws
```

| Layer | Responsibility | Forbidden |
|---|---|---|
| `views` | Route-level layout, compose components | Direct API calls, business logic |
| `components` | UI rendering, emit events upward | Pinia store access (prefer composables) |
| `composables` | Combine store + api + local state | Rendering, template logic |
| `stores` | Hold and mutate global state | API calls (delegate to composables) |
| `api/` | HTTP requests only, error normalization | State mutation, routing |

> **One-way data flow**: data flows down via props, events flow up via `emit`. Never mutate props.

---

## API Layer (`src/api/`)

### `client.js` — Axios instance

This is the **single entry point** for all HTTP calls. All other api files import from here.

```js
// src/api/client.js
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import router from '@/router'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach JWT
client.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor — normalize errors
client.interceptors.response.use(
  (response) => response.data,          // unwrap .data automatically
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      useAuthStore().logout()
      router.push({ name: 'login' })
    }

    // Normalize to a consistent error shape
    const message = error.response?.data?.message ?? 'Unexpected error'
    const code    = error.response?.data?.code    ?? 'UNKNOWN_ERROR'
    return Promise.reject({ status, message, code })
  }
)

export default client
```

### Resource files (one per back-end resource)

```js
// src/api/toursApi.js
import client from './client'

export const toursApi = {
  getAll:     ()           => client.get('/tours'),
  getById:    (id)         => client.get(`/tours/${id}`),
  create:     (placeIds)   => client.post('/tours', { place_ids: placeIds }),
  remove:     (id)         => client.delete(`/tours/${id}`),
  setShare:   (id, level)  => client.patch(`/tours/${id}/share`, { visibility: level }),
  getShared:  (token)      => client.get(`/tours/shared/${token}`),
}
```

**Rules:**
- Api files only call `client`. No `axios` imports elsewhere.
- Never catch errors inside api files — let them propagate to composables.
- Never access the Pinia store from api files.

---

## Pinia Stores (`src/stores/`)

Each store follows the **Setup Store** syntax (Vue 3 idiomatic).

```js
// src/stores/toursStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useToursStore = defineStore('tours', () => {
  const tours   = ref([])
  const loading = ref(false)
  const error   = ref(null)  // { message: string, code: string } | null

  function setError(err) {
    error.value = err ?? null
  }

  function clearError() {
    error.value = null
  }

  return { tours, loading, error, setError, clearError }
})
```

**Rules:**
- Stores hold **state only** — no direct API calls.
- `error` is always `null` (no error) or `{ message, code }` (never a raw Error object).
- `loading` must be reset in `finally` blocks — never left `true` on error.

---

## Composables (`src/composables/`)

Composables are where **coordination** happens: they call the api, update the store, and expose ready-to-use reactive refs to components.

```js
// src/composables/useTours.js
import { toursApi } from '@/api/toursApi'
import { useToursStore } from '@/stores/toursStore'
import { storeToRefs } from 'pinia'

export function useTours() {
  const store = useToursStore()
  const { tours, loading, error } = storeToRefs(store)

  async function generateTour(placeIds) {
    store.clearError()
    store.loading = true
    try {
      const newTour = await toursApi.create(placeIds)
      store.tours.push(newTour.data)
      return newTour.data
    } catch (err) {
      store.setError(err)        // { message, code } from client.js
      return null
    } finally {
      store.loading = false
    }
  }

  async function shareTour(id, visibility) { /* same pattern */ }

  return { tours, loading, error, generateTour, shareTour }
}
```

**Pattern for every async action:**

```
clearError()  →  loading = true  →  try { api call + store mutation }
              →  catch { store.setError(err) }  →  finally { loading = false }
```

---

## Error Handling Strategy

Errors are **normalized at the Axios interceptor** and flow up through composables to the UI.

### Mapping to user-facing messages

```js
// src/utils/formatters.js
const ERROR_MESSAGES = {
  NOT_FOUND:        'This resource no longer exists.',
  FORBIDDEN:        'You do not have access to this.',
  VALIDATION_ERROR: 'Please check your input.',
  UNKNOWN_ERROR:    'Something went wrong. Please try again.',
}

export function friendlyError(code) {
  return ERROR_MESSAGES[code] ?? ERROR_MESSAGES.UNKNOWN_ERROR
}
```

### Displaying errors in components

Use the `AlertBanner` component — never use `alert()` or `console.error` in production code.

```vue
<!-- In any view or component -->
<AlertBanner v-if="error" type="error" :message="friendlyError(error.code)" />
<BaseSpinner v-if="loading" />
```

### Error scenarios to handle

| Scenario | HTTP Code | Expected UI behaviour |
|---|---|---|
| Invalid credentials | 401 | Show error message on login form |
| Token expired | 401 | Auto-logout + redirect to `/login` |
| Resource not found | 404 | Show inline message, do not crash |
| Validation error | 400 | Show field-level or banner error |
| Forbidden action | 403 | Show "access denied" message |
| Network timeout | — | Show "Check your connection" banner |
| Server crash | 500 | Show generic error banner |

---

## Router (`src/router/index.js`)

```js
const routes = [
  { path: '/',                 redirect: '/dashboard' },
  { path: '/login',            name: 'login',       component: LoginView },
  { path: '/register',         name: 'register',    component: RegisterView },
  { path: '/dashboard',        name: 'dashboard',   component: DashboardView,   meta: { requiresAuth: true } },
  { path: '/places',           name: 'places',      component: PlacesView,      meta: { requiresAuth: true } },
  { path: '/tours/:id',        name: 'tour',        component: TourView,        meta: { requiresAuth: true } },
  { path: '/shared/:token',    name: 'shared-tour', component: SharedTourView }, // public
  { path: '/:pathMatch(.*)*',  name: 'not-found',   component: NotFoundView },
]
```

### Navigation Guard

```js
router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```

- After login, redirect to `query.redirect` if present, otherwise `/dashboard`.
- Guests landing on `/shared/:token` must reach the page without being redirected to login.

---

## Auth Store — Token Persistence

```js
// src/stores/authStore.js
export const useAuthStore = defineStore('auth', () => {
  const token   = ref(localStorage.getItem('token') ?? null)
  const user    = ref(JSON.parse(localStorage.getItem('user') ?? 'null'))

  const isAuthenticated = computed(() => !!token.value)

  function login(payload) {
    token.value = payload.token
    user.value  = payload.user
    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.user))
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAuthenticated, login, logout }
})
```

- JWT is stored in `localStorage` for SPA session persistence.
- `logout()` is called automatically by the Axios interceptor on any `401`.

---

## Component Conventions

### Props & Emits — always typed

```vue
<script setup>
const props = defineProps({
  tour: { type: Object, required: true },
})
const emit = defineEmits(['delete', 'share'])
</script>
```

### Loading & Error state — always handled

Every component that triggers an async action must show:
1. A `<BaseSpinner>` while `loading === true`
2. An `<AlertBanner>` when `error !== null`
3. Empty state (`<p>No tours yet.</p>`) when the list is empty

### No logic in templates

Keep `<template>` free of business logic. Extract conditions to `computed` properties.

```vue
<!-- ❌ Bad -->
<p v-if="tours.length === 0 && !loading && !error">No tours yet.</p>

<!-- ✅ Good -->
<p v-if="isEmpty">No tours yet.</p>
<!-- in <script setup>: const isEmpty = computed(() => !loading.value && !error.value && tours.value.length === 0) -->
```

---

## Environment Variables

```
# .env
VITE_API_BASE_URL=http://localhost:5000/api

# .env.example  (committed to git)
VITE_API_BASE_URL=http://localhost:5000/api
```

- Prefix all custom variables with `VITE_` for Vite to expose them to the client bundle.
- `.env` is in `.gitignore`. `.env.example` is committed.
- Never hardcode any URL or secret in source files.

---

## Coding Standards

- Language: **English only** — all code, comments, component names, store names.
- **Composition API** (`<script setup>`) exclusively — no Options API.
- Component file names: **PascalCase** (`TourCard.vue`). Route files: **PascalCase + View suffix** (`TourView.vue`).
- Composable names: **camelCase prefixed with `use`** (`useTours.js`).
- No direct DOM manipulation — use Vue refs (`useTemplateRef`).
- No `console.log` in committed code.

---

## Suggested Tooling

| Purpose | Library |
|---|---|
| Framework | Vue 3 (Composition API) |
| Build tool | Vite |
| State management | Pinia |
| Routing | Vue Router 4 |
| HTTP client | Axios |
| CSS | Tailwind CSS or plain scoped CSS |
| Map display (bonus) | Leaflet + vue-leaflet |
| Form validation | VeeValidate or manual utils |
| Testing | Vitest + Vue Test Utils |
