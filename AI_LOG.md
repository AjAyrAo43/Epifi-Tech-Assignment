# Dedicated AI Collaboration Log (`AI_LOG.md`)

This log documents the AI-assisted engineering process used to design, build, containerize, and test the **PulseGuard Uptime Monitor MVP**.

---

## 1. AI Tech Stack

- **AI Coding Agent**: Antigravity AI Assistant (Google DeepMind Agentic Coding Framework)
- **Underlying Model**: Gemini 3.6 Flash (High)
- **IDE & Tooling**: Antigravity Agentic IDE with integrated terminal execution, workspace file mutation, and structural planning artifacts.

---

## 2. The Prompts That Shipped It

### Prompt 1: Backend Core Scaffolding (Data Layer & Pinger Engine)
> *"Build a FastAPI backend with SQLAlchemy (SQLite) for storing URLs and check history. Use httpx (async) with a bounded 5s timeout to ping registered URLs. Handle failure modes (timeouts, DNS failures, connection errors) gracefully so that checks log `is_up: False` and `status_code: None` without throwing exceptions. Integrate APScheduler (`AsyncIOScheduler`) to run checks automatically every 60 seconds, and trigger an immediate ping upon URL registration so the UI doesn't sit at 'PENDING'."*

### Prompt 2: Frontend Dashboard (React + Vite + Glassmorphism Styling)
> *"Scaffold a React + Vite dashboard in `/frontend`. Build a modern dark glassmorphism interface using Vanilla CSS (`index.css`) with status pills (green glow UP badge, red pulse DOWN badge, gray PENDING badge), latency metrics in monospace, relative check timestamps, and overview stat cards. Implement live polling (`setInterval`) every 5 seconds to fetch `GET /api/urls` with automatic unmount cleanup and inline error boundaries."*

### Prompt 3: Containerization & Deployment Topology
> *"Create a `docker-compose.yml` orchestrating `backend` (Python 3.12-slim) and `frontend` (multi-stage Node build + NGINX static server). Configure named volumes for SQLite persistence across restarts, API healthchecks on `/api/health`, and include an illustrative Terraform configuration in `deploy/main.tf` mapping an AWS ECS Fargate + CloudFront/S3 + EFS architecture."*

---

## 3. Course Corrections & Debugging Log

### Course Correction 1: Initial Pending State Delay on New URL Registration
- **Issue**: Originally, when a user added a new URL via `POST /api/urls`, the record was created in the database without an initial check record. The dashboard displayed `is_up: null` ("PENDING") for up to 60 seconds until the next scheduled APScheduler tick.
- **Root Cause**: Check execution was decoupled entirely into the periodic background job without triggering a synchronous check during request lifecycle.
- **Fix**: Refactored `check_url_instance` in `scheduler.py` into a reusable async function and invoked it directly inside `POST /api/urls` handler prior to returning the API response. Newly added URLs now transition instantly to UP or DOWN.

### Course Correction 2: APScheduler Event Loop & AsyncIO Integration
- **Issue**: Attempting to run synchronous SQLAlchemy DB sessions inside an async APScheduler job caused event loop blocking and concurrency warnings under load.
- **Root Cause**: Mixing synchronous DB sessions inside `asyncio.gather` tasks without proper session isolation.
- **Fix**: Modified `run_all_checks()` to instantiate a scoped `SessionLocal()` DB instance inside the async task worker and explicitly close connections in `finally:` blocks.

### Course Correction 3: NGINX CORS & API Route Forwarding in Containerized Environment
- **Issue**: When running under `docker-compose`, the frontend container attempting to call `/api/urls` faced relative URL routing failures or CORS issues when pointing directly to `localhost:8000`.
- **Root Cause**: Different hostname contexts between browser client and internal container networking.
- **Fix**: Configured `frontend/nginx.conf` with a `location /api/` reverse-proxy directive forwarding requests to `http://backend:8000/api/` inside the Docker bridge network.
