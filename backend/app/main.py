from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import (
    auth,
    alerts,
    incidents,
    playbooks,
    dashboard,
    simulation,
    webhooks,
    indicators,
    assets,
    automation,
    cases,
    notifications,
    audit,
    approvals,
    health,
    reports,
    search
)

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SentinelFlow Enterprise Security Orchestration, Automation & Response (SOAR) Platform"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(playbooks.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(indicators.router, prefix="/api")
app.include_router(assets.router, prefix="/api")
app.include_router(automation.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    # Automatically seed default users & initial playbooks if database is freshly created
    try:
        from app.database import SessionLocal
        from app.models.user import User
        from app.seed import seed_database
        
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        
        if user_count == 0:
            print("No existing users found. Auto-seeding initial SOAR platform data...")
            seed_database()
    except Exception as e:
        print(f"Startup check/seed warning: {e}")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }
