from http.client import HTTPException

from fastapi import APIRouter,Depends,Path,HTTPException
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

router=APIRouter(prefix='/admin',tags=['admin'])


@router.get('/todos',status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None or user.get('user role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Not authorized')
    return db.query(Todos).all()

@router.delete('/delete_todo/{todo_id}',status_code=status.HTTP_200_OK)
async def delete_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None or user.get('user role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No data found')

    db.delete(todo_model)
    db.commit()
