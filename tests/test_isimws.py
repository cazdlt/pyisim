import pytest

from isimws import search
from isimws.auth import Session
from isimws.entities import Person
from secret import admin_login,admin_pw,cert,env,test_url,test_org


@pytest.fixture
def sesion():
    return Session(test_url,admin_login,admin_pw,cert)

def test_search_access(sesion):
    r=search.access(sesion,filter="*Consulta*",limit=2)
    assert len(r)>0

def test_search_people(sesion):
    r=search.people(sesion,Person,"employeenumber","96451425873",limit=1)
    assert len(r)>0

def test_search_service(sesion):
    r=search.service(sesion,test_org,filter="SAP NW")
    assert len(r)>0
    assert r[0].name=="SAP NW"