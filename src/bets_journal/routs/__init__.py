from fastapi import APIRouter

from bets_journal.routs.bet_routs import bets_router
from bets_journal.routs.authenticate_routs import router as auth_router
router = APIRouter()
router.include_router(bets_router)
router.include_router(auth_router)