import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

st.info(f"SUPABASE_URL cargada: {SUPABASE_URL}")
st.info(f"SUPABASE_KEY cargada: {SUPABASE_KEY}")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    supabase_client = None
else:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_perfil_supabase(datos_donante: dict):
    """Guarda los datos del perfil del donante en la base de datos Supabase."""
    if supabase_client:
        try:
            data, count = supabase_client.table("donante").insert(datos_donante).execute()
            st.info(f"Datos insertados en Supabase: {data}, Count: {count}")
            if count > 0:
                st.success("Perfil guardado en Supabase!")
                return True
            else:
                st.error("Error al guardar el perfil en Supabase.")
                return False
        except Exception as e:
            st.error(f"Error de conexión o inserción en Supabase: {e}")
            return False
    else:
        st.warning("No se pudo conectar a Supabase.")
        return False

def donante_perfil():
    st.header("Perfil del Donante")
    with st.form("perfil_form"):
        nombred = st.text_input("Nombre y Apellido")
        mail = st.text_input("Mail Personal")
        telefono = st.text_input("Teléfono")
        direccion = st.text_input("Dirección")
        edad = st.number_input("Edad", min_value=18, max_value=100, step=1)
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
        tipo_de_sangre = st.selectbox("Tipo de Sangre", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        antecedentes = st.text_area("Antecedentes Médicos (separados por coma o en líneas diferentes)")
        medicaciones = st.text_area("Medicaciones Actuales (separadas por coma o en líneas diferentes)")
        cumple_requisitos = st.checkbox("Declaro cumplir con los requisitos básicos para donar")
        guardar = st.form_submit_button("Guardar Perfil")

        if guardar:
    print("Función guardar_perfil_supabase llamada")
    datos_donante = {
        "nombred": nombred,
        "mail": mail,
        "telefono": telefono,
        "direccion": direccion,
        "edad": edad,
        "sexo": sexo[0] if sexo else None,  # Envía solo el primer carácter
        "tipo_de_sangre": tipo_de_sangre,
        "antecedentes": antecedentes,
        "medicaciones": medicaciones,
        "cumple_requisitos": cumple_requisitos,
    }
    guardar_perfil_supabase(datos_donante)
    st.success("Perfil guardado localmente!")

def donante_campanas():
    st.header("Campañas de Donación Disponibles")
    st.info("Aquí se mostrarán las campañas de donación activas.")
    # Aquí iría la lógica para mostrar las campañas

def donante_hospitales():
    st.header("Hospitales")
    st.info("Aquí se mostrará la lista de hospitales asociados.")
    # Aquí iría la lógica para mostrar los hospitales

def donante_requisitos():
    st.header("Requisitos para Donar")
    st.info("Aquí se detallarán los requisitos necesarios para ser donante.")
    # Aquí iría la información sobre los requisitos

def donante_manual():
    st.header("Manual del Donante")
    st.info("Aquí se proporcionará un manual con información útil para los donantes.")
    # Aquí iría el contenido del manual

def donante_page():
    st.sidebar.title("Navegación Donante")
    menu = ["Perfil", "Campañas Disponibles", "Hospitales", "Requisitos", "Manual del Donante"]
    opcion = st.sidebar.selectbox("Selecciona una sección", menu)

    if opcion == "Perfil":
        donante_perfil()
    elif opcion == "Campañas Disponibles":
        donante_campanas()
    elif opcion == "Hospitales":
        donante_hospitales()
    elif opcion == "Requisitos":
        donante_requisitos()
    elif opcion == "Manual del Donante":
        donante_manual()

if __name__ == "__main__":
    donante_page()
