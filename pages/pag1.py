#formulario solicitud hospital
import streamlit as st
from datetime import date
import os
from supabase import create_client, Client
from dotenv import load_dotenv


# 📌 Cargar variables de entorno del archivo .env
load_dotenv()
SUPABASE_URL= https://ocqcjqltxynqsnnuvjbo.supabase.co
SUPABASE_KEY= eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jcWNqcWx0eHlucXNubnV2amJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU0Mjg0MjMsImV4cCI6MjA2MTAwNDQyM30.narYL8GfGLffLvdLYd-MFz_ZXo1KD3ve2xCoTj150ps

# 📌 Conectar a Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Título de la página
st.title("🩸 Crear nueva solicitud de sangre")

st.write("Complete el siguiente formulario para solicitar unidades de sangre.")

# ✅ Formulario
with st.form("formulario_solicitud"):
    tipo_sangre = st.selectbox("Tipo de sangre necesario:", [
        "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"
    ])
    cantidad = st.number_input("Cantidad de unidades necesarias:", min_value=1, max_value=50, step=1)
    fecha_limite = st.date_input("Fecha límite para la donación:", min_value=date.today())
    notas = st.text_area("Notas adicionales (opcional):", placeholder="Ej: paciente pediátrico, cirugía urgente...")

    enviar = st.form_submit_button("📤 Enviar solicitud")

# ✅ Guardar en Supabase si se envió
if enviar:
    data = {
        "tipo_sangre": tipo_sangre,
        "cantidad": cantidad,
        "fecha_limite": str(fecha_limite),
        "notas": notas,
        "estado": "pendiente"  # podés cambiar esto luego a "completa" si se llena
    }

    try:
        response = supabase.table("solicitudes_sangre").insert(data).execute()
        st.success("✅ Solicitud enviada con éxito.")
    except Exception as e:
        st.error(f"❌ Error al guardar en Supabase: {e}")

