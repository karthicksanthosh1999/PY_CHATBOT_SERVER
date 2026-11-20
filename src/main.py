from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.database import Base, engine
from src.routers.chat_route import router as chat_router
from src.routers.auth_route import router as auth_router

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI(
    title="ChatBot",
    description="Developed By JK-Industries",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message" : "Welcome to the ChatBot api session"
    }
