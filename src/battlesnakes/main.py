from snake import info, move, end, start
from fastapi import FastAPI, APIRouter

api = FastAPI(
    title="Battlesnake Webhook Handler",
    description="Webhook endpoints called by Battlesnakes.com to play the game",
)
api_router = APIRouter()
api_router.get("/")(info)
api_router.post("/start")(start)
api_router.post("/move")(move)
api_router.post("/end")(end)
api.include_router(api_router)
