from simrest import sim as simrest
from masaccesos import Person
import json
import time

#Pruebas unitarias

def crear_persona(info_persona):

    #login
    sesion=simrest("cazamorad",'goDiCLNT8Z4W',env="int")

    #crea persona
    justificacion = "Pruebas"
    persona = Person(sesion, **info_persona)
    nombre_persona=persona.cn
    print(f"Creando persona {nombre_persona}..")
    r_per=json.loads(sesion.crearPersona(persona,justificacion).text)

    return persona

def crear_y_solicitar(info_persona,accesos):

    #login
    sesion=simrest("cazamorad",'goDiCLNT8Z4W',env="int")
    sesion_admin=simrest("itim manager","Colpensiones.2019",env="int")

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


    #obtiene actividad de aprobación
    for i in range(len(accesos)):
        print(f"Aprobando actividad {i+1}..")
        act=sesion.buscarActividad(solicitudID=access_requestID)
        assert len(act)==1

        #aprueba la actividad
        r_approval=sesion.completarActividades(act,"Aprobado")
        time.sleep(4)

    return persona

def solicitar_a_existente(nombre_persona,accesos):

    #login
    sesion=simrest("cazamorad",'goDiCLNT8Z4W',env="int")
    sesion_admin=simrest("itim manager","Colpensiones.2019",env="int")

    print(f"Solicitando {len(accesos)} accesos..")
    r_acc=sesion_admin.solicitarAccesos(accesos,nombre_persona)
    access_requestID=json.loads(r_acc.content)["_links"]["result"]["href"]
    time.sleep(3)


    #obtiene actividad de aprobación
    for i in range(len(accesos)):
        print(f"Aprobando actividad {i+1}..")
        act=sesion.buscarActividad(solicitudID=access_requestID)
        assert len(act)==1

        #aprueba la actividad
        r_approval=sesion.completarActividades(act,"Aprobado")
        time.sleep(4)

if __name__ == "__main__":

    # accesos=["Rol prueba CORRDNC BASICO","Rol prueba HLT Verifica","Rol prueba Consulta Pagos","Rol prueba Modican Consulta","Rol prueba Novedades en Línea","Rol prueba Consdnc","Rol prueba Autoliss Consulta","Rol prueba Verigre"]
    
    # accesos=[]

    info_persona={
        "cedulajefe": "1015463230",
        "correo": "camilo.zamora@deltaits.com",
        "cargo": "Analista 420-05",
    }
    accesos=["Rol prueba Modican Consulta",
             "Rol prueba Autoliss Consulta"]
    
    persona = crear_y_solicitar(info_persona,accesos)

    accesos=[
        "Rol prueba CORRDNC BASICO",
        "Rol prueba HLT Verifica"
    ]
    solicitar_a_existente(persona.cn,accesos)
    