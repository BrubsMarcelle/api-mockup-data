from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.adapters.outbound.database.mongodb import MongoDB
from app.adapters.outbound.database.firestore_db import FirestoreDB
from app.adapters.inbound.controllers.api_controller import router as api_router
from app.adapters.inbound.controllers.simulation_controller import router as simulation_router
from app.adapters.inbound.controllers.auth_controller import router as auth_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DATABASE_TYPE == "mongodb":
        MongoDB.connect_db()
    else:
        FirestoreDB.connect_db()
    yield
    if settings.DATABASE_TYPE == "mongodb":
        MongoDB.close_db()
    else:
        await FirestoreDB.close_db()

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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(api_router, prefix="/api/v1", tags=["API Mock Management"])
app.include_router(simulation_router, tags=["Simulation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.RELOAD)