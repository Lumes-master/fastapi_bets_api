from typing import Optional
from datetime import date
from fastapi import Depends, HTTPException


from bets_journal import tables
from bets_journal.database import get_db, Session

from bets_journal.schemas.bet_schemas import  BetPost, Result

from bets_journal.tables import Bet


class BetService:

    @classmethod
    def get_balance(cls, bets: list[Bet] | None = None)->float:
        if not bets:
            return 0
        balance = 0
        for bet in bets:
            balance += (bet.win_sum - bet.sum)

        return balance

    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def _get_bet_by_id(self, id:int, user_id: int)->tables.Bet:
        bet = self.session.query(tables.Bet).filter_by(id=id, user_id=user_id).first()
        if not bet:
            raise HTTPException(
                status_code=404,
                detail="bet is not found"
            )
        return bet

    def get_bet_by_id(self, id:int, user_id: int):
        return self._get_bet_by_id(id=id, user_id=user_id)

    def create_bet(self, data:BetPost, user_id:int)->tables.Bet:
        data_dict = data.dict()
        bet = tables.Bet(**data_dict, user_id=user_id)
        self.session.add(bet)
        self.session.commit()
        self.session.refresh(bet)
        user = self.session.query(tables.User).filter_by(user_id=user_id).first()
        user.balanse = user.balanse + data.win_sum - data.sum
        self.session.save(user)
        return bet


    def get_filtred_bets(
            self,
            user_id: int,
            result: Optional[Result] = None,
            sum_low: int | None = None,
            sum_high: int | None = None,
            coefficient_high: float | None = None,
            coefficient_low: float | None =None,
            time_ago: date | None = None
                                     )->list[Bet]:
        query = self.session.query(tables.Bet).\
            filter(tables.Bet.user_id==user_id)
        if result:
            query = query.filter(tables.Bet.result==result)
        if sum_low:
            query = query.filter(tables.Bet.sum>=sum_low)
        if sum_high:
            query = query.filter(tables.Bet.sum<=sum_high)
        if coefficient_low:
            query = query.filter(tables.Bet.coefficient>=coefficient_low)
        if coefficient_high:
            query=query.filter(tables.Bet.coefficient <=coefficient_high)
        if time_ago:
            query = query.filter(tables.Bet.date >= time_ago)

        return query.all()