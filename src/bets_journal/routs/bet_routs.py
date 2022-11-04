from typing import Optional

from fastapi import APIRouter, Depends

from bets_journal.schemas.authenticate_schemas import UserDB
from bets_journal.schemas.bet_schemas import BetBase, BetPost, BetDB, Result, TimeAgo, time_dict
from bets_journal.services.auth_service import oauth2_schema, get_current_user
from bets_journal.services.bet_service import BetService

bets_router = APIRouter(
    prefix='/bets',
)


@bets_router.get("/{id}", response_model=BetDB)
def get_bet_by_id(
        id:int,
        user:UserDB = Depends(get_current_user),
        service:BetService = Depends()
    ):
    return service.get_bet_by_id(id=id, user_id=user.id)



@bets_router.post("/", response_model=BetDB)
def create_bet_note(
        data: BetPost,
        service: BetService=Depends(),
        user: UserDB = Depends(get_current_user)
        ):
    return service.create_bet(data, user_id=user.id)


@bets_router.get('/filters/', response_model=dict)
def get_list_bets_filters(
        service: BetService = Depends(),
        user: UserDB = Depends(get_current_user),
        result: Optional[Result] = None,
        time_ago: Optional[TimeAgo] = None,
        sum_low: int | None = None,
        sum_high: int | None = None,
        coefficient_high: float | None = None,
        coefficient_low: float | None = None

):
    bets=service.get_filtred_bets(
        user_id=user.id,
        result=result,
        coefficient_high=coefficient_high,
        coefficient_low=coefficient_low,
        sum_low=sum_low,
        sum_high=sum_high,
        time_ago= time_dict.get(time_ago)
        )
    balance = service.get_balance(bets)

    return {"bets":bets, "balance": balance}