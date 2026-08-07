from app.api.routes import router
from fastapi import FastAPI

app = FastAPI(title="Pata Geocoding API")
app.include_router(router)
