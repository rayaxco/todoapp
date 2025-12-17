import pytest
from passlib.crypto.scrypt import validate


def test_equal_or_not_equal():
    assert 3==3

def test_is_instance():
    assert isinstance('a string',str)
    assert isinstance('10',str)

def test_boolean():
    validated=True
    assert validated is True
    assert ('hello'=='world') is False

def test_type():
    assert type('hello' is str)
    assert type('10' is not int)

def test_greater_than_and_less_than():
    assert 7>3
    assert 4<7

def test_list():
    num_list=[1,2,3,4,5]
    any_list=[False,False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)

class Student:
    def __init__(self,first_name:str,last_name:str,major:str,years:str):
        self.first_name=first_name
        self.last_name=last_name
        self.major=major
        self.years=years

@pytest.fixture
def default_employee():
    return Student('john','doe','computer_science',3)

def test_person_initialization(default_employee):
    # p=Student('john','doe','computer_science',3)
    assert default_employee.first_name=='john','first name should be john'
    assert default_employee.last_name=='doe','last name should be doe'
    assert default_employee.major=='computer_science'
    assert default_employee.years==3