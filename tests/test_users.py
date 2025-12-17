from .utils import *
from router.users import get_current_user,get_db
from fastapi import status

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=override_get_current_user

def test_return_user(test_user):
    response=client.get('/Users/get_user')
    assert response.status_code == status.HTTP_200_OK
    # assert response.json()==None
    assert response.json()['username']=='codingwithrobytest'
    assert response.json()['email']=='codingwithrobytest@email.com'
    assert response.json()['first_name']=='eric'
    assert response.json()['last_name']=='roby'
    assert response.json()['is_active']==True
    assert response.json()['phone_number']=='(111)-111-1111'

def test_update_user(test_user):
    response=client.put('/Users/update_user/1')
    response.status_code==200
    # db=TestingSessionLocal()
    # model=db.query(Users).filter(Users.id==1).first()
    # assert model.username==None

def test_change_password(test_user):
    response=client.put('/Users/change_password',json={'old_password':'testpassword','new_password':'newtestpassword'})
    response.status_code==202

def test_change_password_invalid_current_password(test_user):
    response = client.put('/Users/change_password',json={'old_password': 'testpasswords', 'new_password': 'newtestpassword'})
    assert response.status_code==401
    assert response.json()=={'detail':'wrong password'}

def test_phone_number_success(test_user):
    response=client.put('/Users/phonenumber/(222)-222-2222')
    assert response.status_code==204




