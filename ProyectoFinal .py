# from tkinter import *
import tkinter as tk
import pandas as pd
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt

# Mensajes de Inicio
print("INICIO")
print("Preparando Datasets")

input("Presione ENTER para iniciar el Asistente\n")

# Ruta Relativa
ruta = os.path.abspath(os.path.dirname(__file__))
# Lectura del DataFrame Base
dfBase = pd.read_csv(ruta+"/BaseFiltrada.csv", encoding="utf8", parse_dates=True)
dfComuna = pd.read_csv(ruta +"/Comunas.csv", encoding="utf8")
fechaOrdenada = dfBase.sort_values(by="fecha_referencia_tipo_caso", ascending=True)
# OBTENER FECHAS COMO LISTA
# pd.date
fechas = list(fechaOrdenada["fecha_referencia_tipo_caso"].unique())

# LISTA DE CANTIDADES DE GRUPOS DE EDAD A DIFERENCIAR
cantidadGruposEdad = [1,2,3,4]


# VENTANA DE TKINTER
miVentana = tk.Tk()
miVentana.title("HERRAMIENTA CONSULTAS COVID-19 CABA")
miVentana.geometry("650x850")
miVentana.config(bg="lightpink") 
miVentana.config(cursor="hand")
miVentana.config(relief="sunken") 
miVentana.config(bd=25)


# VARIABLES TKINTER -- tk.StringVar(miVentana)

miVariable = tk.StringVar(miVentana)
miVariable.set(cantidadGruposEdad[0])


miVariableFechaD = tk.StringVar(miVentana)
miVariableFechaD.set(fechas[0])
miVariableFechaH = tk.StringVar(miVentana)
miVariableFechaH.set(fechas[-1])


# FUNCIONES PARA EL COMMAND DE CADA BOTÓN y FUNCIONES ACCESORIAS
def actualizarReportes():
    fechaHora = datetime.datetime.now()
   
    fechaTexto = fechaHora.strftime("%Y_%m_%d__%H-%M-%S")
    
    fechaInicio = miVariableFechaD.get()
    
    fechaFin = miVariableFechaH.get()
    
    dfFiltroFecha =  fechaOrdenada.loc[(fechaOrdenada["fecha_referencia_tipo_caso"] >= fechaInicio) & (fechaOrdenada["fecha_referencia_tipo_caso"] <= fechaFin)]
    
    # Actualiza el label "Versión: " con la fecha correspondiente

    # Ejecuta las funciones con los parámetros necesarios
    actualizarVisorVentana(dfFiltroFecha)
    crearPivots(dfFiltroFecha, fechaTexto)

def actualizarVisorVentana(dfFiltrado):
    # Actualizar todos los labels de la ventana

    
    #Ananlizados
    casosAnalizados = len(dfFiltrado)
    elementos["casos_analizados"].config(text="TOTAL DE CASOS ANALIZADOS: " + str(casosAnalizados))

    #Analizados Femeninos
    analizFem = len(dfFiltrado.loc[(dfFiltrado["sexo"]== "F")])
    elementos["analizados_femeninos"].config(text="Subotal Femenino: " + str(analizFem))
    
    # Analizados Masculinos
    analizMasc = len(dfFiltrado.loc[(dfFiltrado["sexo"]== "M")])
    elementos["analizados_masculinos"].config( text="Subotal Masculino: "+ str(analizMasc))
    
    #Confirmados
    casosConfirmados = len(dfFiltrado.loc[(dfFiltrado["clasificacion_resumen"]== "Confirmado")])
    elementos["casos_confirmados"].config(text="TOTAL DE CASOS CONFIRMADOS: " + str(casosConfirmados))
    # Confirmados Femeninos 
    casosConfirmadosF = len(dfFiltrado.loc[(dfFiltrado["sexo"]== "F") & (dfFiltrado["clasificacion_resumen"]=="Confirmado")])
    elementos["confirmados_femeninos"].config(text="Subtotal de Confirmados Femeninos: " + str(casosConfirmadosF))
    #Confirmados Masculinos
    casosConfirmadosM = len(dfFiltrado.loc[(dfFiltrado["sexo"]== "M") & (dfFiltrado["clasificacion_resumen"]=="Confirmado")])
    elementos["confirmados_masculinos"].config(text="Subtotal de Confirmados Masculinos: " + str(casosConfirmadosM))
    # AGREGAR ESOS VALORES A LA VENTANA


def crearPivots(dfFiltrado, fechaHora):
    #     # Averigüe la cantidad de grupos de edad deseados para el análisis
    cantidadElegida = miVariable.get()
    dfFiltrado["grupo_edad"] = pd.cut(dfFiltrado["edad"], bins=int(cantidadElegida)) # Utilice la funcion pd.cut()

    # Pivot por fecha y genere output como csv
    dfPivoteadoFechaGenero = pd.pivot_table(dfFiltrado, columns=["grupo_edad", "clasificacion_resumen"], index=["fecha_referencia_tipo_caso"], aggfunc="size", fill_value=0)
        
    dfPivoteadoFechaGenero.to_csv(ruta+ "/Output/" + fechaHora + "Casos_fecha_edad.csv", encoding="utf8")    
    
    
    dfPivoteadoComuna = dfPivoteado = pd.pivot_table(dfFiltrado, columns=["clasificacion_resumen"], index=["residencia_departamento_nombre"], aggfunc="size", fill_value=0)
    
    dfPivoteadoComuna.to_csv(ruta+ "/Output/" + fechaHora + "Resultados_Comuna.csv", encoding="utf8")   
    
    # Pivot por Comuna, MERGE con el dfBase de Comunas y  output como csv
     
    # Filas: comunas, columnas{tipo de caso, genero}
    
    dfFiltrado["Comuna"]= dfFiltrado["residencia_departamento_nombre"]
    
    dfPivoteadoEspecial =pd.pivot_table( dfFiltrado, columns=["clasificacion_resumen", "sexo"], index=["fecha_referencia_tipo_caso", "Comuna"], aggfunc="size", fill_value=0) 
    
    dfFusion = pd.merge(dfPivoteadoEspecial, dfComuna, on="Comuna")
    
    
    dfFusion.to_csv(ruta+ "/Output/" + fechaHora + "CasosPorComuna.csv", encoding="utf8" )


def graficoTemporal():

    plt.close('all')
    fechaInicio = miVariableFechaD.get()
    
    fechaFin = miVariableFechaH.get() 
    dfFiltroFecha =  fechaOrdenada.loc[(fechaOrdenada["fecha_referencia_tipo_caso"] >= fechaInicio) & (fechaOrdenada["fecha_referencia_tipo_caso"] <= fechaFin)]
    
    dfAgrupadoFecha = pd.pivot_table(dfFiltroFecha, index="fecha_referencia_tipo_caso", columns="clasificacion_resumen", aggfunc="size", fill_value=0)
    series = dfAgrupadoFecha[["Confirmado","Sospechoso","Descartado"]]
    
    series.plot.line()
    plt.show() 
   
    

def graficoPorEdades():
    plt.close('all')
    fechaInicio = miVariableFechaD.get()
    
    fechaFin = miVariableFechaH.get() 
    dfFiltroFecha =  fechaOrdenada.loc[(fechaOrdenada["fecha_referencia_tipo_caso"] >= fechaInicio) & (fechaOrdenada["fecha_referencia_tipo_caso"] <= fechaFin)]
    
    cantidadElegida = miVariable.get()
    dfFiltroFecha["grupo_edad"] = pd.cut(dfFiltroFecha["edad"], bins=int(cantidadElegida))
    
    dfGrupoEdad = dfFiltroFecha["grupo_edad"].value_counts()
    dfGrupoEdad.plot.pie(autopct='%2f') 
    plt.show()
    
  
    
# DICCIONARIO CON TODOS LOS ELEMENTOS (ORDENADOS)
elementos = {
"label1_Titulo": tk.Label(miVentana, text="Bienvenido/a a la Herramienta de Consultas COVID-19 CABA", font=("Verdana", 18), bg="lightpink"),

"label2A_FechaDesde":tk.Label(miVentana, text="Fecha Desde:",fg="cyan",font=("Verdana", 16), bg="lightpink"),
"menuFechaD": tk.OptionMenu(miVentana, miVariableFechaD, *fechas),
"label2B_FechaHasta":tk.Label(miVentana, text="Fecha hasta:", fg="cyan",font=("Verdana", 16), bg="lightpink"),
"menuFechaH": tk.OptionMenu(miVentana, miVariableFechaH, *fechas), 
"label3_GruposEdades": tk.Label(miVentana, text="Cantidad Grupos Edades \n", bg="lightpink"),
"miMenu": tk.OptionMenu(miVentana,miVariable, *cantidadGruposEdad),
"boton_ActualizarReportes": tk.Button(miVentana, text="Actualizar Reportes por Comuna y Fecha \n", command=actualizarReportes,  font=("Verdana", 16), fg="orange"),
"label_version": tk.Label(miVentana, text="VERSION:", fg="blue", bg="lightpink"),
"casos_analizados": tk.Label(miVentana, text="TOTAL DE CASOS ANALIZADOS: ", fg="blue", bg="lightpink"),
"analizados_femeninos": tk.Label(miVentana, text="Subotal Femenino: ", bg="lightpink", font=("Verdana", 16)),
"analizados_masculinos": tk.Label(miVentana, text="Subtotal Masculino: \n", bg="lightpink", font=("Verdana", 16)),
"casos_confirmados": tk.Label(miVentana, text="TOTAL DE CASOS CONFIRMADOS: \n", fg="blue", bg="lightpink", font=("Verdana", 16)),
"confirmados_femeninos": tk.Label(miVentana, text="Subtotal Femenino: \n", bg="lightpink", font=("Verdana", 16)),
"confirmados_masculinos": tk.Label(miVentana, text="Subtotal Masculino: \n ", bg="lightpink", font=("Verdana", 16)),
"boton_grafico1": tk.Button(miVentana, text="Generar Gráficos Temporal Total \n", command=graficoTemporal, font=("Verdana", 16), fg="violet"),
"boton_grafico2": tk.Button(miVentana, text="Generar Gráfico  de Distribución Grupos por edades\n", command=graficoPorEdades,  font=("Verdana", 16), fg="violet")

}

# "PACK" DE TODOS LOS ELEMENTOS DEL DICCIONARIO
for e in elementos.values():
    e.pack()
   
# MAINLOOP DE LA VENTANA

miVentana.mainloop()

