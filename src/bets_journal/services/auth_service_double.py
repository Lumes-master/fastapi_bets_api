from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta

from bets_journal import tables
from bets_journal.database import get_db, Session
from bets_journal.schemas.authenticate_schemas import UserDB, Token
from bets_journal.settings import settings

oath2_schema = OAuth2PasswordBearer(tokenUrl="/users/sign-in/")

def get_current_user(token: str = Depends(oath2_schema))->UserDB:
    return AuthService.validate_token(token)


class AuthService:

    @classmethod
    def validate_password(cls, raw_password: str, hashed_password: str)->bool:
        return bcrypt.verify(raw_password, hashed_password)


    @classmethod
    def hash_password(cls, raw_password: str)->str:
        return bcrypt.hash(raw_password)


    @classmethod
    def create_token(cls, user: tables.User)->Token:
        user_data = UserDB.from_orm(user)
        now=datetime.utcnow()
        payload = {
            "iat":now,
            "nbf": now,
            "exp": now + timedelta(seconds=settings.jwt_expiration),
            "sub": str(user_data.id),
            "user": user_data.dict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            settings.jwt_algorithm
        )
        return Token(access_token=token)

    @classmethod
    def validate_token(cls, token: str)->UserDB:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate":"Bearer"}

            )
        user_data = payload.get("user")
        try:
            user = UserDB.parse_obj(user_data)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )
        return user

    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def authenticate(self, username: str, password: str)->Token:
        user = self.session.query(tables.User).filter_by(
            username=username,
            hashed_password=self.hash_password(password)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wrong credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        token = self.create_token(user)

        return token

    def delete_users(self):
        users= self.session.query(tables.User).all()
        self.session.delete(users)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
