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
from dash.dependencies import Input, Output


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
df.columns = df.columns.str.lower()

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
df.columns = df.columns.str.lower()

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
categorias = ["punt_ingles","punt_matematicas","punt_sociales_ciudadanas","punt_c_naturales"
              ,"punt_lectura_critica","punt_global","Puntaje educacion padres","Puntaje recursos hogar"]
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

munihomicidios_agg['indice_homicidios_ajustado'] = munihomicidios_agg['indice_homicidios'].clip(upper=limite_superior)

##################################################################################################################
##############################################Índice Lesiones Personales##########################################
##################################################################################################################


indice_largo = lesionesp.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_lesiones_personales")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_lesionesp =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
munilesionesp=muni_lesionesp.groupby(["cole_mcpio_ubicacion"])
#munilesionesp.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
munilesionesp_agg = (muni_lesionesp.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_lesiones_personales=("indice_lesiones_personales", "first"),**{col: (col, "mean") for col in categorias}))

##################################################################################################################
##############################################Índice Violencia Intrafamiliar######################################
##################################################################################################################

indice_largo = violencia_int.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_violencia_intrafamiliar")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_violencia_int =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
muniviolencia_int=muni_violencia_int.groupby(["cole_mcpio_ubicacion"])
#muniviolencia_int.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
muniviolencia_int_agg = (muni_violencia_int.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_violencia_intrafamiliar=("indice_violencia_intrafamiliar", "first"),**{col: (col, "mean") for col in categorias}))

##################################################################################################################
##############################################Índice Delitos Sexuales#############################################
##################################################################################################################


indice_largo = delitos_sex.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_delitos_sexuales")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_delitos_sex =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
munidelitos_sex=muni_delitos_sex.groupby(["cole_mcpio_ubicacion"])
#munidelitos_sex.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
munidelitos_sex_agg = (muni_delitos_sex.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_delitos_sexuales=("indice_delitos_sexuales", "first"),**{col: (col, "mean") for col in categorias}))

##################################################################################################################
##############################################Índice Extorsión####################################################
##################################################################################################################


indice_largo = extorsion.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_extorsion")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_extorsion =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
muniext=muni_extorsion.groupby(["cole_mcpio_ubicacion"])
#muniext.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
muniext_agg = (muni_extorsion.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_extorsion=("indice_extorsion", "first"),**{col: (col, "mean") for col in categorias}))

##################################################################################################################
##############################################Índice Amenazas#####################################################
##################################################################################################################

indice_largo = amenazas.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_amenazas")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_amenazas =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
muni_amenazas_agrupadas=muni_amenazas.groupby(["cole_mcpio_ubicacion"])
#muni_amenazas_agrupadas.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
muni_amenazas_agg = (muni_amenazas.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_amenazas=("indice_amenazas", "first"),**{col: (col, "mean") for col in categorias}))

##################################################################################################################
##############################################Índice Hurtos#######################################################
##################################################################################################################


indice_largo = hurtos.melt(id_vars="cole_mcpio_ubicacion",value_vars=[2020, 2021, 2022, 2023, 2024]
                                     ,var_name="año",value_name="indice_hurtos")
        

indice_largo["año"] = indice_largo["año"].astype(int)
puntajes2020s["año"] = puntajes2020s["año"].astype(int)

muni_hurtos =puntajes2020s.merge(indice_largo,on=["cole_mcpio_ubicacion", "año"],how="left")
#print(muni_vio)
#muni_vio.shape
muni_hurtos_agrupados=muni_hurtos.groupby(["cole_mcpio_ubicacion"])
muni_hurtos_agrupados.describe()

#print(munihomicidios.corr(numeric_only=True)["indice_violencia"].sort_values(ascending=False))


#print(categorias)
muni_hurtos_agg = (muni_hurtos.groupby(["cole_mcpio_ubicacion", "año"], as_index=False).agg(Zona=("Zona", "first"),
                                indice_hurtos=("indice_hurtos", "first"),**{col: (col, "mean") for col in categorias}))






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


##################################################################################################################
##################################################################################################################
############################################ Mapa Valle ##########################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################





#arreglar datos
REEMPLAZOS = {
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
    "TULUÁ": "TULUA",
}

def normalizar(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.normalize("NFKD")
            .str.encode("ascii", "ignore")
            .str.decode("utf-8")
            .str.upper()
            .str.strip())

def limpiar_nombre_mpio(s: pd.Series) -> pd.Series:
    return normalizar(s).replace(REEMPLAZOS)


"""
#limpieza exhaustiva
df = df[df["punt_global"].notna()].drop_duplicates().copy()
df["año"] = df["periodo"].astype(str).str[:4].astype(int)
df = df[df["año"] > 2014].copy()
df["cole_mcpio_ubicacion"] = limpiar_nombre_mpio(df["cole_mcpio_ubicacion"])

indicesviolencia = indicesviolencia.copy()
indicesviolencia["cole_mcpio_ubicacion"] = limpiar_nombre_mpio(indicesviolencia["cole_mcpio_ubicacion"])

anios = [2020, 2021, 2022, 2023, 2024]
for y in anios:
    indicesviolencia[y] = pd.to_numeric(indicesviolencia[y], errors="coerce")

indice_largo = indicesviolencia.melt(
    id_vars="cole_mcpio_ubicacion",
    value_vars=anios,
    var_name="año",
    value_name="indice_violencia"
)
indice_largo["año"] = indice_largo["año"].astype(int)

#merges
puntajes2020s = df[df["año"] >= 2020].copy()

punt_agg = (puntajes2020s
            .groupby(["cole_mcpio_ubicacion", "año"], as_index=False)
            .agg(punt_global=("punt_global", "mean")))



muni_vio = puntajes2020s.merge(indice_largo, on=["cole_mcpio_ubicacion", "año"], how="left")

munivio_agg = (muni_vio.groupby(["cole_mcpio_ubicacion", "año"], as_index=False)
               .agg(
                   Zona=("Zona", "first"),
                   indice_violencia=("indice_violencia", "first"),
                   **{col: (col, "mean") for col in categorias}
               ))
"""


#geojson 
gdf = gpd.read_file("valle.json")

#cambiamos por si acaso
if gdf.crs is None:
    gdf = gdf.set_crs(epsg=4326)

gdf = gdf.to_crs(epsg=4326)

# arreglar geometrías inválidas o que fallan en los departamentos
try:
    gdf["geometry"] = gdf["geometry"].make_valid()
except Exception:
    gdf["geometry"] = gdf["geometry"].buffer(0)

gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()

# normalizar nombre
gdf["mpio_cnmbr"] = limpiar_nombre_mpio(gdf["mpio_cnmbr"])

"""
b = gdf.bounds.round(6)
print("bounds únicas:", len(b.drop_duplicates()))
print("top bounds duplicadas:\n", b.value_counts().head(10))

wkts = gdf.geometry.apply(lambda geom: geom.wkt[:200])
print("WKT únicas aprox:", wkts.nunique())
print("top WKT duplicadas:\n", wkts.value_counts().head(10))
"""
#hacerlo de manera mas robusta para que encuentre y llene y no busque y se rinda 
geojson_valle = json.loads(gdf.to_json())
for feat in geojson_valle["features"]:
    mpio = feat["properties"]["mpio_cnmbr"]
    feat["id"] = mpio

#por si acaso resivar
anioesp = 2022
map_df = munivio_agg[munivio_agg["año"] == anioesp].copy()
map_df["mpio_id"] = map_df["cole_mcpio_ubicacion"]

map_df["indice_violencia"] = pd.to_numeric(map_df["indice_violencia"], errors="coerce")
map_df["punt_global"] = pd.to_numeric(map_df["punt_global"], errors="coerce")

#print("No-NaN violencia:", map_df["indice_violencia"].notna().sum())
#print("No-NaN punt_global:", map_df["punt_global"].notna().sum())

map_df = (map_df.groupby("mpio_id", as_index=False)
                .agg(indice_violencia=("indice_violencia", "mean"),
                     punt_global=("punt_global", "mean")))

print("Municipios DF mapa:", map_df["mpio_id"].nunique(), " | Geo features:", len(geojson_valle["features"]))


#gráficos
fig_vio = px.choropleth_mapbox(
    map_df,
    geojson=geojson_valle,
    locations="mpio_id",
    featureidkey="id",
    color="indice_violencia",
    hover_name="mpio_id",
    mapbox_style="open-street-map",
    center={"lat": 4.2, "lon": -76.3},
    zoom=7,
    opacity=0.7,
    title=f"Índice de Violencia en el Valle ({anioesp})"
)
fig_vio.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
fig_vio.update_traces(marker_line_width=1, marker_line_color="black")

fig_punt = px.choropleth_mapbox(
    map_df,
    geojson=geojson_valle,
    locations="mpio_id",
    featureidkey="id",
    color="punt_global",
    hover_name="mpio_id",
    mapbox_style="open-street-map",
    center={"lat": 4.2, "lon": -76.3},
    zoom=7,
    opacity=0.7,
    title=f"Puntajes Globales Saber 11 ({anioesp})"
)
fig_punt.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
fig_punt.update_traces(marker_line_width=1, marker_line_color="black")

##################################################################################################################
##################################################################################################################
############################################ Preparación df_trampa ###############################################
##################################################################################################################
##################################################################################################################
##################################################################################################################



ORDEN_ESTRATO = [
    "Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4",
    "Estrato 5", "Estrato 6", "Sin Estrato"
]

ORDEN_EDU = [
    "Ninguno", "Primaria incompleta", "Primaria completa",
    "Secundaria (Bachillerato) incompleta", "Secundaria (Bachillerato) completa",
    "Técnica o tecnológica incompleta", "Técnica o tecnológica completa",
    "Educación profesional incompleta", "Educación profesional completa",
    "Postgrado", "No sabe", "No Aplica"
]

COLS_TRAMPA = [
    "fami_estratovivienda", "cole_naturaleza", "fami_educacionmadre",
    "fami_educacionpadre", "cole_bilingue", "cole_jornada",
    "cole_area_ubicacion", "fami_tieneinternet", "fami_tienecomputador",
    "fami_tienelavadora", "punt_ingles", "punt_matematicas",
    "punt_sociales_ciudadanas", "punt_c_naturales", "punt_lectura_critica",
    "punt_global"
]

df_trampa = df[COLS_TRAMPA].copy()

df_trampa["fami_estratovivienda"] = (
    df_trampa["fami_estratovivienda"]
    .astype("string").str.strip().fillna("Sin información")
)

for col in ["cole_bilingue", "cole_jornada", "cole_naturaleza",
            "cole_area_ubicacion", "fami_tieneinternet",
            "fami_tienecomputador", "fami_tienelavadora"]:
    df_trampa[col] = (
        df_trampa[col].astype("string").str.strip().str.upper().fillna("SIN INFO")
    )

for col in ["fami_educacionmadre", "fami_educacionpadre"]:
    df_trampa[col] = (
        df_trampa[col].astype("string").str.strip().fillna("Sin información")
    )

PUNTAJES_COLS = [
    "punt_ingles", "punt_matematicas", "punt_sociales_ciudadanas",
    "punt_c_naturales", "punt_lectura_critica", "punt_global"
]
for col in PUNTAJES_COLS:
    df_trampa[col] = pd.to_numeric(df_trampa[col], errors="coerce")

VARIABLES_X = {
    "Bilingüismo": {
        "col": "cole_bilingue",
        "orden": ["N", "S"],
        "labels": {"N": "No bilingüe", "S": "Bilingüe"}
    },
    "Jornada": {
        "col": "cole_jornada",
        "orden": ["MAÑANA", "TARDE", "COMPLETA", "UNICA", "NOCHE", "SABATINA"],
        "labels": {}
    },
    "Naturaleza del colegio": {
        "col": "cole_naturaleza",
        "orden": ["OFICIAL", "NO OFICIAL"],
        "labels": {"OFICIAL": "Oficial", "NO OFICIAL": "No oficial (Privado)"}
    },
    "Área (Urbano/Rural)": {
        "col": "cole_area_ubicacion",
        "orden": ["URBANO", "RURAL"],
        "labels": {"URBANO": "Urbano", "RURAL": "Rural"}
    },
    "Internet en el hogar": {
        "col": "fami_tieneinternet",
        "orden": ["SI", "NO"],
        "labels": {"SI": "Tiene internet", "NO": "No tiene internet"}
    },
    "Computador en el hogar": {
        "col": "fami_tienecomputador",
        "orden": ["SI", "NO"],
        "labels": {"SI": "Tiene computador", "NO": "No tiene computador"}
    },
    "Lavadora en el hogar": {
        "col": "fami_tienelavadora",
        "orden": ["SI", "NO"],
        "labels": {"SI": "Tiene lavadora", "NO": "No tiene lavadora"}
    },
    "Educación de la madre": {
        "col": "fami_educacionmadre",
        "orden": ORDEN_EDU,
        "labels": {}
    },
    "Educación del padre": {
        "col": "fami_educacionpadre",
        "orden": ORDEN_EDU,
        "labels": {}
    },
}

PUNTAJES_LABELS = {
    "punt_global": "Puntaje Global",
    "punt_matematicas": "Matemáticas",
    "punt_ingles": "Inglés",
    "punt_lectura_critica": "Lectura Crítica",
    "punt_c_naturales": "Ciencias Naturales",
    "punt_sociales_ciudadanas": "Sociales y Ciudadanas",
}

COLS_EDU_NUM = ["Puntaje Educación Madre", "Puntaje Educación Padre", "Puntaje educacion padres"]
for col in COLS_EDU_NUM:
    if col not in df_trampa.columns:
        df_trampa[col] = puntajes[col].values


##################################################################################################################
##################################################################################################################
############################################ Dash ################################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################





external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


#Layout Estático
"""
app.layout = html.Div([
    html.H1("Dashboard de Educación y Violencia - Valle del Cauca",
            style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([
        html.Div([dcc.Graph(id="graph-violencia", figure=fig_vio)], className="six columns"),
        html.Div([dcc.Graph(id="graph-puntaje", figure=fig_punt)], className="six columns"),
    ], className="row"),
])
"""

##################################################################################################################
##################################################################################################################
##################################################################################################################
#################################Layout con opciones para cambiar##################################
##################################################################################################################
##################################################################################################################
##################################################################################################################




# arreglar dfs para poder hacer graficos de escoger

categorias = ["punt_ingles","punt_matematicas","punt_sociales_ciudadanas","punt_c_naturales",
              "punt_lectura_critica","punt_global","Puntaje educacion padres","Puntaje recursos hogar"]

indices_dict = {
    "Homicidios": munihomicidios_agg.rename(columns={"indice_homicidios": "valor_indice"}),
    "Lesiones personales": munilesionesp_agg.rename(columns={"indice_lesiones_personales": "valor_indice"}),
    "Violencia intrafamiliar": muniviolencia_int_agg.rename(columns={"indice_violencia_intrafamiliar": "valor_indice"}),
    "Delitos sexuales": munidelitos_sex_agg.rename(columns={"indice_delitos_sexuales": "valor_indice"}),
    "Extorsión": muniext_agg.rename(columns={"indice_extorsion": "valor_indice"}),
    "Amenazas": muni_amenazas_agg.rename(columns={"indice_amenazas": "valor_indice"}),
    "Hurtos": muni_hurtos_agg.rename(columns={"indice_hurtos": "valor_indice"}),
    "Violencia (general)": munivio_agg.rename(columns={"indice_violencia": "valor_indice"}),}

indices_long = []
for nombre, dfi in indices_dict.items():
    tmp = dfi.copy()
    tmp["tipo_indice"] = nombre
    indices_long.append(tmp)

indices_long = pd.concat(indices_long, ignore_index=True)

indices_long["mpio_id"] = indices_long["cole_mcpio_ubicacion"]
indices_long["año"] = indices_long["año"].astype(int)
indices_long["valor_indice"] = pd.to_numeric(indices_long["valor_indice"], errors="coerce")


"""

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Fertility rate, total (births per woman)'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Life expectancy at birth, total (years)'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        id='year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    )
])



"""

# función que construye la tabla pivot para el heatmap 

def construir_heatmap(var_x_nombre, puntaje_col):
    cfg = VARIABLES_X[var_x_nombre]
    col_x = cfg["col"]
    orden_x = cfg["orden"]
    labels_x = cfg["labels"]

    tmp = df_trampa[["fami_estratovivienda", col_x, puntaje_col]].dropna(subset=[puntaje_col]).copy()

    # filtrar solo los valores con orden definido
    tmp = tmp[tmp[col_x].isin(orden_x)]
    tmp = tmp[tmp["fami_estratovivienda"].isin(ORDEN_ESTRATO)]

    tabla = pd.pivot_table(
        tmp,
        index="fami_estratovivienda",
        columns=col_x,
        values=puntaje_col,
        aggfunc="mean"
    )


    filas_presentes = [e for e in ORDEN_ESTRATO if e in tabla.index]
    cols_presentes = [c for c in orden_x if c in tabla.columns]
    tabla = tabla.reindex(index=filas_presentes, columns=cols_presentes)

    if labels_x:
        tabla.columns = [labels_x.get(c, c) for c in tabla.columns]

    return tabla


TAB2_LAYOUT = html.Div([

    html.H3("¿Qué pesa más en el Saber 11: características del colegio o socioeconómicas?",
            style={"textAlign": "center", "marginTop": "20px"}),
    

    html.Div([
        html.Div([
            html.Label("Variable a comparar con el estrato"),
            dcc.Dropdown(
                id="dd-var-x",
                options=[{"label": k, "value": k} for k in VARIABLES_X],
                value="Bilingüismo",
                clearable=False
            )
        ], className="six columns"),

        html.Div([
            html.Label("Puntaje a analizar"),
            dcc.Dropdown(
                id="dd-puntaje-trampa",
                options=[{"label": v, "value": k} for k, v in PUNTAJES_LABELS.items()],
                value="punt_global",
                clearable=False
            )
        ], className="six columns"),
    ], className="row", style={"marginBottom": "20px"}),

    dcc.Graph(id="graph-heatmap-trampa", style={"height": "65vh"}),

    html.Div(id="texto-insight-trampa",
             style={"textAlign": "center", "fontSize": "15px",
                    "color": "#333", "marginTop": "10px", "marginBottom": "20px"}),
    
    html.Hr(style={"margin": "30px 0"}),

    html.H4("Distribución de puntajes por estrato",
            style={"textAlign": "center"}),
    html.P(
        "¿Cómo se distribuyen los puntajes dentro de cada estrato? ",
        style={"textAlign": "center", "color": "#555", "fontSize": "14px",
               "maxWidth": "800px", "margin": "0 auto 20px auto"}
    ),

    html.Div([
        html.Div([
            html.Label("Puntaje a visualizar"),
            dcc.Dropdown(
                id="dd-puntaje-dist",
                options=[{"label": v, "value": k} for k, v in PUNTAJES_LABELS.items()],
                value="punt_global",
                clearable=False
            )
        ], className="six columns"),

        html.Div([
            html.Label("Tipo de gráfico"),
            dcc.RadioItems(
                id="radio-tipo-plot",
                options=[
                    {"label": "  Violín",  "value": "violin"},
                    {"label": "  Boxplot", "value": "box"},
                ],
                value="violin",
                labelStyle={"display": "inline-block", "marginRight": "20px"},
                style={"marginTop": "6px"}
            )
        ], className="six columns"),
    ], className="row", style={"marginBottom": "10px"}),

    dcc.Graph(id="graph-dist-estrato", style={"height": "60vh"}),

    html.Hr(style={"margin": "30px 0"}),

    html.H4("¿La educación de los padres puede compensar el estrato?",
            style={"textAlign": "center"}),
    html.P(
        "Cada punto es un municipio. El eje X muestra el nivel educativo "
        "promedio de los padres, el eje Y el puntaje. ",
        style={"textAlign": "center", "color": "#555", "fontSize": "14px",
               "maxWidth": "850px", "margin": "0 auto 20px auto"}
    ),

    html.Div([
        html.Div([
            html.Label("Educación a comparar"),
            dcc.RadioItems(
                id="radio-edu-scatter",
                options=[
                    {"label": "  Madre",  "value": "Puntaje Educación Madre"},
                    {"label": "  Padre",  "value": "Puntaje Educación Padre"},
                    {"label": "  Ambos", "value": "Puntaje educacion padres"},
                ],
                value="Puntaje educacion padres",
                labelStyle={"display": "inline-block", "marginRight": "20px"},
                style={"marginTop": "6px"}
            )
        ], className="six columns"),

        html.Div([
            html.Label("Puntaje a visualizar"),
            dcc.Dropdown(
                id="dd-puntaje-scatter",
                options=[{"label": v, "value": k} for k, v in PUNTAJES_LABELS.items()],
                value="punt_global",
                clearable=False
            )
        ], className="six columns"),
    ], className="row", style={"marginBottom": "10px"}),

    html.Div([
        html.Label("Mostrar estratos:"),
        dcc.Checklist(
            id="check-estratos",
            options=[{"label": f"  {e}", "value": e} for e in ORDEN_ESTRATO],
            value=["Estrato 1","Estrato 2","Estrato 3",
                   "Estrato 4","Estrato 5","Estrato 6"],
            inline=True,
            labelStyle={"marginRight": "15px"}
        )
    ], style={"marginBottom": "15px"}),

    dcc.Graph(id="graph-scatter-edu", style={"height": "60vh"}),
])






app.layout = html.Div([

    html.H1("Dashboard Educación y Violencia — Valle del Cauca",
            style={"textAlign": "center", "marginBottom": "10px"}),

    dcc.Tabs(id="tabs-main", value="tab-violencia", children=[

        dcc.Tab(label="Violencia y Resultados", value="tab-violencia", children=[
            html.Div([

                html.Div([
                    html.Div([
                        html.Label("Seleccione índice de violencia"),
                        dcc.Dropdown(
                            id="dd-indice",
                            options=[
                                {"label": "Índice Violencia General",      "value": "indice_violencia"},
                                {"label": "Índice Homicidios",             "value": "indice_homicidios"},
                                {"label": "Índice Lesiones Personales",    "value": "indice_lesiones_personales"},
                                {"label": "Índice Violencia Intrafamiliar","value": "indice_violencia_intrafamiliar"},
                                {"label": "Índice Delitos Sexuales",       "value": "indice_delitos_sexuales"},
                                {"label": "Índice Extorsión",              "value": "indice_extorsion"},
                                {"label": "Índice Amenazas",               "value": "indice_amenazas"},
                                {"label": "Índice Hurtos",                 "value": "indice_hurtos"},
                            ],
                            value="indice_violencia",
                            clearable=False
                        )
                    ], className="six columns"),

                    html.Div([
                        html.Label("Categoría del Saber 11"),
                        dcc.Dropdown(
                            id="dd-puntaje",
                            options=[{"label": c.replace("_"," ").title().replace("Punt ",""), "value": c}
                                     for c in categorias],
                            value="punt_global",
                            clearable=False
                        )
                    ], className="six columns"),
                ], className="row"),

                html.Br(),

                html.Div([
                    html.Div([dcc.Graph(id="graph-violencia")], className="six columns"),
                    html.Div([dcc.Graph(id="graph-puntaje")],   className="six columns"),
                ], className="row"),

                html.Br(),
                dcc.Graph(id="graph-corr", style={"height": "70vh"}),
                html.Div(id="texto-correlacion",
                         style={"textAlign": "center", "fontSize": "22px",
                                "fontWeight": "bold", "marginTop": "10px"})
            ], style={"padding": "20px"})
        ]),

        dcc.Tab(label="Trampa del Estrato", value="tab-trampa", children=[
            TAB2_LAYOUT
        ]),
    ])
])
"""

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-type', 'value'),
     Input('year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name, 
                     type='linear' if xaxis_type == 'Linear' else 'log') 

    fig.update_yaxes(title=yaxis_column_name, 
                     type='linear' if yaxis_type == 'Linear' else 'log') 

    return fig


if __name__ == '__main__':
    app.run(debug=True)
"""

@app.callback(
    Output("graph-violencia", "figure"),
    Output("graph-puntaje", "figure"),
    Output("graph-corr", "figure"),
    Output("texto-correlacion", "children"),
    Input("dd-indice", "value"),
    Input("dd-puntaje", "value")
)

def mapas_diferentes(tipo_indice, tipo_puntaje):

    #se pone fijo pq no hay suficientes datos para que en 2021 o 2020 se
    #pueda armar el mapa completo
    aniooo = 2022 

    
    if tipo_indice == "indice_violencia":

        df_base = munivio_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Violencia General 2022 "

    elif tipo_indice == "indice_homicidios":

        df_base = munihomicidios_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Homicidios 2022 "


    elif tipo_indice == "indice_lesiones_personales":

        df_base = munilesionesp_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Lesiones Personales 2022 "

    elif tipo_indice == "indice_violencia_intrafamiliar":

        df_base = muniviolencia_int_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Violencia Intrafamiliar 2022 "

    elif tipo_indice == "indice_delitos_sexuales":

        df_base = munidelitos_sex_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Delitos Sexuales 2022 "

    elif tipo_indice == "indice_extorsion":

        df_base = muniext_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Extorsión 2022 "

    elif tipo_indice == "indice_amenazas":

        df_base = muni_amenazas_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Amenazas 2022 "

    else:

        df_base = muni_hurtos_agg
        titulo= "Mapa de Calor Valle del Cauca: Índice Hurtos 2022 "

    dff = df_base[df_base["año"] == aniooo].copy()
    dff["mpio_id"] = dff["cole_mcpio_ubicacion"]


    #Mapa Violencia
    fig_vio = px.choropleth_mapbox(
        dff,
        geojson=geojson_valle,
        locations="mpio_id",
        featureidkey="id",
        color=tipo_indice,
        hover_name="mpio_id",
        mapbox_style="open-street-map",
        center={"lat": 4.2, "lon": -76.3},
        zoom=7,
        opacity=0.7,
        title=titulo)


    fig_vio.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig_vio.update_traces(marker_line_width=1, marker_line_color="black")


    #Mapa Puntajes
    fig_punt = px.choropleth_mapbox(
        dff,
        geojson=geojson_valle,
        locations="mpio_id",
        featureidkey="id",
        color=tipo_puntaje,
        hover_name="mpio_id",
        mapbox_style="open-street-map",
        center={"lat": 4.2, "lon": -76.3},
        zoom=7,
        opacity=0.7,
        color_continuous_scale="cividis",
        title=f"{tipo_puntaje.replace('_',' ').replace('punt','').title()} ({aniooo})")

    fig_punt.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    fig_punt.update_traces(marker_line_width=1, marker_line_color="black")




    df_dispersion = df_base.copy()
    df_dispersion["mpio"] = df_dispersion["cole_mcpio_ubicacion"]
    df_dispersion["año"] =  pd.to_numeric(df_dispersion["año"], errors="coerce")

    columnas=["mpio","año","Zona"]

    dispersion_df_agrup = (df_dispersion
        .groupby("mpio", as_index=False)
        .agg(
            Zona=("Zona", "first"),
            x_puntaje=(tipo_puntaje, "mean"),
            y_indice=(tipo_indice, "mean"),
        ))

    fig_corr = px.scatter(
        dispersion_df_agrup,
        x="x_puntaje",
        y="y_indice",
        color="Zona",
        hover_name="mpio",   
        hover_data={"Zona": True,"x_puntaje": ":.2f","y_indice": ":.2f","mpio": False},                
        opacity=0.75,
        title=f"Correlación entre {tipo_puntaje.replace('_',' ').replace('punt','').title()} y {tipo_indice.replace('_',' ').replace('indice','Índice').title()}",
        labels=({"x_puntaje": tipo_puntaje.replace("_"," ").replace("punt","").title(),
                "y_indice":  tipo_indice.replace("_"," ").replace("indice","Índice").title()}))

    

    
    fig_corr.update_layout(height=650, margin={"r":30,"t":90,"l":60,"b":60})
    numero = dispersion_df_agrup["x_puntaje"].corr(dispersion_df_agrup["y_indice"])
    texto_corr = f"Correlación = {numero:.3f}"

    return fig_vio, fig_punt, fig_corr, texto_corr


@app.callback(
     Output("graph-heatmap-trampa", "figure"),
     Output("texto-insight-trampa", "children"),
     Input("dd-var-x", "value"),
     Input("dd-puntaje-trampa", "value")
 )
def actualizar_heatmap_trampa(var_x_nombre, puntaje_col):
     tabla = construir_heatmap(var_x_nombre, puntaje_col)

     puntaje_label = PUNTAJES_LABELS.get(puntaje_col, puntaje_col)

     fig = px.imshow(
         tabla,
         color_continuous_scale="YlOrRd",
         aspect="auto",
         text_auto=".1f",
         labels={"x": var_x_nombre, "y": "Estrato", "color": puntaje_label},
         title=f"{puntaje_label} promedio por Estrato × {var_x_nombre}"
     )
     fig.update_layout(
         margin={"t": 80, "b": 60, "l": 120, "r": 40},
         coloraxis_colorbar=dict(title=puntaje_label),
         xaxis_title=var_x_nombre,
         yaxis_title="Estrato socioeconómico",
         font=dict(size=13)
     )
     fig.update_xaxes(tickangle=-20)

     try:
         diff_var = tabla.max(axis=1).mean() - tabla.min(axis=1).mean()
         fila_e1 = tabla.loc["Estrato 1"].mean() if "Estrato 1" in tabla.index else None
         fila_e6 = tabla.loc["Estrato 6"].mean() if "Estrato 6" in tabla.index else None
         diff_estrato = (fila_e6 - fila_e1) if (fila_e1 and fila_e6) else None

         if diff_estrato is not None:
             insight = (
                 f"Diferencia media por {var_x_nombre}: {diff_var:.1f} pts   |   "
                 f"Diferencia Estrato 1 vs Estrato 6: {diff_estrato:.1f} pts"
             )
         else:
             insight = f"Diferencia media por {var_x_nombre}: {diff_var:.1f} pts"
     except Exception:
         insight = ""

     return fig, insight


@app.callback(
    Output("graph-dist-estrato", "figure"),
    Input("dd-puntaje-dist", "value"),
    Input("radio-tipo-plot", "value")
)
def actualizar_dist_estrato(puntaje_col, tipo_plot):
    tmp = df_trampa[["fami_estratovivienda", puntaje_col]].dropna().copy()
    tmp = tmp[tmp["fami_estratovivienda"].isin(ORDEN_ESTRATO)]

    tmp["fami_estratovivienda"] = pd.Categorical(
        tmp["fami_estratovivienda"],
        categories=ORDEN_ESTRATO,
        ordered=True
    )
    tmp = tmp.sort_values("fami_estratovivienda")

    puntaje_label = PUNTAJES_LABELS.get(puntaje_col, puntaje_col)

    if tipo_plot == "violin":
        fig = px.violin(
            tmp,
            x="fami_estratovivienda",
            y=puntaje_col,
            color="fami_estratovivienda",
            box=True,
            points=False,
            category_orders={"fami_estratovivienda": ORDEN_ESTRATO},
            labels={
                "fami_estratovivienda": "Estrato",
                puntaje_col: puntaje_label
            },
            title=f"Distribución de {puntaje_label} por Estrato",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
    else:
        fig = px.box(
            tmp,
            x="fami_estratovivienda",
            y=puntaje_col,
            color="fami_estratovivienda",
            points=False,
            category_orders={"fami_estratovivienda": ORDEN_ESTRATO},
            labels={
                "fami_estratovivienda": "Estrato",
                puntaje_col: puntaje_label
            },
            title=f"Distribución de {puntaje_label} por Estrato",
            color_discrete_sequence=px.colors.sequential.Viridis
        )

    fig.update_layout(
        showlegend=False,
        margin={"t": 70, "b": 60, "l": 60, "r": 30},
        xaxis_title="Estrato socioeconómico",
        yaxis_title=puntaje_label,
        font=dict(size=13)
    )

    return fig    



@app.callback(
    Output("graph-scatter-edu", "figure"),
    Input("radio-edu-scatter", "value"),
    Input("dd-puntaje-scatter", "value"),
    Input("check-estratos", "value")
)
def actualizar_scatter_edu(col_edu, puntaje_col, estratos_seleccionados):
    cols_needed = ["fami_estratovivienda", "cole_mcpio_ubicacion", col_edu, puntaje_col]

    tmp = puntajes[cols_needed].dropna().copy()
    tmp = tmp[tmp["fami_estratovivienda"].isin(ORDEN_ESTRATO)]
    tmp = tmp[tmp["fami_estratovivienda"].isin(estratos_seleccionados)]


    agg = (tmp.groupby(["cole_mcpio_ubicacion", "fami_estratovivienda"], as_index=False)
              .agg(
                  edu_promedio=(col_edu, "mean"),
                  puntaje_promedio=(puntaje_col, "mean"),
                  n=("fami_estratovivienda", "count")
              ))

    puntaje_label = PUNTAJES_LABELS.get(puntaje_col, puntaje_col)
    edu_label = col_edu.replace("Puntaje ", "")

    fig = px.scatter(
        agg,
        x="edu_promedio",
        y="puntaje_promedio",
        color="fami_estratovivienda",
        size="n",
        hover_name="cole_mcpio_ubicacion",
        hover_data={
            "edu_promedio": ":.2f",
            "puntaje_promedio": ":.1f",
            "n": True,
            "fami_estratovivienda": True
        },
        category_orders={"fami_estratovivienda": ORDEN_ESTRATO},
        color_discrete_map={
            "Estrato 1": "#d62728",
            "Estrato 2": "#ff7f0e",
            "Estrato 3": "#ffd700",
            "Estrato 4": "#2ca02c",
            "Estrato 5": "#1f77b4",
            "Estrato 6": "#9467bd",
            "Sin Estrato": "#8c564b",
        },

        labels={
            "edu_promedio": f"Nivel educativo ({edu_label})",
            "puntaje_promedio": puntaje_label,
            "fami_estratovivienda": "Estrato",
            "n": "N° estudiantes"
        },
        title=f"{puntaje_label} vs Educación ({edu_label}) por municipio y estrato",
        trendline="ols",
        trendline_scope="overall"
    )

    fig.update_layout(
        margin={"t": 70, "b": 60, "l": 70, "r": 30},
        legend_title="Estrato",
        font=dict(size=13)
    )

    return fig



if __name__ == '__main__':
    app.run(debug=True)
