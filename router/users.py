import datetime
from datetime import timedelta,datetime,timezone
from fastapi import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic.v1 import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED
from starlette import status

from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError
from .auth import get_current_user
from passlib.context import CryptContext
router=APIRouter(prefix='/Users', tags=['Users'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserRequest(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    hashed_password:str
    is_active:bool
    role:str

class Phone(BaseModel):
    phone_number:str

class ChangePassword(BaseModel):
    old_password:str=Field(min_length=8)
    new_password:str=Field(min_length=8)

@router.get('/get_user',status_code=status.HTTP_200_OK)
async def get_user_information(user:user_dependency,db:db_dependency):
    username=user.get('username')
    return db.query(Users).filter(Users.username==username).first()

@router.put('/update_user/{user_id}',status_code=status.HTTP_201_CREATED)
async def modify_user(user:user_dependency, db:db_dependency, form_data:UserRequest, user_id:int=None):


    user_model=db.query(Users).filter(Users.id==user_id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='user not found')

    hashed_password = bcrypt_context.hash(form_data.hashed_password)
    user_model.email=form_data.email
    user_model.username=form_data.username
    user_model.first_name=form_data.first_name
    user_model.last_name=form_data.last_name
    user_model.hashed_password=hashed_password
    user_model.is_active=form_data.is_active
    user_model.role=form_data.role
    db.add(user_model)
    db.commit()
    raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail='user modified')

@router.put('/change_password',status_code=status.HTTP_202_ACCEPTED)
async def change_password(user:user_dependency,db:db_dependency,form_data:ChangePassword):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Not authorized')

    old_pass_hashed=bcrypt_context.hash(form_data.old_password)
    new_pass_hashed=bcrypt_context.hash(form_data.new_password)

    if old_pass_hashed == new_pass_hashed:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail='new password must be different than old password')
    user_model=db.query(Users).filter(Users.username==user.get('username')).first()
    if not bcrypt_context.verify(form_data.old_password,user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='wrong password')
    user_model.hashed_password=new_pass_hashed
    db.add(user_model)
    db.commit()
    raise HTTPException(status_code=status.HTTP_202_ACCEPTED,detail='password changed')

@router.put('/update_phone_number',status_code=status.HTTP_202_ACCEPTED)
async def update_phone_number(user:user_dependency,db:db_dependency,phone_data:Phone):
    user_model=db.query(Users).filter(Users.username==user.get('username')).first()
    user_model.phone_number=phone_data.phone_number
    db.add(user_model)
    db.commit()

@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phonenumber(user: user_dependency, db: db_dependency,phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.username == user.get('username')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()