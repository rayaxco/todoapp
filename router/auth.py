import datetime
from datetime import timedelta,datetime,timezone
from fastapi import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends,Request
from pydantic.v1 import BaseModel
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED
from starlette import status

from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router=APIRouter(prefix='/auth', tags=['auth'])
SECRET_KEY='6f1fd4e841b000a7a92165f02fc0a008ffa4e9a0071a8174113ef5564cf56e0c'
ALGORITHM='HS256'

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')
# app=FastAPI() #no need for this when using routers app is in the main.py file

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session,Depends(get_db)]
templates=Jinja2Templates('templates')

#####       PAGES
@router.get('/login-page')
def render_login_page(request:Request):
    return templates.TemplateResponse('login.html',{'request':request})


@router.get('/register-page')
def render_login_page(request:Request):
    return templates.TemplateResponse('register-page.html',{'request':request})


class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    role:str
    is_active:bool
    hashed_password:str
    phone_number:str

class Token(BaseModel):
    access_token:str
    token_type:str
#####       endponts
@router.post('/create',status_code=HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request:CreateUserRequest):
    create_user_model=Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        is_active=create_user_request.is_active,
        phone_number=create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()


def authenticate_user(username:str,password:str, db):
    print('calling authenticate / matching username and password and return sql model')
    user_model=db.query(Users).filter(Users.username==username).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password,user_model.hashed_password):
        return False
    return user_model

def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
    print('calling create_access_token')
    encode = {'sub': username, 'id': user_id,'role':role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    token=jwt.encode(encode,SECRET_KEY,ALGORITHM)
    return token



@router.post('/token',response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    print('calling token endpoint')
    is_authenticated=authenticate_user(form_data.username,form_data.password,db)
    if is_authenticated:
        token= create_access_token(is_authenticated.username,is_authenticated.id,is_authenticated.role,timedelta(minutes=20))
        return {'access_token':token,'token_type':'bearer'}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user')

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        print('calling get_current_user')
        payload=jwt.decode(token=token,key=SECRET_KEY,algorithms=ALGORITHM)
        username:str=payload.get('sub')
        user_id:int=payload.get('id')
        role:str=payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user')
        return {'username':username,'user id':user_id,'user role':role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user')



#####       PAGES
