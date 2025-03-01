from fastapi import FastAPI
from app.routers.stock import router as stock_router

app = FastAPI()

app.include_router(stock_router)