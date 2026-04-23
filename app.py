import streamlit as st
import pandas as pd
import os

archivo = "datos_estudiantes.xlsx"

# ----------------------------
# Crear archivo si no existe
# ----------------------------
if not os.path.exists(archivo):
    columnas = [
        "Nombre","Apellidos","Sexo","Fecha Nac","Edad","Direccion",
        "Deportes","Identidad","Curso","Año",
        "Talla","Peso","Envergadura","IMC",
    ]

    pruebas = [
        "Cooper","Ruffer","Burpee","Course",
        "Flxb Brazos","Flxb Piernas","Flxb Tronco","Flxb Profunda",
        "Fz Brazos","Fz Vertical","Fz Horizontal","Fz Abdominal",
        "Fz Balon","Coordinacion","Velocidad","Agilidad"
    ]

    for p in pruebas:
        columnas.append(f"{p}_Marca")
        columnas.append(f"{p}_Nota")

    columnas.append("Nota Media")
    columnas.append("Lesiones")

    df = pd.DataFrame(columns=columnas)
    df.to_excel(archivo, index=False)

# ----------------------------
# FORMULARIO
# ----------------------------
st.title("Valoración Física")

with st.form("formulario"):
    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    sexo = st.selectbox("Sexo", ["H", "M"])
    fecha = st.date_input("Fecha de nacimiento")
    edad = st.number_input("Edad", 10, 30)
    direccion = st.text_input("Dirección")
    deportes = st.text_input("Deportes")
    identidad = st.text_input("Tarjeta de identidad")
    curso = st.text_input("Curso")
    año = st.number_input("Año", 2020, 2030)

    st.subheader("Medidas")
    talla = st.number_input("Talla (m)")
    peso = st.number_input("Peso (kg)")
    envergadura = st.number_input("Envergadura (cm)")
    imc = peso / (talla**2) if talla > 0 else 0

    st.subheader("Pruebas")
    pruebas_nombres = [
        "Cooper","Ruffer","Burpee","Course",
        "Flxb Brazos","Flxb Piernas","Flxb Tronco","Flxb Profunda",
        "Fz Brazos","Fz Vertical","Fz Horizontal","Fz Abdominal",
        "Fz Balon","Coordinacion","Velocidad","Agilidad"
    ]

    marcas = {}
    for p in pruebas_nombres:
        marcas[p] = st.number_input(f"{p} (marca)", value=0.0)

    lesiones = st.text_area("Lesiones")

    enviar = st.form_submit_button("Guardar")

# ----------------------------
# GUARDAR DATOS
# ----------------------------
if enviar:
    df = pd.read_excel(archivo)

    nueva_fila = {
        "Nombre":nombre,"Apellidos":apellidos,"Sexo":sexo,
        "Fecha Nac":fecha,"Edad":edad,"Direccion":direccion,
        "Deportes":deportes,"Identidad":identidad,
        "Curso":curso,"Año":año,
        "Talla":talla,"Peso":peso,"Envergadura":envergadura,"IMC":imc
    }

    for p in pruebas_nombres:
        nueva_fila[f"{p}_Marca"] = marcas[p]
        nueva_fila[f"{p}_Nota"] = 0

    nueva_fila["Nota Media"] = 0
    nueva_fila["Lesiones"] = lesiones

    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    # ----------------------------
    # CALCULAR NOTAS POR SEXO
    # ----------------------------
    for sexo_grupo in ["H","M"]:
        df_sexo = df[df["Sexo"] == sexo_grupo]

        for p in pruebas_nombres:
            if p in ["Velocidad","Agilidad","Coordinacion","Ruffer"]:
                asc = True  # menor es mejor
            else:
                asc = False # mayor es mejor

            ranking = df_sexo[f"{p}_Marca"].rank(ascending=asc, method="min")

            notas = 5 - (ranking - 1)*0.2
            notas = notas.clip(lower=1)

            df.loc[df["Sexo"] == sexo_grupo, f"{p}_Nota"] = notas

    # Nota media
    notas_cols = [f"{p}_Nota" for p in pruebas_nombres]
    df["Nota Media"] = df[notas_cols].mean(axis=1)

    df.to_excel(archivo, index=False)

    st.success("Datos guardados correctamente")
