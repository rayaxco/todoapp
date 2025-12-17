from .utils import *
from main import app
from router.todos import get_db, get_current_user
from fastapi import status
from models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



def test_read_all_authenticated(test_todo):
    response=client.get("/todos/")
    print(response.json())
    assert response.status_code==status.HTTP_200_OK
    assert response.json()==[{'complete':False,'title':'learn to cook','description':'learn everyday','id':1,'priority':5,'owner_id':1}]

def test_read_one_authenticated(test_todo):
    response=client.get("/todos/todos/1")
    print(response.json())
    assert response.status_code==status.HTTP_200_OK
    assert response.json()=={'complete':False,'title':'learn to cook','description':'learn everyday','id':1,'priority':5,'owner_id':1}

def test_read_one_authenticated_not_found(test_todo):
    response=client.get('/todos/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()=={'detail':'Not found'}

def test_create_todo(test_todo):
    request_data={
        'title':'new todo',
        'description':'new todo description',
        'priority':4,
        'complete':False
    }
    response=client.post('/todos/create_todo',json=request_data)
    assert response.status_code==201
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==2).first()
    assert model.title==request_data.get('title')
    assert model.description==request_data.get('description')
    assert model.priority==request_data.get('priority')

def test_update_todo(test_todo):
    request_data={
        'title':'changed title',
        'description':'need to learn everyday',
        'priority':5,
        'complete':False
    }
    response=client.put('/todos/todo/1',json=request_data)
    assert response.status_code==202
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model.title=="changed title"


def test_update_todo_not_found(test_todo):
    request_data={
        'title':'changed title',
        'description':'need to learn everyday',
        'priority':5,
        'complete':False
    }
    response=client.put('/todos/todo/999',json=request_data)
    assert response.status_code==404
    assert response.json()=={'detail':'Not found'}

def test_delete_todo(test_todo):
    response=client.delete('/todos/delete/1')
    assert response.status_code==202
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response=client.delete('/todos/delete/999')
    assert response.status_code==404
    assert response.json()=={'detail':'No data found'}