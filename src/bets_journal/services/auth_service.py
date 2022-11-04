from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Response
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.hash import bcrypt
from random import sample
from string import ascii_letters, digits

from bets_journal.schemas.authenticate_schemas import UserDB, Token, UserPost
from bets_journal.settings import settings
from bets_journal import tables
from bets_journal.database import Session, get_db



oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/sign-in/")


def get_current_user(token: str = Depends(oauth2_schema)):
    return AuthService.validate_token(token)

class AuthService:

    @classmethod
    def create_password(cls)->str:
        new_password="".join(sample(ascii_letters + digits, 8))
        return new_password

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(raw_password, hashed_password)


    @classmethod
    def hash_password(cls, raw_password: str) -> str:
        return bcrypt.hash(raw_password)


    @classmethod
    def create_token(cls, user: tables.User) -> Token:
        user_data = UserDB.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            "exp": now + timedelta(seconds=settings.jwt_expiration),
            "sub": str(user_data.id),
            "user": user_data.dict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return Token(access_token=token)

    @classmethod
    def validate_token(cls, token: str) -> UserDB:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise exception from None
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


    def verify_register_data(self, user_data: dict) -> bool:
        print(user_data)
        query = self.session.query(tables.User)
        excisting_email = query.filter_by(email=user_data.get("email")).first()
        print(excisting_email)
        if excisting_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email is already in use",
                headers={"WWW-Authenticate": "Bearer"}
            )

        excisting_password = query.filter_by(
            hashed_password=self.hash_password(user_data.get("password"))).first()
        if excisting_password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This password is not unique",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return True

    def create_user(self, data: UserPost) -> Token:
        # user_data = data.dict()
        # if self.verify_register_data(user_data):
        #     user = tables.User(
        #         email=data.email,
        #         password_hash=self.hash_password(data.password)
        #     )
        user = tables.User(
                username=data.username,
                email=data.email,
                hashed_password=self.hash_password(data.password)
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        token = self.create_token(user)
        return token

    def authenticate_user(self, username: str, password: str) -> Token:
        user = self.session.query(tables.User).filter_by(username=username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"

            )
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Password is not valid"
            )
        return self.create_token(user)


    def _get_user_by_email(self, email:str)->tables.User:
        user = self.session.query(tables.User).filter_by(email=email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user


    def delete_users(self):
        users= self.session.query(tables.User).all()
        self.session.delete(users)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    def set_temporary_password(self, email:str)->str:
        user = self._get_user_by_email(email=email)
        user_password = self.create_password()
        hashed_password = self.hash_password(user_password)
        user.hashed_password = hashed_password
        self.session.commit()
        return user_password
