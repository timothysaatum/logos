from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import routers (create these as needed)
# from app.api.endpoints import auth, users, data

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Logos System API",
    openapi_url=f"{settings.API_PREFIX}/docs" if settings.ENVIRONMENT != "production" else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
# app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": settings.SYSTEM_STATUS,
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }