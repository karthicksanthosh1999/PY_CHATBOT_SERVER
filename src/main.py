from fastapi import FastAPI

from src.database.database import Base, engine
from src.routers.chat_route import router as chat_router

app = FastAPI(
    title="ChatBot",
    description="Developed By JK-Industries",
    version="0.0.1"
)

Base.metadata.create_all(bind=engine)

app.include_router(chat_router)

@app.get("/")
def home():
    return {
        "message" : "Welcome to the ChatBot api session"
    }
