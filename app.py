import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------
# CONFIGURACIÓN
# ------------------------
st.set_page_config(page_title="Valoración Física", layout="wide")

SHEET_ID = "TU_ID_DE_GOOGLE_SHEETS"

# ------------------------
# CONEXIÓN GOOGLE SHEETS
# ------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credenciales_dict = st.secrets["gcp_service_account"]

credenciales = ServiceAccountCredentials.from_json_keyfile_dict(
    credenciales_dict, scope
)

cliente = gspread.authorize(credenciales)
hoja = cliente.open_by_key(SHEET_ID).sheet1

# ------------------------
# CARGAR DATOS EXISTENTES
# ------------------------
data = hoja.get_all_records()
df = pd.DataFrame(data)

# ------------------------
# FORMULARIO
# ------------------------
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

    st.subheader("Medidas Antropométricas")
    talla = st.number_input("Talla (m)", value=0.0)
    peso = st.number_input("Peso (kg)", value=0.0)
    envergadura = st.number_input("Envergadura (cm)", value=0.0)

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

# ------------------------
# GUARDAR DATOS
# ------------------------
if enviar:

    nueva_fila = {
        "Nombre": nombre,
        "Apellidos": apellidos,
        "Sexo": sexo,
        "Fecha": str(fecha),
        "Edad": edad,
        "Direccion": direccion,
        "Deportes": deportes,
        "Identidad": identidad,
        "Curso": curso,
        "Año": año,
        "Talla": talla,
        "Peso": peso,
        "Envergadura": envergadura,
        "IMC": imc,
        "Lesiones": lesiones
    }

    for p in pruebas_nombres:
        nueva_fila[f"{p}_Marca"] = marcas[p]
        nueva_fila[f"{p}_Nota"] = 0

    # Agregar a dataframe
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    # ------------------------
    # CALCULAR NOTAS
    # ------------------------
    pruebas_menor_mejor = ["Velocidad","Agilidad","Coordinacion","Ruffer"]

    for sexo_grupo in ["H", "M"]:
        df_sexo = df[df["Sexo"] == sexo_grupo]

        for p in pruebas_nombres:
            col_marca = f"{p}_Marca"
            col_nota = f"{p}_Nota"

            if col_marca not in df.columns:
                continue

            if p in pruebas_menor_mejor:
                ranking = df_sexo[col_marca].rank(ascending=True, method="min")
            else:
                ranking = df_sexo[col_marca].rank(ascending=False, method="min")

            notas = 5 - (ranking - 1) * 0.2
            notas = notas.clip(lower=1)

            df.loc[df["Sexo"] == sexo_grupo, col_nota] = notas

    # Nota media
    notas_cols = [f"{p}_Nota" for p in pruebas_nombres]
    df["Nota Media"] = df[notas_cols].mean(axis=1)

    # ------------------------
    # GUARDAR EN GOOGLE SHEETS
    # ------------------------
    hoja.clear()
    hoja.append_row(df.columns.tolist())

    for i in range(len(df)):
        hoja.append_row(df.iloc[i].astype(str).tolist())

    st.success("✅ Datos guardados y notas calculadas")

# ------------------------
# MOSTRAR DATOS
# ------------------------
st.subheader("📊 Base de datos")
st.dataframe(df)
