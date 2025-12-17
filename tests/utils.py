from sqlalchemy import create_engine, StaticPool,text
from sqlalchemy.orm import sessionmaker
from starlette.staticfiles import StaticFiles
from database import Base
from main import app
from router.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from models import Todos,Users
from router.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL='sqlite:///./testdb.db'
engine=create_engine(SQLALCHEMY_DATABASE_URL,
                     connect_args={'check_same_thread':False},
                     poolclass=StaticPool)
TestingSessionLocal=sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'codingwithrobytest','user id':1,'user role':'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client=TestClient(app)

@pytest.fixture
def test_todo():
    todo=Todos(
        title='learn to cook',
        description='learn everyday',
        priority=5,
        complete=False,
        owner_id=1
    )
    db=TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text('DELETE from todos;'))
        connection.commit()

@pytest.fixture
def test_user():
    user=Users(
        username='codingwithrobytest',
        first_name='eric',
        last_name='roby',
        email='codingwithrobytest@email.com',
        is_active=True,
        hashed_password=bcrypt_context.hash('testpassword'),
        role='admin',
        phone_number='(111)-111-1111'
    )
    db=TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE from users;'))
        connection.commit()