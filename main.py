from datetime import datetime
from fastapi import FastAPI
import uvicorn
from routes import currency_router
from xml.etree import ElementTree as ET
from contextlib import asynccontextmanager
from database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("База готова")
    yield


app = FastAPI(lifespan=lifespan, docs_url="/swagger_ui", redoc_url="/redoc")
app.include_router(currency_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
