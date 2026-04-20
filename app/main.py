from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.inbound.controllers.api_controller import router as api_router
from app.adapters.inbound.controllers.simulation_controller import router as simulation_router
from app.adapters.inbound.controllers.auth_controller import router as auth_router
<<<<<<< Updated upstream
=======
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
>>>>>>> Stashed changes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to db
    MongoDB.connect_db()
    yield
    # Shutdown: close db
    MongoDB.close_db()

app = FastAPI(
    title="API Mockup System",
    description="A hexagonal architecture API Mockup data generator and simulator.",
    lifespan=lifespan,
    docs_url="/swagger"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API Mockup Service is running", "docs": "/docs"}

# 1. Register logic/utility routes first
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(api_router, prefix="/api/v1", tags=["API Mock Management"])

# 2. Finally, register simulation wildcard last (it must be the very last one)
app.include_router(simulation_router, tags=["Simulation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
