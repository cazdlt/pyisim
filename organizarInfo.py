# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd

#obtener info
info_path="C:\\Users\\CamiloZamora\\Documents\\Colpensiones\\Configs\\Integraciones\\Heredadas adaptador\\adaptador\\Información Técnica Heredadas.xlsx"
df=pd.read_excel(info_path,sheet_name=[0, 1],usecols="A:G")
info_df=df[0].copy().dropna(subset=['Nombre de la Aplicación'])
info_df["Nombre de la Aplicación"]=info_df["Nombre de la Aplicación"].apply(lambda x: x.strip())
nombres_s=df[1].loc[:,["Nombre aplicación"]].squeeze()

nombres_s.head()


# %%
app=****

# Haciendo pruebas con:
    # HISTORIA LABORAL TRADICIONAL VERIFICA
    # Consulta_De_Pagos
    # Modican_Consulta
    # PERFIL_CONSULTA_NEL
    # Consdnc
    # Autoliss_Consultor
    # VERIGRE 

try:
    df_search=info_df[info_df["AMBIENTE BASE DE DATOS"]=="SYBASE"].set_index("Nombre de la Aplicación")
    df_app=****[app]
    dbs=df_app["Base Datos"].str.upper()
    roles=df_app["Roles"].dropna().apply(lambda x: x.split("\n")).explode().str.upper()
    grupos=df_app["GRUPOS"].dropna().astype(int).astype(str)

    alias_name=""
    try:
        alias_idx=[db.lower() for db in dbs].index("hltradicional")
        alias_name=dbs.iloc[alias_idx]
        dbs=dbs.mask(lambda x: x==alias_name).dropna()
        #print(f"Alias:",alias_name)
    except ValueError:
        pass

    dbs_salida="'"+dbs+"'"
    dbs_str=', '.join(dbs_salida)

    script_dbs=\
f"""databasenames=[{dbs_str}]
aliases=[{alias_name}]

user=****[0]

ret=[]
for(var i=0;i<databasenames.length;i++){{
    access=databasenames[i].toUpperCase()+":user:public:"+user
    ret.push(access)
}}

for(var i=0;i<aliases.length;i++){{
    access=aliases[i].toUpperCase()+":alias:dbo"
    ret.push(access)
}}
return ret"""

    print("Roles Sybase:",", ".join(roles))
    print("Grupos sabass:",", ".join(grupos.to_list()))
    if "historia laboral" in app.lower():
        print("Grupos HL o HLT:",app)
    print("Bases de datos Sybase:\n"+script_dbs)
except KeyError:
    print("No posee titularidades de Sybase")

try:
    #df_search=info_df["SQL SERVER " == info_df["AMBIENTE BASE DE DATOS"]].set_index("Nombre de la Aplicación")
    df_search=info_df.loc["SQL SERVER " == info_df["AMBIENTE BASE DE DATOS"]].set_index("Nombre de la Aplicación")
    df_app=****[[app]]
    dbs=df_app["Base Datos"].str.upper()
    roles=df_app[["Base Datos","Roles"]].dropna()

    dbs_str=', '.join("'"+dbs+"'")

    roles_str=", ".join(roles["Base Datos"].str.upper()+":"+roles["Roles"].str.upper())

    script_dbs=\
f"""databasenames=[{dbs_str}]

user=****[0]

ret=[]
for(var i=0;i<databasenames.length;i++){{
    access=databasenames[i].toUpperCase()+":"+user
    ret.push(access)
}}

return ret"""

    print("Roles SQL:",roles_str)
    print("Bases de datos SQL:\n"+script_dbs)
except KeyError:
    print("\nNo posee titularidades de SQL Server")


# %%


