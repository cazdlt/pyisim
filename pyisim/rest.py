import json
import requests
import urllib
from urllib.parse import urlencode
from pyisim.exceptions import NotFoundError, MultipleFoundError,AuthenticationError

requests.packages.urllib3.disable_warnings()

# cat=organizationunits/bporganizations
# si atributos="*" devuelve todos los atributos
# el filtro no importan mayus y es va con comodines (*filtro*)
# si buscar_igual=True entonces quita comodines de busqueda
# si viene con algún atrubuto, lo recupera


class ISIMClient:
    def __init__(self, url, user_, pass_, cert_path=None):

        self.__addr = url
        self.s, self.CSRF = self.autenticar(user_, pass_, cert_path)

    def autenticar(self, user_, pass_, cert=None):

        assert cert is not None, "No certificate passed"
        url = self.__addr + "/itim/restlogin/login.jsp"
        s = requests.Session()
        # print(cert)
        s.verify = cert
        headers = {"Accept": "*/*"}
        r1 = s.get(url, headers=headers)

        assert 404 != r1.status_code, "Error 404: " + r1.text
        # jsessionid=self.s.cookies.get("JSESSIONID")

        url = self.__addr + "/itim/j_security_check"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # cookies={"j_username_tmp":user_,"j_password_tmp":pass_}
        data_login = {"j_username": user_, "j_password": pass_}
        s.post(url, headers=headers, data=data_login)

        # print(r2)
        url = self.__addr + "/itim/rest/systemusers/me"
        r3 = s.get(url, headers=headers)
        try:
            CSRF = r3.headers["CSRFToken"]
        except KeyError:
            # print(user_, pass_)
            raise AuthenticationError(
                "Error de autenticación, verifique sus credenciales."
            )
        return s, CSRF

    def buscarOUs(
        self, profile_name, filtro, buscar_por=None, attributes="", limit=100
    ):

        url = self.__addr + "/itim/rest/organizationcontainers/" + profile_name
        tipos = [
            "bporganizations",
            "organizationunits",
            "organizations",
            "locations",
            "admindomains",
        ]
        if profile_name not in tipos:
            raise Exception(
                "No es una categoría de OU válida. Seleccione un tipo de categoría entre las siguientes: "
                + str(tipos)
            )

        name_attrs = {
            "bporganizations": "ou",
            "organizationunits": "ou",
            "organizations": "o",
            "locations": "l",
            "admindomains": "ou",
        }

        if not buscar_por:
            buscar_por = name_attrs[profile_name]

        data = {"attributes": attributes, "limit": limit, buscar_por: filtro}

        OUs = json.loads(self.s.get(url, params=data).text)

        return list(OUs)

    # si filtro="*" busca todo
    def buscarPersonas(
        self, perfil, atributos="cn", embedded="", buscar_por="cn", filtro="*", limit=50
    ):

        assert perfil.lower() in ("person", "bpperson")

        url = self.__addr + "/itim/rest/people"
        if perfil.lower() == "bpperson":
            url = url + "/bpperson"

        data = {
            "attributes": atributos,
            "embedded": embedded,
            "limit": limit,
            buscar_por: filtro,
        }
        headers = {"Cache-Control": "no-cache"}
        data = urlencode(data, quote_via=urllib.parse.quote)

        try:
            response = self.s.get(url, params=data, headers=headers).text
            if response.find("ISIMLoginRequired") != -1:
                # TODO handle this
                raise Exception("Please login.")
            personas = json.loads(response)
        except Exception:
            personas = []

        return list(personas)

    def crearPersona(self, person, orgid, justification):

        url = self.__addr + "/itim/rest/people"

        # tipo_persona = person.profile_name

        # tipos = ["Person", "BPPerson"]
        # if tipo_persona in tipos:
        #     raise Exception(
        #         "No es una tipo válido de persona. Seleccione un tipo de persona entre los siguientes: "+str(tipos))

        person_data = person.__dict__.copy()
        person_data.pop("changes", "")

        data = {
            "justification": justification,
            "profileName": person.profile_name,
            "orgID": orgid,
            "_attributes": person_data,
        }

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            # "X-HTTP-Method-Override": "submit-in-batch" FP2
        }

        ret = self.s.post(url, json=data, headers=headers)
        return json.loads(ret.text)

    def modificarPersona(self, href, changes, justification):
        url = self.__addr + href

        data = {
            "justification": justification,
            "_attributes": changes,
        }

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        ret = self.s.put(url, json=data, headers=headers)
        return json.loads(ret.text)

    def buscarAcceso(
        self,
        by="accessName",
        atributos="accessName",
        filtro="*",
        limit=20,
        requestee_href=None,
    ):

        url = self.__addr + "/itim/rest/access"

        data = {
            by: filtro,
            "attributes": atributos,
            "limit": limit,
            "requestee": requestee_href,
            # "filterId": "accessSearch"
        }
        data = urlencode(data, quote_via=urllib.parse.quote)

        res = self.s.get(url, params=data).text
        accesos = json.loads(res)

        return list(accesos)

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

        return {"_links": {tipo: {"href": json_["_links"]["self"]["href"]}}}

    def buscarActividad(
        self, solicitudID="", search_attr="activityName", search_filter="*"
    ):

        url = self.__addr + "/itim/rest/activities"
        data = {
            "filterId": "activityFilter",
            "status": "PENDING",
            search_attr: search_filter,
        }

        headers = {"Cache-Control": "no-cache"}

        actividades = json.loads(self.s.get(url, params=data, headers=headers).text)
        if solicitudID:
            actividades = filter(
                lambda a: a["_links"]["request"]["href"] == solicitudID, actividades
            )
            return list(actividades)

        return list(actividades)

    def solicitarAccesos(self, accesos, persona, justification):
        url = self.__addr + "/itim/rest/access/assignments"

        persona_rest = {"self": {"href": persona.href}}

        accesos_rest = [{"_links": {"access": {"href": a.href}}} for a in accesos]

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch",
        }

        # persona: {'self': {'href': '/itim/rest/people/ZX...bnNpb25lcw'}}
        # accesos: [{'_links':{'access': {'href': '/itim/rest/access/32...7126878451'}}},...]
        data = {
            "justification": justification,
            "requests": [
                {
                    "requestee": {
                        "_links": persona_rest,
                        "add": {"assignments": accesos_rest},
                    }
                }
            ],
        }

        # print(data)
        return self.s.post(url, json=data, headers=headers)

    def parse_rfi_form(self, workitem_id, rfi_values):

        response = self.s.get(
            f"{self.__addr}/itim/rest/activities/rfiformdetails/{workitem_id}"
        )
        form_details = json.loads(response.text)
        # esto es un arreglo con la info del formulario
        form = form_details["template"]["page"]["body"]["tabbedForm"]["tab"]

        rfi_form = []
        for tab in form:
            for element in tab["formElement"]:
                attr_name = element["name"].split(".")[-1]
                editable = element["editable"]
                value = ""

                try:
                    required = element["required"]
                except KeyError:
                    required = False

                if required:
                    try:
                        value = form_details["defaultAttrValues"][attr_name]
                    except KeyError:
                        pass
                if editable:
                    value = [
                        attr["value"]
                        for attr in rfi_values
                        if attr["name"] == attr_name
                    ][0]

                if editable or required:
                    rfi_form.append(
                        {
                            "name": attr_name,
                            "value": value,
                        }
                    )

        return rfi_form

    # falta tener en cuenta cuando llegan varias actividades
    def completarActividades(self, actividades, resultado, justification="ok"):

        url = self.__addr + "/itim/rest/workitems"

        resultCodes = {
            "approve": "AA",
            "reject": "AR",
            "successful": "SS",
            "warning": "SW",
            "failure": "SF",
        }

        body = []

        if isinstance(resultado, str):
            resultado = resultado.lower()

        if len(actividades) == 0:
            raise Exception("Nothing to complete")

        for activity in actividades:
            activityType = activity["_attributes"]["type"]
            activityLabel = activity["_attributes"]["name"]
            workitem = activity["_links"]["workitem"]["href"]

            if activityType == "APPROVAL":
                assert resultado in ["approve", "reject"]
            elif activityType == "WORK_ORDER":
                assert resultado in ["successful", "warning", "failure"]
            elif activityType == "RFI":
                assert isinstance(resultado, list)

            resultCode = resultCodes[resultado] if activityType != "RFI" else "RS"
            action = {
                "_links": {"self": {"href": workitem}},
                "action": {"code": resultCode},
                "label": activityLabel,
                "justification": justification,
            }

            if activityType == "RFI":

                assert (
                    len(actividades) == 1
                ), "Solo es posible completar un RFI a la vez"

                workitem_id = workitem.split("/")[-1]

                action = {
                    "action": {"code": resultCode},
                    "label": activityLabel,
                    "justification": justification,
                }

                if len(resultado) > 0:

                    rfi_form = self.parse_rfi_form(workitem_id, resultado)
                    action["rfiAttributeValues"] = rfi_form

                headers = {
                    "CSRFToken": self.CSRF,
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                }

                return self.s.put(f"{url}/{workitem_id}", json=action, headers=headers)

            body.append(action)

        headers = {
            "CSRFToken": self.CSRF,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-HTTP-Method-Override": "submit-in-batch",
            "methodOverride": "submit-in-batch",
        }

        return self.s.put(url, json=body, headers=headers)

    def buscarFormulario(self, perfil):

        url = self.__addr + "/itim/rest/forms/people"

        assert perfil in ["Person", "BPPerson"], "Perfil inválido."

        urlPerfil = url + "/" + perfil
        resp = self.s.get(urlPerfil)

        return json.loads(resp.text)["template"]["page"]["body"]["tabbedForm"]["tab"]

    def buscarServicio(self, search_attr, search_filter, limit, atributos=""):

        url = self.__addr + "/itim/rest/services"

        data = {
            search_attr: search_filter,
            "attributes": atributos,
            "limit": limit,
        }
        data = urlencode(data, quote_via=urllib.parse.quote)

        servicios = json.loads(self.s.get(url, params=data).content)

        if len(servicios) == 0:
            raise NotFoundError(
                f"Servicio no encontrado: ({search_attr}={search_filter})"
            )

        return servicios

    # def eliminarServicio(self, nombre):

    #     url = self.__addr + "/itim/rest/services"

    #     servicio = self.buscarServicio(nombre)
    #     servicio_href = servicio[0]["_links"]["self"]["href"]
    #     servicio_id = servicio_href.split("/")[-1]

    #     url_del = f"{url}/{servicio_id}"

    #     headers = {
    #         "CSRFToken": self.CSRF,
    #         "Content-Type": "application/json",
    #         "Accept": "*/*",
    #         "X-HTTP-Method-Override": "submit-in-batch",
    #     }

    #     return self.s.delete(url_del, headers=headers)

    def lookupSolicitud(self, requestID):
        url = self.__addr + "/itim/rest/requests"

        url_req = url + "/" + requestID
        data = {"attributes": "*"}

        solicitud = json.loads(self.s.get(url_req, params=data).text)

        return solicitud

    def lookupActividad(self, activityID):
        url = self.__addr + "/itim/rest/activities"

        url_act = url + "/" + activityID
        data = {"attributes": "*"}

        actividad = json.loads(self.s.get(url_act, params=data).text)

        return actividad

    def lookupPersona(self, href, attributes="dn"):
        url = self.__addr + href

        params = {
            "attributes": attributes,
            "forms": False,
        }

        person = self.s.get(url, params=params)

        return json.loads(person.text)

    def lookupCurrentPerson(self, attributes="*", embedded=""):
        url = self.__addr + "/itim/rest/people/me"

        params = {
            "attributes": attributes,
            "embedded": embedded,
        }

        person = self.s.get(url, params=params)

        return json.loads(person.text)
