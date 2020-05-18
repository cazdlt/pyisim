from isimws.auth import Session
from isimws.classes import Person
import json
import time

#Pruebas unitarias

def crear_persona(user_,pass_,env,info_persona):

    #login
    sesion=Session(user_,pass_,env).restclient

    #crea persona
    justificacion = "Pruebas"
    persona = Person(sesion, **info_persona)
    nombre_persona=persona.cn
    print(f"Creando persona {nombre_persona}..")
    r_per=json.loads(sesion.crearPersona(persona,justificacion).text)

    return persona

def crear_y_solicitar(user_,pass_,user_admin,pass_admin,env,info_persona,accesos):

    #login
    sesion=Session(user_,pass_,env).restclient
    sesion_admin=Session(user_admin,pass_admin,env).restclient

    #crea persona
    justificacion = "Pruebas"
    persona = Person(sesion, **info_persona)
    nombre_persona=persona.cn
    print(f"Creando persona {nombre_persona}..")
    r_per=json.loads(sesion.crearPersona(persona,justificacion).text)
    time.sleep(4)

    #solicita acceso
    print(f"Solicitando {len(accesos)} accesos..")
    r_acc=sesion_admin.solicitarAccesos(accesos,nombre_persona)
    access_requestID=json.loads(r_acc.content)["_links"]["result"]["href"]
    time.sleep(3)


    #aprueba las actividades
    while True:
        actividades=sesion.buscarActividad(solicitudID=access_requestID)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="APPROVAL",actividades))
        print(f"Se han encontrado {len(actividades)} aprobaciones")
        if len(actividades)<1:
            break
        else:
            r_approval=sesion.completarActividades(actividades,"Aprobado")
            time.sleep(3)

    while True:
        actividades=sesion.buscarActividad(solicitudID=access_requestID)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="WORK_ORDER",actividades))
        print(f"Se han encontrado {len(actividades)} OTs")
        if len(actividades)<1:
            break
        else:
            r_approval=sesion.completarActividades(actividades,"Correcto")
            time.sleep(3)

    print("Solicitud completada.")

    return persona

def solicitar_a_existente(user_,pass_,_user_admin,pass_admin,env,nombre_persona,accesos):

    #login
    sesion=Session(user_,pass_,env).restclient
    sesion_admin=Session(_user_admin,pass_admin,env).restclient

    print(f"Solicitando {len(accesos)} accesos..")
    r_acc=sesion_admin.solicitarAccesos(accesos,nombre_persona)
    access_requestID=json.loads(r_acc.content)["_links"]["result"]["href"]
    time.sleep(3)

    #aprueba las actividades
    while True:
        actividades=sesion.buscarActividad(solicitudID=access_requestID)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="APPROVAL",actividades))
        print(f"Se han encontrado {len(actividades)} aprobaciones")
        if len(actividades)<1:
            break
        else:
            r_approval=sesion.completarActividades(actividades,"Aprobado")
            time.sleep(3)

    while True:
        actividades=sesion.buscarActividad(solicitudID=access_requestID)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="WORK_ORDER",actividades))
        print(f"Se han encontrado {len(actividades)} OTs")
        if len(actividades)<1:
            break
        else:
            r_approval=sesion.completarActividades(actividades,"Correcto")
            time.sleep(3)

def completar_actividades_de_solicitud(user_,pass_,env,id_solicitud):

    sesion=Session(user_,pass_,env).restclient
    href_solicitud=f"/itim/rest/requests/{id_solicitud}"
    #aprueba las actividades
    while True:
        actividades=sesion.buscarActividad(solicitudID=href_solicitud)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="APPROVAL",actividades))
        print(f"Se han encontrado {len(actividades)} aprobaciones")
        if len(actividades)<1:
            break
        else:
            r_approval=sesion.completarActividades(actividades,"Aprobado")
            time.sleep(3)

    while True:
        actividades=sesion.buscarActividad(solicitudID=href_solicitud)
        actividades=list(filter(lambda a: a["_attributes"]["type"]=="WORK_ORDER",actividades))
        print(f"Se han encontrado {len(actividades)} OTs")
        if len(actividades)<1:
            return
        else:
            r_approval=sesion.completarActividades(actividades,"Correcto")
            time.sleep(3)

    return r_approval


    