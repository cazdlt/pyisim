import pandas as pd
from simsoap import sim
import numpy as np
import pprint
from isim_classes import ProvisioningPolicy
from tictoc import tic,toc
import re

def construir_attrs(titularidades_df):
    """
    Recibe un dataframe con información de parámetros de atributos de un servicio para una política de suministro
    Organiza en un dict para procesarlos a XML
    """

    # print(entitlements_df)
    # siempre hay solo uno
    entitlements_df=titularidades_df.copy()
    servicio = entitlements_df["nombre_servicio"].unique()

    auto = entitlements_df["automatico"].unique()
    assert len(auto) == 1, "Todo el servicio debe ser o manual o automático."

    flujo = entitlements_df["flujo"].unique()
    #print(servicio,flujo)
    assert len(flujo) == 1, "Todo el servicio debe tener el mismo flujo."

    atributos = entitlements_df.drop(["nombre_politica", "nombre_servicio", "automatico","flujo"], axis=1).set_index(
        "nombre_atributo")  # quita columnas que sobran
    atributos["valor"] = atributos.apply(lambda row: [s.strip() for s in str(row["valor"]).split(",")] if "return " not in row["valor"] else [row["valor"]], axis=1)  # vuelve atributos multivalor a lista
    atributos["enforcement"] = atributos.apply(lambda row: str(row["enforcement"]).lower(), axis=1)  # vuelve atributos multivalor a lista


    atributos.rename(columns={"valor": "values"}, inplace=True)

    atributos_dict = atributos.to_dict('index')
    atributos_dict["auto"] = auto[0]
    
    atributos_dict["flujo"] = flujo[0] if isinstance(flujo[0],str) else ""

    return atributos_dict

def leerTitularidades(csv_filename):
    """
    Recibe la ruta a un CSV con información de políticas de suministro (ver pp.csv)
    Devuelve dict organizado con info de estas para procesar a XML
    """
    csv_df = pd.read_csv(csv_filename, sep=****;",encoding="utf8")
    csv_df["nombre_politica"]=csv_df["nombre_politica"].apply(lambda r: re.sub("\s"," ",r)) #error raro \xa0

    nombres_politica = csv_df["nombre_politica"].unique()
    politicas = {}
    # print(csv_df)
    for politica in nombres_politica:
        politica_df = csv_df[csv_df["nombre_politica"] == politica]
        attrs_serie = politica_df.groupby(
            "nombre_servicio").apply(construir_attrs)

        attrs_dict = attrs_serie.to_dict()
        politicas[politica] = attrs_dict
        #print(attrs_serie)

    return politicas

def leerPoliticas(csv_filename):

    politicas = pd.read_csv(csv_filename, sep=****;",index_col="nombre",comment="#").astype(str) 
    politicas["roles"]=politicas["roles"].apply(lambda x: x.split(","))
    politicas["nombre"]=politicas.index

    politicas=politicas.rename({
        "roles":"memberships",
        "nombre":"name",
        "descripcion":"description",
        "prioridad":"priority"
    },axis=1)

    # politicas["servicios_auto"]=politicas["servicios_auto"].apply(lambda x: x.split(",") if x != "nan" else None)
    # politicas["servicios_manual"]=politicas["servicios_manual"].apply(lambda x: x.split(",") if x != "nan" else None)

    return politicas

def crearOModificarPolitica(sesion,politica,entitlements):
    """
       Primero busca (por nombre)
            Si no lo encuentra, lo crea
            Si lo encuentra, lo modifica
    """

    pol=politica.copy()
    # pp=****(sesion,politica.name,politica.descripcion,entitlements,politica.roles,politica.ou)
    
    try:
        wsou=****(pol["ou"])
    except Exception as e:
        return f"ERROR - {str(e)} - {pol.name}"

    found=sesion.buscarPoliticaSuministro(wsou,pol.name,find_unique=False)
    
    if len(found)==0:
        print(f"Creando política {pol.name}")
        try:
            tic()
            pp=****(sesion=sesion,entitlements=entitlements,**pol.to_dict())
            toc("Tiempo de creación")

            tic()
            r=pp.crearEnSIM(sesion)        
            toc("Tiempo de respuesta")
            return f"CREADO - {r['subject']} - Solicitud {r['requestId']}"
        except Exception as e:
            return f"ERROR - {str(e)} - {pol.name}"

    elif len(found)==1:
        print(f"Política encontrada, actualizando {pol.name}")
        try:
           
            tic()
            pp=****(sesion=sesion,entitlements=entitlements,**pol.to_dict())
            toc("Tiempo de creación")

            pp_found=found[0]
            tic()
            r=pp.modificarEnSIM(sesion,pp_found)
            toc("Tiempo de respuesta modificación")
        except Exception as e:
            return f"ERROR - {str(e)} - {pol.name}"

        return f"ACTUALIZADO   - {r['subject']} - Solicitud {r['requestId']}"
    else:
        return f"ERROR - Múltiples políticas encontradas con el nombre {pol['name']}"

def carga(usuario,clave,ruta_titularidades,ruta_politicas):
    sesion=sim(usuario,clave)

    tic()
    entitlements=leerTitularidades(ruta_titularidades)
    politicas=leerPoliticas(ruta_politicas)
    toc("Tiempo de carga")

    responses=[]
    for nombre,politica in politicas.iterrows():
       
        try:
            titularidades=entitlements[nombre]
            if not titularidades:
                raise KeyError
        except KeyError:
            response = f"ERROR - No se han encontrado titularidades para {nombre}"
        else:    
            #print(titularidades)
            response=crearOModificarPolitica(sesion,politica,titularidades)
            
        print(response,"\n")
        responses.append(response)

    politicas["responses"]=responses

    return politicas

if __name__ == "__main__":

    usuario=****
    clave=****
    path_entitlements="data/carga/titularidad_prueba_perfiles.csv"
    path_politicas="data/carga/politica_prueba_heredadas.csv"
    path_resultados="output/csv/out_pp_corrdnc.csv"


    res=carga(usuario,clave,path_entitlements,path_politicas)

    res.to_csv(path_resultados,sep=****;")

    

    
    
    