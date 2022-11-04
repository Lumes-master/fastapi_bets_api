from fastapi import FastAPI
from routs import router as bets_router
app = FastAPI()
app.include_router(bets_router)