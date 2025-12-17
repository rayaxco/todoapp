from fastapi import FastAPI,Request,status
import models
from database import engine, SessionLocal
from router import auth, todos, admin,users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

models.Base.metadata.create_all(bind=engine)
templates=Jinja2Templates(directory='templates')

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.mount('/static',StaticFiles(directory='static'),name='static')
@app.get('/')
def home_render():
    return RedirectResponse('/todos/todo-page')

@app.get('/healthy')
def health_check():
    return {'status':'healthy'}
