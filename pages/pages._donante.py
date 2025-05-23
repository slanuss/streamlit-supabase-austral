# pages/_donante.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carga las variables de entorno para este archivo
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env para _donante.py. La conexión a Supabase fallará.")
    supabase_client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Opcional: una pequeña prueba de conexión para depuración. Comentar si no la necesitas.
        # response = supabase_client.table("donante").select("id").limit(1).execute()
        # if response.error:
        #     st.warning(f"Advertencia: Problema al conectar o consultar la tabla 'donante' desde _donante.py: {response.error.message}")
        # else:
        #     st.success("Conexión a Supabase desde _donante.py OK.")
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase en _donante.py: {e}")
        supabase_client = None


def guardar_perfil_supabase(datos_donante: dict):
    """Guarda los datos del perfil del donante en la base de datos Supabase."""
    if supabase_client:
        try:
            # Asegúrate de que "donante" sea el nombre exacto de tu tabla en Supabase
            data, count = supabase_client.table("donante").insert(datos_donante).execute()
            if data and len(data) > 0: # Verifica que 'data' no esté vacío y contenga algo
                st.success("Perfil guardado en Supabase!")
                return True
            else:
                st.error("Error al guardar el perfil en Supabase. No se insertaron registros.")
                return False
        except Exception as e:
            st.error(f"Error de conexión o inserción en Supabase (donante): {e}")
            return False
    else:
        st.warning("No se pudo conectar a Supabase para guardar el perfil del donante. Revisa tus variables .env.")
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
            datos_donante = {
                "nombred": nombred,
                "mail": mail,
                "telefono": telefono,
                "direccion": direccion,
                "edad": edad,
                "sexo": sexo,
                "tipo_de_sangre": tipo_de_sangre,
                "antecedentes": antecedentes,
                "medicaciones": medicaciones,
                "cumple_requisitos": cumple_requisitos,
            }
            guardar_perfil_supabase(datos_donante)

def donante_campanas():
    st.header("Campañas de Donación Disponibles")
    st.info("Aquí se mostrarán las campañas a las que te puedes afiliar. Esta información se gestionará desde el perfil de beneficiario.")

def donante_hospitales():
    st.header("Hospitales")
    st.info("Aquí se mostrará la lista de hospitales asociados.")

def donante_requisitos():
    st.header("Requisitos para Donar")
    st.info("Aquí se detallarán los requisitos necesarios para ser donante.")

def donante_manual():
    st.header("Manual del Donante")
    st.info("Aquí se proporcionará un manual con información útil para los donantes.")

def donante_info_donaciones():
    st.header("Información sobre Donaciones")
    st.info("Aquí se mostrará información relevante sobre donaciones, proporcionada por los hospitales.")

# Esta es la función principal que será llamada desde Inicio.py
def donante_page():
    st.sidebar.title("Navegación Donante")
    menu = ["Perfil", "Campañas Disponibles", "Información sobre Donaciones", "Hospitales", "Requisitos", "Manual del Donante"]
    opcion = st.sidebar.selectbox("Selecciona una sección", menu)

    if opcion == "Perfil":
        donante_perfil()
    elif opcion == "Campañas Disponibles":
        donante_campanas()
    elif opcion == "Información sobre Donaciones":
        donante_info_donaciones()
    elif opcion == "Hospitales":
        donante_hospitales()
    elif opcion == "Requisitos":
        donante_requisitos()
    elif opcion == "Manual del Donante":
        donante_manual()