from main import app
from .utils import *
from router.admin import get_db,get_current_user

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user

def test_admin_read_all(test_todo):
    response=client.get('/admin/todos')
    assert response.status_code==200
    assert response.json()==[{'complete':False,'title':'learn to cook','description':'learn everyday','id':1,'priority':5,'owner_id':1}]


def test_delete_user(test_todo):
    response=client.delete('/admin/delete_todo/1')
    assert response.status_code==200
    db=TestingSessionLocal()
    model=db.query(Todos).filter(Todos.id==1).first()
    assert model is None

def test_delete_user_not_found(test_todo):
    response=client.delete('/admin/delete_todo/999')
    assert response.status_code==404
    assert response.json()=={'detail':'No data found'}