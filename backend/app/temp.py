from fastapi import FastAPI
from app.api.v1.routes import router

app = FastAPI()

app.include_router(router)

print("FastAPI app loaded")
