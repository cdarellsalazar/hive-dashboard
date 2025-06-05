from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import telemetry

app = FastAPI(title="Drone Dashboard API")

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
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)