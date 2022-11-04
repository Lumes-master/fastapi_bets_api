from datetime import date, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel

time_dict = {"today":date.today(),
             "last_week":date.today() + timedelta(days=-7),
             "last_month":date.today() + timedelta(days=-30),
             "last_six_months": date.today() + timedelta(days=-182),
             "last_year": date.today() + timedelta(days=-356)
             }

class TimeAgo(str, Enum):
    LAST_DAY = "today"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_SIX_MONTHS = "last_six_months"
    LAST_YEAR = "last_year"



class Result(str, Enum):
    WIN="WIN"
    LOOSE="LOOSE"

class BetBase(BaseModel):

    date: Optional[date]
    coefficient: float
    sum: float
    result: Result
    win_sum: float


class BetDB(BetBase):

    id:int

    class Config:
        orm_mode = True

class BetPost(BetBase):
    pass