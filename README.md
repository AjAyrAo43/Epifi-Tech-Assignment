# PulseGuard — Real-Time Full-Stack Uptime Monitor MVP

A lightweight, high-performance, full-stack uptime monitoring system built with Python (FastAPI + SQLAlchemy + APScheduler), React (Vite + Glassmorphism UI), SQLite, and Docker Compose.

---

## ⚡ 1-Line Setup

Launch the full-stack ecosystem (backend API, automated scheduler, and frontend dashboard) locally with a single command:

```bash
docker compose up --build
```

- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Healthcheck**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Testing Steps & System Verification

Follow these steps to verify healthy and degraded status tracking:

1. **Start the application**: Run `docker compose up --build` and open [http://localhost:5173](http://localhost:5173) in your browser.
2. **Test Healthy Endpoint (UP State)**:
   - Enter `https://example.com` into the *Register New Endpoint* field and click **Add Monitor**.
   - **Expected Result**: The endpoint immediately checks upon registration and displays a green **`UP`** badge with HTTP status code `200` and a response latency (e.g., `~120 ms`).
3. **Test Unreachable Endpoint (DOWN State)**:
   - Enter an invalid or non-existent URL, such as `https://invalid-domain-xyz-999.com` and click **Add Monitor**.
   - **Expected Result**: The system handles DNS/timeout failure gracefully and displays a red **`DOWN`** badge with HTTP Code `None (Failed)`.
4. **Inspect Check History**:
   - Click the history icon (🕒) next to any monitored target to open the modal and inspect individual ping history records with timestamps and status metrics.
5. **Auto-Polling Verification**:
   - Leave the browser open; the dashboard polls backend status every 5 seconds without requiring page reloads.

---

## 🏗️ Architecture Overview

The system follows a clean modular layout:

```text
├── /backend
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, lifespan scheduler boot
│   │   ├── database.py      # SQLAlchemy SQLite engine & session management
│   │   ├── models.py        # URL & Check ORM schemas with cascade deletes
│   │   ├── schemas.py       # Pydantic request/response schemas & URL validator
│   │   ├── scheduler.py     # Async HTTP pinger (httpx) & APScheduler job
│   │   └── routers/urls.py  # REST API endpoints (/api/urls, /api/urls/:id/checks)
│   ├── requirements.txt
│   └── Dockerfile
├── /frontend
│   ├── src/
│   │   ├── App.jsx          # Dashboard layout & 5s interval polling loop
│   │   ├── api.js           # API fetch wrapper
│   │   ├── components/      # Navbar, StatsOverview, AddUrlForm, UrlList, CheckHistoryModal
│   │   └── index.css        # Custom glassmorphism dark theme & pulse animations
│   ├── nginx.conf           # Production NGINX reverse-proxy configuration
│   └── Dockerfile
├── /deploy
│   └── main.tf              # Illustrative Terraform IaC cloud deployment sketch
├── docker-compose.yml       # Multi-container orchestration & persistent volume
├── AI_LOG.md                # Detailed AI collaboration log
├── AGENT.md                 # Agent execution session roadmap
└── PLAN.md                  # System design specification
```

For full technical specifications, refer to [`PLAN.md`](PLAN.md).

---

## ☁️ Deployment Sketch (Infrastructure-as-Code)

To host this MVP on a cloud provider (e.g., AWS), the recommended topology comprises:

- **Frontend**: Vite static bundle hosted on **AWS S3** served globally via **AWS CloudFront CDN** with HTTPS.
- **Backend API & Pinger**: Containerized FastAPI service running on **AWS ECS Fargate** behind an **Application Load Balancer (ALB)**.
- **Persistence**: SQLite database mounted on an **AWS EFS (Elastic File System)** volume shared across task restarts.
- **Scale Out Path**: For higher scale (>1,000s of monitored URLs), transition database persistence from SQLite to **AWS RDS PostgreSQL** and decouple pinger jobs to an AWS SQS + Lambda / Celery worker queue.

An illustrative Terraform configuration is provided in [`deploy/main.tf`](deploy/main.tf).

---

## 🤖 AI Collaboration Log

Detailed documentation of AI tools used, raw prompt interactions, and real debugging course corrections is available in [`AI_LOG.md`](AI_LOG.md).
