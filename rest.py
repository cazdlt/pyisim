import json
import urllib
from urllib.parse import urlencode

import requests

from .exceptions import *

requests.packages.urllib3.disable_warnings()

# cat=organizationunits/bporganizations
# si atributos="*" devuelve todos los atributos
# el filtro no importan mayus y es va con comodines (*filtro*)
# si buscar_igual=True entonces quita comodines de busqueda
# si viene con algún atrubuto, lo recupera


class ISIMClient:

    def __init__(self, user_, pass_, url):

        self.__addr = url
        self.s, self.CSRF = self.autenticar(user_, pass_)

    def autenticar(self, user_, pass_):

        url = self.__addr+"/itim/restlogin/login.jsp"
        s = requests.Session()
        headers = {"Accept": "*/*"}
        r1=s.get(url, headers=headers)
    
        assert 404 != r1.status_code,"Error 404: "+r1.text
        # jsessionid=self.s.cookies.get("JSESSIONID")

        url = self.__addr+"/itim/j_security_check"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # cookies={"j_username_tmp":user_,"j_password_tmp":pass_}
        data_login = {"j_username": user_, "j_password": pass_}
        r2 = s.post(url, headers=headers, data=data_login)

        #print(r2)
        url = self.__addr+"/itim/rest/systemusers/me"
        r3 = s.get(url, headers=headers)
        try:
            CSRF = r3.headers["CSRFToken"]
        except KeyError:
            #print(user_, pass_)
            raise AuthenticationError(
                "Error de autenticación, verifique sus credenciales.")
        return s, CSRF

    def buscarOUs(self, cat, buscar_por="ou", filtro="*", buscar_igual=False):

        url = self.__addr+"/itim/rest/organizationcontainers/"+cat
        tipos = ["bporganizations", "organizationunits", "organizations"]
        if cat not in tipos:
            raise Exception(
                "No es una categoría de OU válida. Seleccione un tipo de categoría entre las siguientes: "+str(tipos))

        # print(atributos)
        data = {
            "attributes": buscar_por
        }

        OUs = json.loads(self.s.get(url, params=data).text)

        # print(OUs)
        # print(data)

        # filtro de búsqueda
        try:
            if filtro != "*":
                if buscar_igual:
                    OUs = filter(lambda ou: filtro.lower() ==
                                 ou["_attributes"][buscar_por].lower(), OUs)
                else:
                    OUs = filter(lambda ou: filtro.lower()
                                 in ou["_attributes"][buscar_por].lower(), OUs)
        except KeyError:
            OUs = None

        return list(OUs)

    # si filtro="*" busca todo
    def buscarPersonas(self, perfil, atributos="cn", embedded="", buscar_por="cn", filtro="*"):

        assert perfil in ("person", "bpperson")

        url = self.__addr+"/itim/rest/people"
        if perfil == "bpperson":
            url = url+"/bpperson"

        data = {"attributes": atributos,
                "embedded": embedded,
                buscar_por: filtro
                }
        data = urlencode(data, quote_via=urllib.parse.quote)

        try:
            response = self.s.get(url, params=data).text
            if response.find("ISIMLoginRequired") != -1:
                # TODO handle this
                raise Exception
            personas = json.loads(response)
        except Exception as e:
            personas = []

        return list(personas)

    def crearPersona(self, person, justificacion):

        url = self.__addr+"/itim/rest/people"

        tipo_persona = person.__class__.__name__

        tipos = ["Person", "BPPerson"]
        if tipo_persona not in tipos:
            raise Exception(
                "No es una tipo válido de persona. Seleccione un tipo de persona entre los siguientes: "+str(tipos))

        data = {
            "justification": justificacion,
            "profileName": tipo_persona,
            "orgID": person.orgid,
            "_attributes": person.__dict__
        }

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch"
        }

        return self.s.post(url, json=data, headers=headers)

    def crearBpperson(self, bpp, justificacion):

        url = self.__addr+"/itim/rest/people"

        tipo_persona = bpp.__class__.__name__

        tipos = ["Person", "BPPerson"]
        if tipo_persona not in tipos:
            raise Exception(
                "No es una tipo válido de persona. Seleccione un tipo de persona entre los siguientes: "+str(tipos))

        data = {
            "justification": justificacion,
            "profileName": tipo_persona,
            "orgID": bpp.orgid,
            "_attributes": bpp.__dict__
        }

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch"
        }

        return self.s.post(url, json=data, headers=headers)

    def buscarAcceso(self, atributos="accessName", filtro="*"):
        ""

        url = self.__addr+"/itim/rest/access"

        data = {"accessName": filtro,
                "accessCategory": filtro,
                "attributes": atributos,
                "limit": "1000",
                "filterId": "accessSearch"
                }
        data = urlencode(data, quote_via=urllib.parse.quote)

        accesos = json.loads(self.s.get(url, params=data).text)

        # print(data)
        listaAccesos = list(accesos)

        if len(listaAccesos) == 0:
            raise NotFoundError("Acceso no encontrado: "+filtro)

        return listaAccesos

    # retorna el primer elemento

    def verificarResultadoUnico(self, json_):
        if len(json_) > 1:
            raise MultipleFoundError()
        elif len(json_) == 0:
            raise NotFoundError()
        else:
            return json_[0]

    def obtenerLinks(self, json_, tipoObjeto):

        tipos = {"acceso": "access", "persona": "self"}
        assert tipoObjeto in tipos.keys()
        tipo = tipos[tipoObjeto]

        json_ = self.verificarResultadoUnico(json_)

        return {
            "_links": {
                tipo: {
                    "href": json_["_links"]["self"]["href"]
                }
            }
        }

    def buscarActividad(self, solicitudID="",search_attr="activityName",search_filter="*"):

        url = self.__addr+"/itim/rest/activities"
        data = {
            "filterId": "activityFilter",
            "status": "PENDING",
            search_attr:search_filter
        }

        headers={
            "Cache-Control" : "no-cache "
        }

        actividades = json.loads(self.s.get(url, params=data,headers=headers).text)
        if solicitudID:
            actividades = filter(
                lambda a: a["_links"]["request"]["href"] == solicitudID, actividades)
            return list(actividades)

        return list(actividades)

    def solicitarAccesos(self, nombreAccesos, nombrePersona, justificacion="test"):
        url = self.__addr+"/itim/rest/access/assignments"

        try:
            persona = self.obtenerLinks(self.buscarPersonas("person",
                                                            filtro=nombrePersona), "persona")["_links"]
        except NotFoundError:
            try:
                persona = self.obtenerLinks(self.buscarPersonas("bpperson",
                                                                filtro=nombrePersona), "persona")["_links"]
            except NotFoundError:
                raise PersonNotFoundError(
                    "Persona no encontrada: "+nombrePersona)

        #accesos = [obtenerLinks(buscarAcceso(self.s, filtro=nombre), "acceso") for nombre in nombreAccesos]
        # print(accesos)

        listaAccesos = open("data/accesos.txt", "r").readlines()
        accesos = [acceso.split(";")[0].strip(
        ) for acceso in listaAccesos if acceso.split(";")[1].strip() in nombreAccesos]
        # print(accesos)
        dictAccesos = list(
            map(lambda ruta: {"_links": {"access": {"href": ruta}}}, accesos))

        #print([buscarAcceso(self.s, filtro=nombre) for nombre in nombreAccesos])

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch"
        }

        data = {
            "justification": justificacion,
            "requests": [{
                "requestee": {
                    "_links": persona,
                    "add": {
                        "assignments": dictAccesos
                    }
                }
            }]
        }

        # print(data)
        return self.s.post(url, json=data, headers=headers)

    # falta tener en cuenta cuando llegan varias actividades
    def completarActividades(self, actividades, resultado, justificacion="ok"):

        url = self.__addr+"/itim/rest/workitems"

        resultCodes = {
            "Aprobado": "AA",
            "Rechazado": "AR",
            "Correcto": "SS",
            "Aviso": "SW",
            "Error": "SF"
        }

        body = []
        if len(actividades) == 0:
            raise Exception("No hay actividades para completar")

        for activity in actividades:
            activityType = activity["_attributes"]["type"]
            activityLabel = activity["_attributes"]["name"]
            workitem = activity["_links"]["workitem"]["href"]

            if activityType == "APPROVAL":
                assert resultado in ["Aprobado", "Rechazado"]
            elif activityType == "WORK_ORDER":
                assert resultado in ["Correcto", "Aviso", "Error"]

            resultCode = resultCodes[resultado]
            action = {
                "_links": {
                    "self": {
                        "href": workitem
                    }
                },
                "action": {
                    "code": resultCode
                },
                "label": activityLabel,
                "justification": justificacion
            }
            body.append(action)

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch",
            "methodOverride": "submit-in-batch"
        }

        return self.s.put(url, json=body, headers=headers)
    
    def buscarFormulario(self, perfil):

        url = self.__addr+"/itim/rest/forms/people"

        assert perfil in ["Person","BPPerson"],"Perfil inválido."

        urlPerfil=url+"/"+perfil  
        resp=****(urlPerfil)
        
        return json.loads(resp.text)["template"]["page"]["body"]["tabbedForm"]["tab"]

    def buscarServicio(self, nombre,atributos=""):
        
        url= self.__addr+"/itim/rest/services"

        data = {
                "erservicename": nombre,
                "attributes":','.join(atributos)
               }
        data = urlencode(data, quote_via=urllib.parse.quote)

        servicios = json.loads(self.s.get(url, params=data).text)

        listaServicios = list(servicios)

        if len(listaServicios) == 0:
            raise NotFoundError("Servicio no encontrado: "+nombre)

        return listaServicios

    def eliminarServicio(self,nombre):

        url= self.__addr+"/itim/rest/services"

        servicio=self.buscarServicio(nombre)
        servicio_href=servicio[0]["_links"]["self"]["href"]
        servicio_id=servicio_href.split("/")[-1]

        url_del=f"{url}/{servicio_id}"

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch"
        }
        
        return self.s.delete(url_del, headers=headers)

    def lookupSolicitud(self,requestID):
        url= self.__addr+"/itim/rest/requests"

        url_req=url+"/"+requestID
        data={
            "attributes":"*"
        }

        solicitud = json.loads(self.s.get(url_req,params=data).text)

        return solicitud

    def lookupActividad(self,activityID):
        url= self.__addr+"/itim/rest/activities"

        url_act=url+"/"+activityID
        data={
            "attributes":"*"
        }

        actividad = json.loads(self.s.get(url_act,params=data).text)

        return actividad
