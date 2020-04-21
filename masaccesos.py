from random import randint, seed, choice
from simrest import sim
import names
import time

class ContratoNoEncontradoError(Exception):
    pass

class Person:
    orgid = "ZXJnbG9iYWxpZD0wMDAwMDAwMDAwMDAwMDAwMDAwMCxvdT1jb2xwZW5zaW9uZXMsZGM9Y29scGVuc2lvbmVz"

    def __init__(self, sesion, tipodoc="CC", nombre=None, apellido=None, doc=None, correo="pruebasiamqa@colpensiones.gov.co", cedulajefe="", dep=****, cargo=None, tipocontrato=None):

        if nombre is None:
            nombre = names.get_first_name()
        self.givenname = nombre

        if apellido is None:
            apellido = names.get_last_name()
        self.sn = apellido

        if doc is None:
            doc = str(randint(1, 100000000000))
        self.employeenumber = doc

        if dep is None:
            #data="accesos/sim/data/dependencias.txt"
            data="data/dependencias.txt"
            deps = open(data).read().splitlines()
            dep = choice(deps)
        self.departmentnumber = dep

        if cargo is None:
            #data="accesos/sim/data/cargos.txt"
            data="data/cargos.txt"
            cargos = open(data).read().splitlines()
            cargo = choice(cargos)
        self.title = cargo

        if tipocontrato is None:
            #data="accesos/sim/data/tiposContrato.txt"
            data="data/tiposContrato.txt"
            tiposcontrato = open(data).read().splitlines()
            tipocontrato = choice(tiposcontrato)
        self.businesscategory = tipocontrato

        if cedulajefe:

            dire = sesion.buscarPersonas(
                "person", atributos="dn", buscar_por="employeenumber", filtro=cedulajefe)

            if len(dire) == 0:
                raise Exception(
                    "No se ha encontrado ninguna persona con la cédula de jefe ingresada.")
            elif len(dire) > 1:
                raise Exception(
                    "Se ha encontrado más de una persona con la cédula de jefe ingresada.")
            else:
                self.manager = dire[0]["_attributes"]["dn"]

        else:
            self.manager = ""

        self.initials = tipodoc
        self.mobile = correo
        self.cn = self.givenname+" "+self.sn

    def __str__(self):
        return f"Person.\n\tNombre completo: {self.cn}\n\tCédula: {self.employeenumber}"


class BPPerson:
    orgid = "ZXJnbG9iYWxpZD0wMDAwMDAwMDAwMDAwMDAwMDAwMCxvdT1jb2xwZW5zaW9uZXMsZGM9Y29scGVuc2lvbmVz"

    def __init__(self, sim, tipodoc="CC", nombre=None, apellido=None, doc=None, correo="pruebasiamqa@colpensiones.gov.co", contrato=None):

        if nombre is None:
            nombre = names.get_first_name()
        self.givenname = nombre

        if apellido is None:
            apellido = names.get_last_name()
        self.sn = apellido

        if doc is None:
            doc = str(randint(1, 100000000000))
        self.employeenumber = doc

        bpOrgs=sim.buscarOUs(cat="bporganizations", filtro=contrato, buscar_por="description",buscar_igual=True)
        #print(bpOrgs)
        if not bpOrgs:
            raise ContratoNoEncontradoError(f"El contrato {contrato} no está registrado en +Accesos. El usuario no ha sido creado.")
        else:
            self.description=contrato

        self.mail = correo
        self.initials = tipodoc
        
        self.cn = self.givenname+" "+self.sn        

    def __str__(self):
        return f"BPPerson.\n\tNombre completo: {self.cn}\n\tCédula: {self.employeenumber}\n\tContrato: {self.description}"


if __name__ == "__main__":

    usuario = input("Usuario: ")
    clave = input("Clave: ")
    prueba = BPPerson(sim)
    print(prueba)
