import pytest

from isimws import search
from pycolp.auth import MasAccesos
from pycolp import PersonColpensiones


@pytest.fixture
def sesion():
    u=****
    p=****
    env="int"
    cert="ca colp.cer"
    return MasAccesos(u,p,env,cert)


def test_search_access(sesion):
    r=search.access(sesion,filter="*Consulta*",limit=2)
    assert len(r)>0

def test_search_people(sesion):
    r=search.people(sesion,PersonColpensiones,"employeenumber","96451425873",limit=1)
    assert len(r)>0

def test_request_access(sesion):
    acc=search.access(sesion,filter="*Consulta*",limit=2)
    p=****(sesion,PersonColpensiones,"employeenumber","96451425873",limit=1)[0]
    req=p.solicitar_accesos(sesion,acc,"ok")
    assert req.status_code==202

def test_create_person(sesion):

    info_persona={
        "cedulajefe": "1015463230",
        "correo": "camilo.zamora@deltaits.com",
        "cargo": "Analista 420-05", #Director 130-06
        "dep":"Vicepresidencia de Operaciones del Regimen de Prima Media;Direccion de Historia Laboral",
    }
    justificacion="test"
    
    persona = PersonColpensiones(sesion, **info_persona)

    r_per=persona.crear(sesion,justificacion)
    assert "requestId" in r_per

def test_search_service(sesion,by="er"):
    r=search.service(sesion,"Colpensiones",filter="SAP NW")
    assert len(r)>0
    assert r[0].name=="SAP NW"