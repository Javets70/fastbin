from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql import text

from app.core.config import get_settings
from app.core.database import engine, get_db
from app.models import User, Paste

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    print("Database connection established")

    yield

    # Shutdown
    print("Closing database connections...")
    await engine.dispose()
    print("Application shutdown complete")


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


# Database test endpoint
@app.get("/api/v1/health")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "app": settings.APP_NAME}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/static-health")
async def static_health_check(request: Request):
    return templates.TemplateResponse(request, "base.html", {})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
