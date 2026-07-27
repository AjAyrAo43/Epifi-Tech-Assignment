from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import urls
from .scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Start background ping scheduler
    start_scheduler()
    yield
    # Shutdown scheduler cleanly
    stop_scheduler()


app = FastAPI(
    title="Uptime Monitor API",
    description="Full-stack Uptime Monitoring Backend Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware allowing frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls.router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}
