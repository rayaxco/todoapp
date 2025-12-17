from http.client import HTTPException

from fastapi import APIRouter,Depends,Path,HTTPException,Request
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router=APIRouter(
    prefix='/todos', tags=['Todos']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]
templates=Jinja2Templates('templates')

class TodoRequest(BaseModel):
    title :str=Field(min_length=1)
    description :str=Field(min_length=1,max_length=100)
    priority :int=Field(gt=0,lt=6)
    complete :bool

def redirect_to_login():
    redirect_response=RedirectResponse(url='/auth/login-page',status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response
###     PAGES
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            print('redirecting here')
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("user id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()

# @router.get('/edit-todo-page/{todoid}')
# async def render_edit_todo_page(todoid:int, db:db_dependency,request:Request):
#     try:
#         print('calling')
#         user=await get_current_user(request.cookies.get('access_token'))
#         if user is None:
#             return redirect_to_login()
#         todo=db.query(Todos).filter(Todos.id==todoid).first()
#
#         # return templates.TemplateResponse('edit-todo.html',{'request':request,'todo':todo,'user':user})
#         return templates.TemplateResponse("edit-todo.html",{"request": request, "todo": todo, "user": user})
#     except:
#         return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):

    user = await get_current_user(request.cookies.get('access_token'))

    if user is None:
        return redirect_to_login()

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})




@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        print(request.cookies.get('body'))
        print(user)

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()




###     ENDPOINTS
@router.get('/',status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return db.query(Todos).filter(Todos.owner_id==user.get('user id')).all()

@router.get('/todos/{todo_id}',status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=-1)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    todo_model=db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('user id')).first()

    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')

@router.post('/create_todo',status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,db:db_dependency,todo_request:TodoRequest):
    print(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed!')
    todo_model=Todos(**todo_request.model_dump(),owner_id=user.get('user id'))
    db.add(todo_model)
    db.commit()

@router.put('/todo/{todo_id}',status_code=status.HTTP_202_ACCEPTED)
async def update_todo(user:user_dependency,db:db_dependency,todo_id:int,update_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed!')

    todo_update=Todos(**update_request.model_dump())
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id==user.get('user id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    todo_model.title=update_request.title
    todo_model.description = update_request.description
    todo_model.priority = update_request.priority
    todo_model.complete = update_request.complete
    db.add(todo_model)
    db.commit()

@router.delete('/delete/{todo_id}',status_code=status.HTTP_202_ACCEPTED)
async def delete_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed!')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('user id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No data found')

    db.delete(todo_model)
    db.commit()



