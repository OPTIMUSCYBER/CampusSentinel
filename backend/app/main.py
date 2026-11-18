from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CampusSentinel API Prototype",
    version="0.1.0"
)

# CORS Configuration
# Note: This is configured for local dev. It needs tightening before any real deployment.
# Testing on other devices over home wifi requires binding the server to 0.0.0.0 and allowing the LAN origin.
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.api.v1 import devices, labs, admin, agent

app.include_router(labs.router, prefix="/api/v1/labs", tags=["Labs"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": f"{settings.PROJECT_NAME} API is running"}
