from fastapi import (
    BackgroundTasks, Depends, File,
    HTTPException, status, UploadFile)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from typing import List

from bets_journal.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_username,
    MAIL_PORT=25,
    MAIL_SERVER="mail.lanet.ua",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class Email(BaseModel):
    email: List[EmailStr]


async def send_email(email: Email):
    new_password = "new_password"
    link = "<a href='http://localhost:8000/auth/change-password'> Click to change password </a>"
    template = f"""
    <!DOCTYPE html!>
    <html>
        <head>
        </head>
        <body>
            <div style = "display: flex"; "align-items: center; 
            justife-content: center; flex-direction">
            
            <h3> New Password.</h3>
            
            <p> Your new temporary password is {new_password}. Please, use it to 
            set new permanent password using this link {link}. Take in consideration, 
            that temporary pass will be valid only till the.
            </p>
            </h3>
            
            </div>
        </body>
    </html>
    """
    message = MessageSchema(
        subject="Changing your password in Bet journal",
        recipients=email.dict().get("email"),
        body=template,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
