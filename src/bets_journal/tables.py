from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sq

Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    username = sq.Column(sq.Text, index=True, unique=True)
    email = sq.Column(sq.Text, unique=True )
    hashed_password =sq.Column(sq.Text, unique=True)


class Bet(Base):
    __tablename__ = "bets"

    id = sq.Column(sq.Integer, primary_key=True)
    date = sq.Column(sq.DATE, index=True)
    coefficient = sq.Column(sq.FLOAT)
    sum = sq.Column(sq.FLOAT)
    result = sq.Column(sq.Text)
    win_sum = sq.Column(sq.FLOAT)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"))
