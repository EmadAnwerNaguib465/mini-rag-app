from fastapi import FastAPI
from routes import base ,data
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings


app = FastAPI()
@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_conn= AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client = app.mongodb_conn[settings.MONGO_DB_NAME]

async def shutdown_db_client():
    app.mongodb_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

