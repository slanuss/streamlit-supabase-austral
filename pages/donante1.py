import streamlit as st
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, configúralas para que la conexión a la base de datos funcione.")
    supabase_client: Client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
        supabase_client: Client = None

# --- Funciones para Beneficiario ---

def obtener_datos_beneficiario(beneficiario_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos.")
        return None
    try:
        response = supabase_client.table("beneficiario").select("*, id_beneficiario").eq("mail", beneficiario_email).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del beneficiario: {e}")
        return None

def crear_campana(id_beneficiario, nombre_campana, tipo_sangre, fecha_inicio, fecha_fin, ubicacion, estado_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear campaña.")
        return False
    try:
        # Asegúrate de que los nombres de las columnas coincidan con tu tabla 'campaña' en Supabase
        data = {
            "id_beneficiario": id_beneficiario,
            "nombre_campana": nombre_campana,
            "tipo_sangre_requerida": tipo_sangre, 
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "ubicacion": ubicacion,
            "estado_campana": estado_campana,
            # Si tienes una columna 'descripcion' en tu DB, agrégala aquí y en los parámetros de la función
            # "descripcion": descripcion_campana,
        }
        response = supabase_client.table("campaña").insert(data).execute()
        if response.data:
            st.success("🎉 ¡Campaña creada exitosamente!")
            return True
        else:
            st.error(f"❌ Error al crear campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error al conectar con Supabase para crear campaña: {e}")
        return False

def obtener_mis_campanas(id_beneficiario):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener campañas.")
        return []
    try:
        # Aquí también, asegura que los nombres de las columnas son correctos
        # Las columnas que se muestran en tus capturas son:
        # id_beneficiario, id_hospital, fecha_inicio, fecha_fin, ubicacion, nombre_campana, estado_campana, tipo_sangre_requerida
        response = supabase_client.table("campaña").select("id_campana, nombre_campana, fecha_inicio, fecha_fin, ubicacion, estado_campana, tipo_sangre_requerida").eq("id_beneficiario", id_beneficiario).order("fecha_inicio", desc=True).execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"❌ Error al cargar tus campañas: {e}")
        st.error("Asegúrate de que la tabla 'campaña' exista y las RLS permitan la lectura.")
        return []

def finalizar_campana_db(campana_id):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede finalizar campaña.")
        return False
    try:
        # Actualiza el estado de la campaña
        response = supabase_client.table("campaña").update({"estado_campana": "Finalizada"}).eq("id_campana", campana_id).execute()
        if response.data:
            st.success(f"✅ Campaña {campana_id} finalizada con éxito.")
            return True
        else:
            st.error(f"❌ Error al finalizar campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error al finalizar campaña en Supabase: {e}")
        return False


# --- Funciones de sección de Beneficiario ---
def beneficiario_crear_campana():
    st.markdown("<h2 style='color: #B22222;'>Crear Nueva Campaña de Donación ✨</h2>", unsafe_allow_html=True)
    st.write("Configura los detalles de tu nueva campaña para solicitar donantes.")

    beneficiario_data = obtener_datos_beneficiario(st.session_state['user_email'])
    beneficiario_id = beneficiario_data.get('id_beneficiario') if beneficiario_data else None
    
    if not beneficiario_id:
        st.warning("No se pudo obtener el ID del beneficiario. Asegúrate de que tu perfil esté completo y el email de sesión sea correcto.")
        return

    # Usar el tipo de sangre del beneficiario registrado para la campaña si es necesario
    tipo_sangre_beneficiario = beneficiario_data.get('tipo_de_sangre', 'O+') if beneficiario_data else 'O+'

    with st.form("crear_campana_form"):
        nombre_campana = st.text_input("Nombre de la Campaña", help="Ej: 'Campaña Urgente A+'")
        
        # Si tienes una columna de descripción en tu DB, la agregas aquí:
        # descripcion_campana = st.text_area("Descripción de la Campaña (opcional)")

        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha de Inicio", datetime.now())
        with col2:
            fecha_fin = st.date_input("Fecha Límite para la Donación", datetime.now())

        ubicacion = st.text_input("Ubicación de la Donación", help="Ej: 'Hospital Central, Sala 5'")
        
        tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        tipo_sangre_requerida = st.selectbox("Tipo de Sangre Requerida", tipos_sangre, index=tipos_sangre.index(tipo_sangre_beneficiario) if tipo_sangre_beneficiario in tipos_sangre else 0)
        st.info(f"Tu tipo de sangre registrado es: **{tipo_sangre_beneficiario}**. Esto se asociará a la campaña.")
        
        estado_campana = st.selectbox("Estado Inicial", ["En curso", "Próxima", "Finalizada"], index=0) # Añadir "Finalizada" para la creación si es necesario

        st.write("---")
        crear_button = st.form_submit_button("Crear Campaña")

        if crear_button:
            if not all([nombre_campana, fecha_inicio, fecha_fin, ubicacion, tipo_sangre_requerida]):
                st.error("Por favor, completa todos los campos obligatorios.")
            elif fecha_fin < fecha_inicio:
                st.error("La fecha límite no puede ser anterior a la fecha de inicio.")
            else:
                if crear_campana(beneficiario_id, nombre_campana, tipo_sangre_requerida, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"), ubicacion, estado_campana):
                    time.sleep(1)
                    st.rerun() # CORRECCIÓN: Usar st.rerun()

def beneficiario_mis_campanas():
    st.markdown("<h2 style='color: #B22222;'>Mis Campañas Creadas 📋</h2>", unsafe_allow_html=True)
    st.write("Visualiza y gestiona el estado de tus campañas de donación.")

    beneficiario_data = obtener_datos_beneficiario(st.session_state['user_email'])
    beneficiario_id = beneficiario_data.get('id_beneficiario') if beneficiario_data else None

    if not beneficiario_id:
        st.warning("No se pudo obtener el ID del beneficiario. Asegúrate de que tu perfil esté completo y el email de sesión sea correcto.")
        return

    mis_campanas = obtener_mis_campanas(beneficiario_id)

    if mis_campanas:
        for campana in mis_campanas:
            # Asegúrate de usar los nombres de columna correctos de tu tabla 'campaña'
            # CORRECCIÓN: Usar 'id_campana' y 'nombre_campana'
            campana_id = campana.get('id_campana')
            nombre_campana = campana.get('nombre_campana', 'N/A')
            estado_campana = campana.get('estado_campana', 'N/A')

            with st.expander(f"Campaña: {nombre_campana} (Estado: {estado_campana})"):
                st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                st.write(f"**Ubicación:** {campana.get('ubicacion', 'N/A')}")
                st.write(f"**Tipo de Sangre Requerida:** {campana.get('tipo_sangre_requerida', 'N/A')}")
                
                # Si tienes una descripción:
                # st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")

                if estado_campana != "Finalizada":
                    if st.button(f"✅ Finalizar Campaña", key=f"finalizar_{campana_id}"):
                        if finalizar_campana_db(campana_id):
                            st.balloons()
                            time.sleep(1)
                            st.rerun() # CORRECCIÓN: Usar st.rerun()
                else:
                    st.info("Esta campaña ya ha sido finalizada.")
            st.markdown("---")
    else:
        st.info("ℹ️ Todavía no has creado ninguna campaña. ¡Crea una para empezar!")

# --- Función principal de la página de Beneficiario ---
def beneficiario_page():
    st.title("🤝 Panel de Beneficiario")
    st.markdown("---")

    # Verifica si el usuario está logueado como Beneficiario
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Beneficiario':
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        st.stop()

    tab1, tab2 = st.tabs(["Crear Campaña", "Mis Campañas"])

    with tab1:
        beneficiario_crear_campana()
    with tab2:
        beneficiario_mis_campanas()

if __name__ == "__main__":
    beneficiario_page()