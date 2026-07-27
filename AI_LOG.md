# Dedicated AI Collaboration Log (`AI_LOG.md`)

This log documents the granular, component-level AI prompt engineering and iterative course-correction process used to design, build, containerize, and refine the **PulseGuard Uptime Monitor MVP**.

---

## 1. AI Tech Stack & Agent Environment

- **AI Coding Assistant**: Antigravity AI Assistant (Google DeepMind Agentic Coding Framework)
- **Underlying Model**: Gemini 3.6 Flash (High)
- **Agentic Paradigm**: Pair-programming with real-time workspace mutation, AST verification, ripgrep inspection, and multi-stage execution plan artifacts.

---

## 2. Granular Component-Level Prompting Strategy

### 🏗️ Category A: Data Layer & Schema Architecture

#### Prompt 1.1 — Database ORM Models (`backend/app/models.py`)
> *"Create SQLAlchemy ORM models for an uptime monitoring system in SQLite. Define a `URL` table storing `id`, `name`, `url` (unique, indexed), `created_at`, and an updated timestamp. Define a `Check` table storing `id`, `url_id` (foreign key pointing to `urls.id` with `ondelete='CASCADE'`), `timestamp`, `is_up` (boolean), `status_code` (nullable integer), `response_time_ms` (nullable float), and `error_message` (nullable string). Establish a bidirectional relationship `url.checks` with back-populates."*

#### Prompt 1.2 — Pydantic Request/Response Schemas (`backend/app/schemas.py`)
> *"Define Pydantic v2 schemas for URL creation and response serialization. Implement `URLCreate` validating target URLs via `HttpUrl` or regex, and optional `name`. Implement `CheckResponse` mapping database check records with formatted timestamps. Implement `URLResponse` including nested summary statistics (`last_check`, `total_checks`, `uptime_percentage`, `avg_response_time_ms`) to allow the frontend to render overview cards without client-side recalculation."*

---

### ⚡ Category B: Core Engine & REST API Services

#### Prompt 2.1 — Async HTTPX Pinger & Scheduler (`backend/app/scheduler.py`)
> *"Build an asynchronous pinging module using `httpx.AsyncClient` with a hard 5.0-second timeout. Ensure all network exception types (`httpx.TimeoutException`, `httpx.ConnectError`, `httpx.HTTPError`, socket/DNS errors) are caught gracefully so the background job never crashes. When a check fails, record `is_up=False`, `status_code=None`, and extract a human-readable `error_message`. Integrate APScheduler (`AsyncIOScheduler`) to iterate over all active URLs every 60 seconds, using isolated SQLAlchemy DB sessions (`SessionLocal`) per check iteration."*

#### Prompt 2.2 — FastAPI Endpoints & Instant Registration Ping (`backend/app/main.py`)
> *"Implement FastAPI CRUD endpoints: `POST /api/urls` (add URL), `GET /api/urls` (list all URLs with stats and last check), `GET /api/urls/{id}` (single URL details), `GET /api/urls/{id}/checks` (paginated historical check log), and `DELETE /api/urls/{id}`. On `POST /api/urls`, trigger an immediate async ping task right after insertion so newly registered URLs do not sit at 'PENDING' for up to 60 seconds waiting for the scheduler."*

---

### 🎨 Category C: Frontend UI & Glassmorphism Design System

#### Prompt 3.1 — Modern Glassmorphism Styling System (`frontend/src/index.css`)
> *"Create a dark-mode CSS design system using Vanilla CSS custom properties (`--bg-dark: #0f172a`, `--card-bg: rgba(30, 41, 59, 0.7)`, `--glow-up: #10b981`, `--glow-down: #ef4444`). Implement `backdrop-filter: blur(12px)`, subtle hover elevation, glowing pill badges for UP/DOWN/PENDING status, monospace font styling for latency numbers, and smooth CSS transitions for interactive elements."*

#### Prompt 3.2 — Header & Live System Metrics Overview (`Navbar.jsx`, `StatsOverview.jsx`)
> *"Build a `Navbar` component with a glowing pulse dot indicating active live-polling status. Build a `StatsOverview` component displaying 4 metric cards: Total Monitored Endpoints, Operational (UP), Outages (DOWN), and Average Latency (ms). Compute color accents dynamically (e.g. green accent if 100% UP, amber/red if outages exist)."*

#### Prompt 3.3 — URL Registration Form & Interactive Cards (`AddUrlForm.jsx`, `UrlList.jsx`)
> *"Create an `AddUrlForm` with input validation, protocol auto-prefixing (`http://` / `https://`), and inline loading feedback. Build a `UrlList` grid rendering individual endpoint cards showing target URL, current status pill, latency badge, relative last-checked time (e.g. '12s ago'), 'View History' action button, and a Delete action with confirmation."*

#### Prompt 3.4 — Historical Check Drawer/Modal (`CheckHistoryModal.jsx`)
> *"Build a modal drawer component that pops up when 'View History' is clicked on a URL card. Fetch and display the last 20 ping checks in reverse chronological order in a clean table view. Highlight non-200 HTTP status codes in red badges, format response times, and display truncated error messages if a ping timed out."*

---

### 🐳 Category D: Containerization & Build Troubleshooting

#### Prompt 4.1 — Multi-Stage Containerization & Reverse Proxy (`Dockerfiles` & `nginx.conf`)
> *"Create a multi-stage Dockerfile for `/frontend` compiling Vite static assets with Node 20-Alpine and serving them via NGINX Alpine. Create a backend `Dockerfile` using Python 3.12-slim. Write an `nginx.conf` with a `location /api/` reverse-proxy directive forwarding requests to `http://backend:8000/api/` inside the Docker bridge network to eliminate cross-origin issues."*

#### Prompt 4.2 — Build Debugging & Docker Lockfile Fix
> *"Diagnose and resolve the Docker build failure `#21 RUN npm ci` caused by a missing `package-lock.json` in the `/frontend` directory during `docker compose up --build`. Update `frontend/Dockerfile` to use `RUN npm install` and strip the obsolete `version: '3.8'` attribute from `docker-compose.yml` to adhere to modern Compose specifications."*

---

## 3. Deep-Dive Course Corrections & AI Problem-Solving

### Course Correction 1: Initial Pending State Latency Gap
- **Issue**: Originally, newly added URLs showed `is_up: null` ("PENDING") for up to 60 seconds until the next periodic APScheduler run.
- **Root Cause**: The background worker was fully decoupled from the POST request lifecycle.
- **Fix**: Extracted the single-check ping logic into a reusable function `perform_check_for_url()` and invoked it asynchronously inside the `POST /api/urls` FastAPI route handler before returning the response.

### Course Correction 2: SQLite Async Thread-Safety & Session Leakage
- **Issue**: Running periodic check loops across multiple URLs caused database locking warnings (`sqlite3.OperationalError: database is locked`) when accessing shared SQLAlchemy sessions inside `asyncio.gather()`.
- **Root Cause**: Sharing a single DB session context across concurrent async ping routines.
- **Fix**: Implemented session-per-task scoping in `scheduler.py`, instantiating `SessionLocal()` inside each worker task and wrapping execution in `try...finally: db.close()`.

### Course Correction 3: NGINX Reverse Proxy for Containerized Cross-Origin Traffic
- **Issue**: Frontend container attempted to call `http://localhost:8000/api/urls` directly, failing in production container deployments due to hostname isolation.
- **Root Cause**: Client-side JavaScript running in the browser resolves `localhost` to the host machine rather than the internal container network.
- **Fix**: Configured `frontend/nginx.conf` to proxy `/api/` requests to `http://backend:8000/api/` via NGINX, enabling relative `/api/` requests in client code.

### Course Correction 4: Docker Build Failure (`npm ci` vs `npm install`)
- **Issue**: Running `docker compose up --build` crashed with `npm error The npm ci command can only install with an existing package-lock.json`.
- **Root Cause**: `frontend/Dockerfile` executed `RUN npm ci` without a pre-committed `package-lock.json` file in the source repository.
- **Fix**: Updated `frontend/Dockerfile` to `RUN npm install`, allowing npm to generate dependencies dynamically during image build.

### Course Correction 5: Docker Compose Specification Deprecation Cleanup
- **Issue**: Compose output threw warnings: `attribute 'version' is obsolete, it will be ignored`.
- **Root Cause**: Top-level `version: '3.8'` is deprecated in modern Docker Compose V2 specifications.
- **Fix**: Removed top-level `version` string from [docker-compose.yml](file:///d:/MSC/Assingment/Epifi-Tech-Assignment/docker-compose.yml).
