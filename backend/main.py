from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before application starts)
    print("Server started. Routes:")
    for route in app.routes:
        print(f"Route: {route.path}, Methods: {getattr(route, 'methods', ['WebSocket'])}")
    yield
    # Shutdown code (runs when application is shutting down)
    print("Server shutting down")

app = FastAPI(title="Drone Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router)

@app.get("/")
async def root():
    return {"message": "Drone Dashboard API"}

@app.get("/health")
async def health_check():
    print("Health check endpoint called") 
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)