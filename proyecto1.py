#Proyecto 1 
#Juan Camilo Gómez-202220238
#Jerónimo Rueda-202223775

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns  
import geopandas as gpd
import requests
import json
import dash
from dash import dcc  # dash core components
from dash import html # dash html components
import plotly.express as px
import pandas as pd


df = pd.read_csv("Saber 11 Datos Valle.csv")
indicesviolencia = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx",sheet_name="Indices")
homicidios = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Homicidios")
lesionesp = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Lesiones Personales")
violencia_int = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Violencia Intrafamiliar")
delitos_sex = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Delitos Sexuales")
extorsion = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Extorsión")
amenazas = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Amenazas")
hurtos = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Hurtos")
secuestros = pd.read_excel("Violencia Valle del Cauca Indices con Página con todo junto.xlsx", sheet_name="Secuestro")
mapa_valle = gpd.read_file('valle.json')

##################################################################################################################
##################################################################################################################
##########################################FALTANTES Y REEMPLAZOS##################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################

mapaarreglo = {
    "Sin Estrato": 0,
    "Estrato 1": 1,
    "Estrato 2": 2,
    "Estrato 3": 3,
    "Estrato 4": 4,
    "Estrato 5": 5,
    "Estrato 6": 6
}

df["estrato_num"] = df["fami_estratovivienda"].map(mapaarreglo)


#df[df["fami_estratovivienda"]=="Sin Estrato"][["estrato_num", "fami_estratovivienda"]].head()

df[df["punt_lectura_critica"].isna()]["periodo"].value_counts()

df=df[df["punt_global"].notna()]
df=df.drop_duplicates()


df["estu_fechanacimiento"] = pd.to_datetime(
    df["estu_fechanacimiento"],
    format="%d/%m/%Y",
    errors="coerce"
)
#df["estu_fechanacimiento"].isna().sum()

#df["estu_fechanacimiento"].describe()

#df.loc[641382, ["estu_fechanacimiento","periodo"]]

df["año"]=df["periodo"].astype(str).str[:4]



ti_menoresedad = pd.to_datetime("01/01/" + (df["año"].astype(int) - 17).astype(str),format="%d/%m/%Y")

cc_mayoresedad = pd.to_datetime("01/01/" + (df["año"].astype(int) - 18).astype(str),format="%d/%m/%Y")

reemplazofechanac = df["estu_fechanacimiento"].isna() | (df["estu_fechanacimiento"].dt.year == 1900)

df.loc[reemplazofechanac, "estu_fechanacimiento"] = np.where(df.loc[reemplazofechanac, "estu_tipodocumento"].eq("TI"),ti_menoresedad.loc[reemplazofechanac],cc_mayoresedad.loc[reemplazofechanac])
#df.loc[df["estu_fechanacimiento"].isna(), "estu_fechanacimiento"] = np.where(df["estu_tipodocumento"] == "TI",ti_menoresedad,cc_mayoresedad)
#df[df["estu_fechanacimiento"].isna()][["estu_fechanacimiento","periodo","estu_tipodocumento"]][["periodo","estu_tipodocumento"]].value_counts() 

df=df[df["año"].astype(int)>2014]

#print(df["estu_fechanacimiento"].sort_values().head(50))
#print(df["estu_fechanacimiento"].sort_values().tail(10))

reemplazos = {
    "CALIMA": "CALIMA EL DARIEN",
    "CALIMA (DARIEN)": "CALIMA EL DARIEN",
    "BUGA": "GUADALAJARA DE BUGA",
    "JAMUNDÍ": "JAMUNDI",
    "ALCALÁ": "ALCALA",
    "ANDALUCÍA": "ANDALUCIA",
    "BOLÍVAR": "BOLIVAR",
    "EL ÁGUILA": "EL AGUILA",
    "GUACARÍ": "GUACARI",
    "RIOFRÍO": "RIOFRIO",
    "LA UNIÓN": "LA UNION",
    "TULUÁ": "TULUA"
}

df["cole_mcpio_ubicacion"] = df["cole_mcpio_ubicacion"].replace(reemplazos)



#df[["cole_cod_mcpio_ubicacion","estrato_num"]].groupby("cole_cod_mcpio_ubicacion").value_counts()
prom_estrato=(df.groupby("cole_cod_mcpio_ubicacion")["estrato_num"].transform("mean").round())

df["estrato_num"] = df["estrato_num"].fillna(prom_estrato).astype("Int64")
df["fami_estratovivienda"]=df["fami_estratovivienda"].fillna("Estrato"+prom_estrato.astype("string")).astype("string")

#print(prom_estrato)

#df[df["cole_bilingue"].isna()].describe()
#df[["cole_bilingue","estrato_num"]].groupby("cole_bilingue").value_counts()
df["cole_bilingue"] = df["cole_bilingue"].fillna("Desconocido")
df["cole_caracter"] = df["cole_caracter"].fillna("Desconocido")
df["cole_cod_dane_establecimiento"] = df["cole_cod_dane_establecimiento"].fillna("Desconocido (Instituto Tecnológico Gran Colombia)")
df["cole_area_ubicacion"] = df["cole_area_ubicacion"].fillna("RURAL")
df["cole_cod_dane_establecimiento"] = df["cole_area_ubicacion"].fillna("RURAL")
df["estu_cod_depto_presentacion"] = df["estu_cod_depto_presentacion"].fillna(df["estu_cod_reside_depto"])
df["estu_depto_presentacion"] = df["estu_depto_presentacion"].fillna(df["estu_depto_reside"])

df["estu_cod_mcpio_presentacion"] = df["estu_cod_mcpio_presentacion"].fillna(df["estu_cod_reside_mcpio"])
df["estu_cod_reside_depto"] = df["estu_cod_reside_depto"].fillna(df["cole_depto_ubicacion"])
df["estu_cod_reside_mcpio"] = df["estu_cod_reside_mcpio"].fillna(df["cole_mcpio_ubicacion"])
df["estu_depto_reside"] = df["estu_depto_reside"].fillna(df["estu_depto_presentacion"])
df["estu_genero"] = df["estu_genero"].fillna("Desconocido")
df["estu_mcpio_presentacion"] = df["estu_mcpio_presentacion"].fillna(df["cole_mcpio_ubicacion"])
df["estu_mcpio_reside"] = df["estu_mcpio_reside"].fillna(df["cole_mcpio_ubicacion"])

df["fami_cuartoshogar"] = df["fami_cuartoshogar"].fillna("Desconocido")
df["fami_educacionmadre"] = df["fami_educacionmadre"].fillna("Desconocido")
df["fami_educacionpadre"] = df["fami_educacionpadre"].fillna("Desconocido")
df["fami_personashogar"] = df["fami_personashogar"].fillna("Desconocido")
df["fami_tieneautomovil"] = df["fami_tieneautomovil"].fillna("No")
df["fami_tienecomputador"] = df["fami_tienecomputador"].fillna("No")
df["fami_tieneinternet"] = df["fami_tieneinternet"].fillna(df["fami_tienecomputador"])
df["fami_tienelavadora"] = df["fami_tienelavadora"].fillna("No")




#df[df["cole_area_ubicacion"].isna()].head()
#df[["cole_cod_dane_establecimiento","cole_cod_mcpio_ubicacion"]]["cole_cod_dane_establecimiento"].isna().groupby(df["cole_cod_mcpio_ubicacion"]).value_counts()
#df[df["cole_cod_dane_establecimiento"].isna()]["cole_nombre_establecimiento"].value_counts()
#df[df["desemp_ingles"].isna()]["estrato_num"].value_counts()
#df["fami_tienecomputador"].value_counts()

#df[["punt_ingles", "punt_matematicas", "punt_lectura_critica","punt_global"]].corr()["punt_ingles"]
corr_mat = df[["punt_ingles", "punt_matematicas", "punt_lectura_critica"]].corr()
c_mat = abs(corr_mat["punt_ingles"]["punt_matematicas"])
c_lec = abs(corr_mat["punt_ingles"]["punt_lectura_critica"])
suma_c = c_mat + c_lec
reemplazo = ((c_mat / suma_c) * df["punt_matematicas"] + (c_lec / suma_c) * df["punt_lectura_critica"])
df["punt_ingles"] = df["punt_ingles"].fillna(round(reemplazo, 0))


#df[df["desemp_ingles"].isna()]["punt_ingles"].describe()



"""
if df["punt_ingles"]<27:

    df["desemp_ingles"]=df["desemp_ingles"].fillna("A1")

elif df["punt_ingles"]<=40:
    df["desemp_ingles"]=df["desemp_ingles"].fillna("A2")
elif df["punt_ingles"]<55:
    df["desemp_ingles"]=df["desemp_ingles"].fillna("B1")
else:
    df["desemp_ingles"]=df["desemp_ingles"].fillna("B+")
"""

condiciones = [
    df["punt_ingles"] < 27,
    df["punt_ingles"] <= 40,
    df["punt_ingles"] < 55]
valores = ["A1", "A2", "B1"]
#df["desemp_ingles"].value_counts()

nivel_calc = np.select(condiciones, valores, default="B+")

df["desemp_ingles"] = df["desemp_ingles"].fillna(pd.Series(nivel_calc, index=df.index))


categorias= df.columns.tolist()
df["estu_cod_reside_depto"].replace({'VALLE': 76}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'CALI': 76001}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'GUADALAJARA DE BUGA': 76111}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'BUGALAGRANDE': 76113}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'EL CERRITO': 76248}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'JAMUNDÍ': 76364}, inplace=True)
df["estu_cod_reside_mcpio"].replace({'YUMBO': 76892}, inplace=True)
df["año"]=df["periodo"].astype(str).str[:4]

df=df[df["año"].astype(int)>2014]
#df.isna().sum()


#print(df.shape)

#(642592, 51)


#print(df.isna().sum())

##################################################################################################################
##################################################################################################################
##########################################PUNTAJES A VARIABLES CATEGÓRICAS########################################
##################################################################################################################
##################################################################################################################
##################################################################################################################

puntajes=df.copy()


puntajes["Puntaje area ubicacion"] = puntajes["cole_area_ubicacion"].map({"URBANO": 1, "RURAL": 0})
puntajes["Puntaje bilingue"] = puntajes["cole_bilingue"].map({"S": 1, "N": 0})
#puntajes["Puntaje calendario"] = puntajes["cole_calendario"].map({"A": 1, "B": 2,"OTROS": 3})
#puntajes["Puntaje caracter"] = puntajes["cole_caracter"].map({"TÉCNICO/ACADÉMICO": 1, "ACADÉMICO": 2,"TÉCNICO": 3,"NO APLICA": 4})
puntajes["Puntaje Genero col"] = puntajes["cole_genero"].map({"MIXTO": 1, "FEMENINO": 2,"MASCULINO": 3})
puntajes["Puntaje Jornada"] = puntajes["cole_jornada"].map({"MAÑANA": 1, "TARDE": 2,"COMPLETA": 3,"NOCHE": 4,"UNICA": 5,"SABATINA":6})
puntajes["Puntaje Naturaleza"] = puntajes["cole_naturaleza"].map({"OFICIAL": 1, "NO OFICIAL": 0})
puntajes["Puntaje Sede Principal"] = puntajes["cole_sede_principal"].map({"S": 1, "N": 0})
puntajes["Puntaje Investigación"] = puntajes["estu_estadoinvestigacion"].map({"PUBLICAR": 3, "VALIDEZ OFICINA JURÍDICA": 2,"PRESENTE CON LECTURA TARDIA":1,"NO SE COMPROBO IDENTIDAD DEL EXAMINADO":0})
#puntajes["Puntaje Genero"] = puntajes["estu_genero"].map({"M": 0, "F": 1})
puntajes["Puntaje Libertad"] = puntajes["estu_privado_libertad"].map({"S": 0, "N": 1})
puntajes["Puntaje Cuartos Hogar"] = puntajes["fami_cuartoshogar"].map({"Uno": 1, "Dos": 2,"Tres": 3,"Cuatro": 4,"Cinco": 5,"Seis":6,"Seis o mas": 6.5,"Siete": 7,"Ocho": 8,"Nueve": 9,"Diez o más": 10})

puntajes["Puntaje Educación Madre"] = puntajes["fami_educacionmadre"].map({"No Aplica":0,"No sabe":1,"Ninguno":2,"Primaria incompleta":3,
                                                                           "Primaria completa":4,"Secundaria (Bachillerato) incompleta":5,
                                                                           "Secundaria (Bachillerato) completa":6,"Técnica o tecnológica completa":7,
                                                                           "Técnica o tecnológica incompleta":8,"Educación profesional incompleta":9,
                                                                           "Educación profesional completa":10,"Postgrado":11})

puntajes["Puntaje Educación Padre"] = puntajes["fami_educacionpadre"].map({"No Aplica":0,"No sabe":1,"Ninguno":2,"Primaria incompleta":3,
                                                                           "Primaria completa":4,"Secundaria (Bachillerato) incompleta":5,
                                                                           "Secundaria (Bachillerato) completa":6,"Técnica o tecnológica completa":7,
                                                                           "Técnica o tecnológica incompleta":8,"Educación profesional incompleta":9,
                                                                           "Educación profesional completa":10,"Postgrado":11})

puntajes["Puntaje Personas Hogar"] = puntajes["fami_personashogar"].map({"Una": 1, "1 a 2":1.5,"Dos": 2,"Tres": 3,"3 a 4":3.5,"Cuatro": 4,"Cinco": 5,
                                                                         "5 a 6":5.5,"Seis": 6,"Siete": 7,"7 a 8":7.5,"Ocho": 8,"Nueve": 9,"9 o más":9.5,
                                                                         "Diez": 10,"Doce o más": 10})
puntajes["Puntaje Automóvil"] = puntajes["fami_tieneautomovil"].map({"Si": 1, "No": 0})
puntajes["Puntaje Computador"] = puntajes["fami_tienecomputador"].map({"Si": 1, "No": 0})

puntajes["Puntaje Lavadora"] = puntajes["fami_tienelavadora"].map({"Si": 1, "No": 0})
puntajes["Puntaje Desempeño ingles"] = puntajes["desemp_ingles"].map({"A-":0,"A1": 1, "A2": 2,"B1": 3,"B+": 4})


puntajes["desemp_ingles"].value_counts()

"""



"""

def normalizar(s):
    return (s.str.normalize("NFKD")
                .str.encode("ascii","ignore")
                .str.decode("utf-8").str.upper()
                .str.strip())





puntajes["cole_mcpio_ubicacion"] = (df["cole_mcpio_ubicacion"].pipe(normalizar))
puntajes["cole_mcpio_ubicacion"] = puntajes["cole_mcpio_ubicacion"].replace(["CALIMA (DARIEN)", "CALIMA"], "CALIMA EL DARIEN")

mapazonas= {
    # Zona Pacífico 
    "BUENAVENTURA": "Pacífico",

    # Zona Centro
    "CALIMA EL DARIEN": "Centro",
    "YOTOCO": "Centro",
    "SAN PEDRO": "Centro",
    "GUADALAJARA DE BUGA": "Centro",   
    "BUGA": "Centro",                  
    "GUACARI": "Centro",
    "GINEBRA": "Centro",
    "EL CERRITO": "Centro",

    # Zona Sur 
    "DAGUA": "Sur",
    "LA CUMBRE": "Sur",
    "VIJES": "Sur",
    "YUMBO": "Sur",
    "CALI": "Sur",
    "PALMIRA": "Sur",
    "CANDELARIA": "Sur",
    "PRADERA": "Sur",
    "FLORIDA": "Sur",
    "JAMUNDI": "Sur",
    "RESTREPO": "Sur",

    # Zona Norte
    "ALCALA": "Norte",
    "ULLOA": "Norte",
    "CARTAGO": "Norte",
    "ANSERMANUEVO": "Norte",
    "EL AGUILA": "Norte",
    "EL CAIRO": "Norte",
    "VERSALLES": "Norte",
    "ARGELIA": "Norte",
    "TORO": "Norte",
    "OBANDO": "Norte",
    "LA VICTORIA": "Norte",
    "LA UNION": "Norte",
    "ROLDANILLO": "Norte",
    "ZARZAL": "Norte",
    "BOLIVAR": "Norte",
    "TRUJILLO": "Norte",
    "RIOFRIO": "Norte",
    "EL DOVIO": "Norte",
    "ANDALUCIA": "Norte",
    "BUGALAGRANDE": "Norte",
    "TULUA": "Norte",
    "SEVILLA": "Norte",
    "CAICEDONIA": "Norte",
}

puntajes["Zona"] = puntajes["cole_mcpio_ubicacion"].map(mapazonas)
#print(municipios.groupby("Zona").size())
#municipios[municipios["Zona"].isna()]
#puntajes.head()

"""
puntajess.head()
#puntajess.info()


puntajess.corr(numeric_only=True)


sns.heatmap(puntajess.corr(numeric_only=True), cmap="coolwarm")
puntajess.corr(numeric_only=True)["punt_global"].sort_values(ascending=False)



puntajess[puntajess["Puntaje Automóvil"]==1][["Puntaje Automóvil","punt_global"]].describe()
"""




#sns.scatterplot(data=puntajes, x="Puntaje educacion padres", y="punt_global", hue="Zona")
#puntajes[puntajes["Puntaje educacion padres"].isna()].head()
"""
for i in puntajes.columns:
    promedio = puntajes[i].mean()

    puntajes[i] = puntajes[i].fillna(promedio)

municipiosss= df.copy()
"""


#puntajes_solonum.columns

puntajes["Puntaje bilingue"].fillna(puntajes["Puntaje bilingue"].mode()[0],inplace=True)

ordenlogico = ["Puntaje Educación Madre","Puntaje Educación Padre","Puntaje Personas Hogar","Puntaje Cuartos Hogar"]

for col in ordenlogico:
    puntajes[col] = puntajes[col].fillna(puntajes.groupby("fami_estratovivienda")[col].transform("mean"))



puntajes["año"] = puntajes["año"].astype(int)
puntajes["Puntaje educacion padres"] = puntajes["Puntaje Educación Padre"]+puntajes["Puntaje Educación Madre"]
puntajes["Puntaje recursos hogar"] = puntajes["Puntaje Automóvil"]+puntajes["Puntaje Computador"]+puntajes["Puntaje Lavadora"]
#puntajes["Puntaje Genero"] = puntajes["estu_genero"].map({"M": 0, "F": 1})


puntajes_solonum = puntajes.iloc[:, 45:].copy()
puntajes2020s=puntajes[puntajes["año"].astype(int)>=2020]

##################################################################################################################
##################################################################################################################
############################################Violencia#############################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################

##################################################################################################################
##############################################Índice Homicidios###################################################
##################################################################################################################

indice_largo = homicidios.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_homicidios")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_homicidios =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
#munihomicidios=muni_homicidios.groupby(["cole_mcpio_ubicacion"])
#munihomicidios.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
munihomicidios_agg = (muni_homicidios.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_homicidios=("indice_homicidios", "first"),**{col: (col, "mean") for col in categorias}))


limite_superior = munihomicidios_agg['indice_homicidios'].quantile(0.90)
# 2. Localizar la fila exacta (Municipio 'EL AGUILA' y Año 2022) y asignar el nuevo valor
# Usamos .loc[fila, columna]
munihomicidios_agg['indice_homicidios_ajustado'] = munihomicidios_agg['indice_homicidios'].clip(upper=limite_superior)






##################################################################################################################
##############################################Índice General Violencia############################################
##################################################################################################################


anios=[2020, 2021, 2022, 2023, 2024]
# Convertir 2020–2024 a numeric correctamente
for y in anios:
    indicesviolencia[y] = (indicesviolencia[y].astype(str))
    indicesviolencia[y] = pd.to_numeric(indicesviolencia[y], errors="coerce")
    
#indicesviolencia.isna().sum()
#indicesviolencia.head()


indice_largo = indicesviolencia.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024],var_name="año",value_name="indice_violencia")

indice_largo["año"] = indice_largo["año"].astype(int)

puntajes2020s["año"] = puntajes2020s["año"].astype(int)


muni_vio = puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")

categorias = ["punt_ingles","punt_matematicas","punt_sociales_ciudadanas","punt_c_naturales","punt_lectura_critica",
              "punt_global","Puntaje educacion padres","Puntaje recursos hogar"]

munivio_agg = (muni_vio.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_violencia=("indice_violencia", "first"),**{col: (col, "mean") for col in categorias}))












external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
