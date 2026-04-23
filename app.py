import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Valoración Física", layout="wide")

archivo = "datos_estudiantes.xlsx"

# ----------------------------
# CREAR ARCHIVO SI NO EXISTE
# ----------------------------
pruebas_nombres = [
    "Cooper","Ruffer","Burpee","Course",
    "Flxb Brazos","Flxb Piernas","Flxb Tronco","Flxb Profunda",
    "Fz Brazos","Fz Vertical","Fz Horizontal","Fz Abdominal",
    "Fz Balon","Coordinacion","Velocidad","Agilidad"
]

if not os.path.exists(archivo):
    columnas = [
        "Nombre","Apellidos","Sexo","Fecha Nac","Edad","Direccion",
        "Deportes","Identidad","Curso","Año",
        "Talla","Peso","Envergadura","IMC"
    ]

    for p in pruebas_nombres:
        columnas.append(f"{p}_Marca")
        columnas.append(f"{p}_Nota")

    columnas.append("Nota Media")
    columnas.append("Lesiones")

    df = pd.DataFrame(columns=columnas)
    df.to_excel(archivo, index=False)

# ----------------------------
# FORMULARIO
# ----------------------------
st.title("🏃 Valoración Física")

with st.form("formulario"):
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre")
        apellidos = st.text_input("Apellidos")
        sexo = st.selectbox("Sexo", ["H", "M"])
        fecha = st.date_input("Fecha de nacimiento")
        edad = st.number_input("Edad", 10, 30)

    with col2:
        direccion = st.text_input("Dirección")
        deportes = st.text_input("Deportes")
        identidad = st.text_input("Tarjeta de identidad")
        curso = st.text_input("Curso")
        año = st.number_input("Año", 2020, 2030)

    st.subheader("Medidas")
    talla = st.number_input("Talla (m)", min_value=0.0)
    peso = st.number_input("Peso (kg)", min_value=0.0)
    envergadura = st.number_input("Envergadura (cm)", min_value=0.0)

    imc = peso / (talla**2) if talla > 0 else 0

    st.subheader("Pruebas")

    marcas = {}
    for p in pruebas_nombres:
        marcas[p] = st.number_input(f"{p} (marca)", min_value=0.0)

    lesiones = st.text_area("Lesiones")

    enviar = st.form_submit_button("Guardar")

# ----------------------------
# PROCESO PRINCIPAL
# ----------------------------
if enviar:

    # VALIDACIÓN BÁSICA
    if nombre == "" or apellidos == "":
        st.error("Nombre y Apellidos son obligatorios")
        st.stop()

    df = pd.read_excel(archivo)

    # NUEVA FILA
    nueva_fila = {
        "Nombre":nombre,"Apellidos":apellidos,"Sexo":sexo,
        "Fecha Nac":fecha,"Edad":edad,"Direccion":direccion,
        "Deportes":deportes,"Identidad":identidad,
        "Curso":curso,"Año":año,
        "Talla":talla,"Peso":peso,"Envergadura":envergadura,"IMC":imc
    }

    for p in pruebas_nombres:
        nueva_fila[f"{p}_Marca"] = marcas[p]
        nueva_fila[f"{p}_Nota"] = 0.0

    nueva_fila["Nota Media"] = 0.0
    nueva_fila["Lesiones"] = lesiones

    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    # ----------------------------
    # LIMPIEZA DE DATOS
    # ----------------------------
    for p in pruebas_nombres:
        df[f"{p}_Marca"] = pd.to_numeric(df[f"{p}_Marca"], errors="coerce")
        df[f"{p}_Nota"] = df[f"{p}_Nota"].astype(float)

    # ----------------------------
    # CALCULAR NOTAS
    # ----------------------------
    pruebas_menor_mejor = ["Velocidad","Agilidad","Coordinacion","Ruffer"]

    for sexo_grupo in ["H", "M"]:
        df_sexo = df[df["Sexo"] == sexo_grupo]

        for p in pruebas_nombres:
            col_marca = f"{p}_Marca"
            col_nota = f"{p}_Nota"

            if p in pruebas_menor_mejor:
                ranking = df_sexo[col_marca].rank(ascending=True, method="min")
            else:
                ranking = df_sexo[col_marca].rank(ascending=False, method="min")

            notas = 5 - (ranking - 1)*0.2
            notas = notas.clip(lower=1)

            df.loc[df["Sexo"] == sexo_grupo, col_nota] = notas.astype(float)

    # NOTA MEDIA
    notas_cols = [f"{p}_Nota" for p in pruebas_nombres]
    df["Nota Media"] = df[notas_cols].mean(axis=1).round(2)

    # GUARDAR
    df.to_excel(archivo, index=False)

    st.success("✅ Datos guardados correctamente")

    # ----------------------------
    # DESCARGAR EXCEL
    # ----------------------------
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)

    st.download_button(
        label="📥 Descargar Excel",
        data=buffer,
        file_name="datos_estudiantes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ----------------------------
# MOSTRAR DATOS
# ----------------------------
try:
    df = pd.read_excel(archivo)
    st.subheader("📊 Base de datos")
    st.dataframe(df)
except:
    pass
