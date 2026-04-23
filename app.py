import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Valoración Física", layout="wide")

archivo = "datos_estudiantes.xlsx"

# ----------------------------
# PRUEBAS
# ----------------------------
pruebas_nombres = [
    "Cooper","Ruffer","Burpee","Course",
    "Flxb Brazos","Flxb Piernas","Flxb Tronco","Flxb Profunda",
    "Fz Brazos","Fz Vertical","Fz Horizontal","Fz Abdominal",
    "Fz Balon","Coordinacion","Velocidad","Agilidad"
]

# ----------------------------
# COLUMNAS BASE
# ----------------------------
columnas_base = [
    "Nombre","Apellidos","Sexo","Edad",
    "Deportes","Identidad","Curso",
    "Talla","Peso","Envergadura","IMC"
]

columnas_correctas = columnas_base.copy()

for p in pruebas_nombres:
    columnas_correctas.append(f"{p}_Marca")
    columnas_correctas.append(f"{p}_Nota")

columnas_correctas.append("Nota Media")
columnas_correctas.append("Lesiones")

# ----------------------------
# CREAR / CARGAR ARCHIVO
# ----------------------------
if os.path.exists(archivo):
    df = pd.read_excel(archivo)

    # LIMPIAR columnas viejas
    df = df[[col for col in df.columns if col in columnas_correctas]]

    # AGREGAR columnas faltantes
    for col in columnas_correctas:
        if col not in df.columns:
            df[col] = 0

    df = df[columnas_correctas]

else:
    df = pd.DataFrame(columns=columnas_correctas)

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
        edad = st.number_input("Edad", 10, 30)

    with col2:
        deportes = st.text_input("Deportes")
        identidad = st.text_input("Tarjeta de identidad")
        curso = st.text_input("Curso")

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
# PROCESO
# ----------------------------
if enviar:

    if nombre == "" or apellidos == "":
        st.error("Nombre y Apellidos son obligatorios")
        st.stop()

    nueva_fila = {
        "Nombre":nombre,"Apellidos":apellidos,"Sexo":sexo,
        "Edad":edad,"Deportes":deportes,"Identidad":identidad,
        "Curso":curso,"Talla":talla,"Peso":peso,
        "Envergadura":envergadura,"IMC":imc
    }

    for p in pruebas_nombres:
        nueva_fila[f"{p}_Marca"] = marcas[p]
        nueva_fila[f"{p}_Nota"] = 0.0

    nueva_fila["Nota Media"] = 0.0
    nueva_fila["Lesiones"] = lesiones

    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    # LIMPIEZA
    for p in pruebas_nombres:
        df[f"{p}_Marca"] = pd.to_numeric(df[f"{p}_Marca"], errors="coerce")
        df[f"{p}_Nota"] = df[f"{p}_Nota"].astype(float)

    # CALCULAR NOTAS
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

    # RANKING GENERAL
    df["Ranking"] = df["Nota Media"].rank(ascending=False)

    # ----------------------------
    # GUARDAR EN 3 HOJAS
    # ----------------------------
    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Todos", index=False)
        df[df["Sexo"] == "H"].to_excel(writer, sheet_name="Hombres", index=False)
        df[df["Sexo"] == "M"].to_excel(writer, sheet_name="Mujeres", index=False)

    st.success("✅ Datos guardados correctamente")

    # ----------------------------
    # DESCARGAR
    # ----------------------------
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Todos", index=False)
        df[df["Sexo"] == "H"].to_excel(writer, sheet_name="Hombres", index=False)
        df[df["Sexo"] == "M"].to_excel(writer, sheet_name="Mujeres", index=False)

    st.download_button(
        label="📥 Descargar Excel completo",
        data=buffer,
        file_name="valoracion_fisica.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ----------------------------
# MOSTRAR DATOS
# ----------------------------
st.subheader("📊 Base de datos")
st.dataframe(df)

if st.button("🔴 Borrar todos los datos y reiniciar"):
    if os.path.exists(archivo):
        os.remove(archivo)
        st.success("Base de datos eliminada. Reiniciando...")
        st.rerun()

