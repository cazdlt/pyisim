import pandas as pd
from simsoap import sim
import numpy as np
import pprint
from isim_classes import StaticRole
from tictoc import tic,toc

def leerRoles(csv_path):

    converters={
        "dueños_cedula"
        "dueños_rol"
    }
    roles_df=pd.read_csv(csv_path,sep=****;",dtype={
        "dueños_rol":str,
        "dueños_cedula":str
    })
    roles_df=roles_df.where(roles_df.notna(), None)

    roles_df[["dueños_rol","dueños_cedula"]]=roles_df[["dueños_rol","dueños_cedula"]] \
                                                .applymap(lambda x: x.split(",") if x is not None else None)
    #print(roles_df)

    roles_df=roles_df.rename({
        "nombre":"name",
        "descripcion":"description",
        "acceso_opcion":"access_option",
        "acceso_categoria":"access_category",
        "dueños_rol":"owner_roles",
        "dueños_cedula":"owner_cedulas",
        "clasificacion":"classification"
    },axis=1)

    return roles_df

def crearOModificarRol(sesion,rol_info):
    """
       Primero busca (por nombre)
            Si no lo encuentra, lo crea
            Si lo encuentra, lo modifica
    """
    found=sesion.buscarRol(f"(errolename={rol_info['name']})",find_unique=False)

    rol_dict=rol_info.to_dict()
    try:
        tic()
        rol=StaticRole(sesion,**rol_dict)
        toc("Tiempo al crear rol")
    except Exception as e:
            return f"ERROR - {str(e)} - {rol_info['name']}"

    if len(found)==0:
        print(f"Creando rol {rol_info['name']}")
        try:
            tic()
            r=rol.crearEnSIM(sesion)
            toc("Tiempo de respuesta")
            return f"CREADO - {r['itimDN']}"

        except Exception as e:
            return f"ERROR - {str(e)} - {rol_info['name']}"

    elif len(found)==1:
        print(f"Rol encontrado, actualizando {rol_info['name']}")
        #print(found[0])
        try:
            tic()
            r=rol.modificarEnSIM(sesion,found[0]["itimDN"])
            toc("Tiempo de respuesta")
            return f"ACTUALIZADO - {rol_info['name']}"

        except Exception as e:
            return f"ERROR - {str(e)} - {rol_info['name']}"

    else:
        return f"ERROR - Múltiples roles encontrados con el nombre {rol['name']}"

def carga(usuario,clave,ruta_roles):
    sesion=sim(usuario,clave)

    tic()
    roles_df=leerRoles(ruta_roles)
    toc("Tiempo de carga")

    responses=[]

    for idx,rol in roles_df.iterrows():

        response=crearOModificarRol(sesion,rol)
        responses.append(response)
        print(response,"\n")

    roles_df["responses"]=responses
    return roles_df

if __name__ == "__main__":
    
    usuario=****
    clave=****
    path_roles="data/carga/rol_prueba_heredadas.csv"
    path_resultados="output/csv/role_output.csv"

    res=carga(usuario, clave, path_roles)
    res.to_csv(path_resultados,sep=****;")

    


