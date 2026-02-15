#Proyecto 1 
#Juan Camilo Gómez-202220238
#Jerónimo Rueda-202223775

import numpy as np
import pandas as pd 

df = pd.read_csv("Saber 11 Datos Valle.csv")

#print(df.shape)

#(642592, 51)


print(df.isna().sum())

