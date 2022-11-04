from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from bets_journal import tables
from bets_journal.schemas.authenticate_schemas import Token, UserPost, UserDB
from bets_journal.services.auth_service import AuthService

router = APIRouter()

@router.get("/get-user/{id}")
def get_user(id:int, service: AuthService=Depends())->UserDB:
    user = service.session.query(tables.User).filter_by(id=id).first()

    return user

@router.post("/auth/sign-in/")
def sign_in(data: OAuth2PasswordRequestForm = Depends(), service:AuthService = Depends())->Token:
    return service.authenticate_user(data.username, data.password)


@router.post("/auth/register/")
def register_user(user_data: UserPost, service: AuthService = Depends()):
    return service.create_user(user_data)

