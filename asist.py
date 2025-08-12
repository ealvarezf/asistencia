import streamlit as st
import json
import pyodbc
import pandas as pd
from datetime import date

# Leer el archivo JSON
with open('rekon_config.json', 'r') as file:
    config = json.load(file)

SERVER = config["SERVER"]
DATABASE = config["DATABASE"]
USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]
KEYFEC = config["FECHA"]
SQ = "%"
DRIVER = "ODBC Driver 17 for SQL Server"  # Asegúrate de tener este driver instalado

try:
    # Crear la conexión a SQL Server
    conn = pyodbc.connect(
        f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
    )
    st.sidebar.write("✅ Conexión exitosa")
    KEYFEC = st.sidebar.date_input("Selecciona una fecha", value=date.today())

    # Crear un cursor para ejecutar la consulta
    cursor = conn.cursor()
        # consulta SQL para carga de cuadrillas
    query = """ SELECT '%' SquadName
                 UNION 
                SELECT DISTINCT SquadName FROM VW_REKON_EVENT
                 WHERE Fecha = ?
                 ORDER BY SquadName """
            # Ejecutar la consulta
    cursor.execute(query, (KEYFEC,)) 

        # Obtener los resultados listado de cuadrillas
    rows = cursor.fetchall()
    # Convertir resultados a lista
    opciones = [row[0] for row in rows]  # row[0] porque fetchall() devuelve tuplas

    # Crear selectbox con valores de la base de datos
    SQ = st.sidebar.selectbox("Selecciona una cuadrilla", opciones)
        # consulta SQL para carga de Ranchos
    query = """ SELECT '%' Rancho
                 UNION
                SELECT DISTINCT Rancho
                 FROM VW_REKON_EVENT
                WHERE Fecha = ?
                  AND Rancho IS NOT NULL
                ORDER BY Rancho """
            
            # Ejecutar la consulta
    cursor.execute(query, (KEYFEC,)) 

        # Obtener los resultados listado de cuadrillas
    rows = cursor.fetchall()
    opcranch = [row[0] for row in rows]  # row[0] porque fetchall() devuelve tuplas

    Ranch = st.sidebar.selectbox("Selecciona un Rancho", opcranch)


    #st.stop()
        # Escribir la consulta SQL
    query = """ SELECT Fecha, SquadName Cuadrilla, Person_Id Id, Person_Firstname Nombre, Person_Lastname Apellidos, Person_DocumentNumber IdNomina, NSS, Event_Date, Rancho, Event_Attributes      
                  FROM VW_REKON_EVENT
                 WHERE Fecha = ?
                   AND SquadName LIKE ?
                   AND Rancho LIKE ?
                 ORDER BY SquadName, Person_Firstname , Person_Lastname  """

        # Ejecutar la consulta
    cursor.execute(query, (KEYFEC, SQ, Ranch,)) 

        # Obtener los resultados
    rows = cursor.fetchall()

    # Verificar si hay resultados
    if rows:
        # Convertir a DataFrame
        df = pd.DataFrame.from_records(rows, columns=[desc[0] for desc in cursor.description])
        st.header("Asistencias Rekon")
        st.dataframe(df, use_container_width=True)
        st.write(f"Número de filas recuperadas: {len(rows)}")        
    else:
        st.write("⚠️ No se encontraron datos.")

        # Cerrar cursor y conexión
    cursor.close()
    conn.close()

except Exception as e:
    st.write("❌ Error al conectar a SQL Server:", e)
    
