# Backend — Uptime Monitor API

FastAPI backend with SQLite storage and APScheduler engine.

## Local Setup (Standalone)

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate environment:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Linux/macOS: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Access interactive API documentation at `http://localhost:8000/docs`.
