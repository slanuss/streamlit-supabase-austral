import streamlit as st
import pandas as pd
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

# --- Función para obtener datos del hospital ---
# Asumo que el hospital se identificará por su mail (igual que donante/beneficiario)
def obtener_datos_hospital(hospital_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del hospital.")
        return None
    try:
        # Asumo que tienes una tabla 'hospital' y una columna 'mail'
        response = supabase_client.table("hospital").select("*").eq("mail", hospital_email).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del hospital: {e}")
        return None

# --- Función para actualizar datos del hospital ---
def actualizar_datos_hospital(hospital_email, datos):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del hospital.")
        return False
    try:
        response = supabase_client.table("hospital").update(datos).eq("mail", hospital_email).execute()
        if response.data:
            st.success("✅ ¡Perfil del Hospital actualizado con éxito!")
            time.sleep(1)
            st.rerun()
            return True
        else:
            st.error(f"❌ Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False

# --- Funciones para Campañas Publicadas por el Hospital ---
def obtener_campanas_hospital(hospital_id):
    if supabase_client:
        try:
            # Asumo que la tabla 'campaña' tiene una columna 'ID_Hospital'
            response = supabase_client.table("campaña").select("*").eq("ID_Hospital", hospital_id).order("Fecha_Limite", desc=False).execute()
            if response.data:
                return response.data
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas del hospital: {e}")
            return []
    return []

def crear_nueva_campana(datos_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña.")
        return False
    try:
        data, count = supabase_client.table("campaña").insert(datos_campana).execute()
        if data and len(data) > 0:
            st.success("🎉 ¡Nueva campaña publicada con éxito!")
            return True
        else:
            st.error("❌ No se pudo publicar la nueva campaña.")
            return False
    except Exception as e:
        st.error(f"❌ Error al crear nueva campaña: {e}")
        return False

# --- Definición de las funciones de sección del Hospital ---
def hospital_perfil():
    st.markdown("<h2 style='color: #4CAF50;'>Mi Perfil de Hospital 🏥</h2>", unsafe_allow_html=True)
    st.write("Gestiona la información de tu hospital y asegura que tus datos estén actualizados.")

    email_usuario_logueado = st.session_state.get('user_email', 'hospital@ejemplo.com')
    hospital_id_logueado = st.session_state.get('user_db_id') # ID de la DB si lo obtuvimos

    perfil_existente = obtener_datos_hospital(email_usuario_logueado)

    valores_iniciales = {
        "nombre_hospital": "", "mail": email_usuario_logueado, "telefono": "", "direccion": "",
        "sitio_web": "", "descripcion": ""
    }
    
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombre_hospital', 'N/A')}**")
        valores_iniciales["nombre_hospital"] = perfil_existente.get("nombre_hospital", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["sitio_web"] = perfil_existente.get("sitio_web", "")
        valores_iniciales["descripcion"] = perfil_existente.get("descripcion", "")

    with st.form("hospital_perfil_form"):
        st.markdown("#### Información del Hospital")
        col1, col2 = st.columns(2)
        with col1:
            nombre_hospital = st.text_input("Nombre del Hospital", value=valores_iniciales["nombre_hospital"])
            mail = st.text_input("Mail de Contacto", value=valores_iniciales["mail"], disabled=True)
            telefono = st.text_input("Teléfono del Hospital", value=valores_iniciales["telefono"])
        with col2:
            direccion = st.text_input("Dirección del Hospital", value=valores_iniciales["direccion"])
            sitio_web = st.text_input("Sitio Web (opcional)", value=valores_iniciales["sitio_web"])
        
        descripcion = st.text_area("Breve Descripción del Hospital", value=valores_iniciales["descripcion"])

        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "nombre_hospital": nombre_hospital,
                "mail": mail,
                "telefono": telefono,
                "direccion": direccion,
                "sitio_web": sitio_web,
                "descripcion": descripcion
            }
            st.write("Datos a guardar:", datos_a_guardar) # Debugging
            if perfil_existente:
                actualizar_datos_hospital(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de hospital aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el hospital ya exista en la base de datos para poder actualizar su perfil.")


def hospital_campanas_publicadas():
    st.markdown("<h2 style='color: #4CAF50;'>Mis Campañas Publicadas 📢</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes ver y gestionar las campañas de donación de sangre que tu hospital ha publicado.")

    hospital_id_logueado = st.session_state.get('user_db_id')

    if not hospital_id_logueado:
        st.warning("⚠️ Para ver campañas, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    campanas = obtener_campanas_hospital(hospital_id_logueado)

    if campanas:
        for campana in campanas:
            with st.expander(f"Campaña: {campana.get('Nombre_Campaña', 'Sin Nombre')} (Sangre: {campana.get('Tipo_Sangre_Requerida', 'N/A')})"):
                st.write(f"**ID Campaña:** {campana.get('ID_Campaña', 'N/A')}")
                st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                st.write(f"**Fecha Límite:** {campana.get('Fecha_Limite', 'N/A')}")
                st.write(f"**Tipo de Sangre Requerida:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
                st.write(f"**Cantidad Necesaria:** {campana.get('Cantidad_Necesaria', 'N/A')} unidades")
                # Aquí podrías añadir botones para editar o eliminar la campaña
                # if st.button(f"Editar Campaña {campana.get('ID_Campaña')}", key=f"edit_camp_{campana.get('ID_Campaña')}"):
                #     st.info("Funcionalidad de edición de campaña en desarrollo.")
                # if st.button(f"Eliminar Campaña {campana.get('ID_Campaña')}", key=f"del_camp_{campana.get('ID_Campaña')}"):
                #     st.info("Funcionalidad de eliminación de campaña en desarrollo.")
            st.markdown("---")
    else:
        st.info("ℹ️ No has publicado ninguna campaña aún. ¡Usa la sección 'Publicar Nueva Campaña' para empezar!")


def hospital_publicar_campana():
    st.markdown("<h2 style='color: #4CAF50;'>Publicar Nueva Campaña de Donación ➕</h2>", unsafe_allow_html=True)
    st.write("Crea una nueva campaña de donación de sangre para tu hospital y llega a más donantes.")

    hospital_id_logueado = st.session_state.get('user_db_id')

    if not hospital_id_logueado:
        st.warning("⚠️ Para publicar campañas, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    with st.form("nueva_campana_form"):
        nombre_campana = st.text_input("Nombre de la Campaña", placeholder="Campaña de Verano - Julio")
        descripcion_campana = st.text_area("Descripción de la Campaña", placeholder="Necesitamos donantes de todos los tipos de sangre para cubrir las necesidades de este mes.")
        fecha_limite = st.date_input("Fecha Límite para la Donación", value=datetime.today().date())
        
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Cualquiera"]
        tipo_sangre_requerida = st.selectbox("Tipo de Sangre Requerida", sangre_options)
        
        cantidad_necesaria = st.number_input("Cantidad Necesaria (unidades)", min_value=1, value=10)

        guardar_campana = st.form_submit_button("🚀 Publicar Campaña")

        if guardar_campana:
            datos_campana = {
                "ID_Hospital": hospital_id_logueado, # Clave foránea al ID del hospital
                "Nombre_Campaña": nombre_campana,
                "Descripcion_Campaña": descripcion_campana,
                "Fecha_Limite": fecha_limite.isoformat(),
                "Tipo_Sangre_Requerida": tipo_sangre_requerida,
                "Cantidad_Necesaria": cantidad_necesaria,
                "Fecha_Publicacion": datetime.now().isoformat() # Fecha de creación de la campaña
            }
            # *** Debugging para ver los datos antes de enviar ***
            st.write("Datos de la nueva campaña:", datos_campana)
            # ***************************************************
            if crear_nueva_campana(datos_campana):
                st.balloons()
                st.rerun() # Recargar para que aparezca en 'Campañas Publicadas'


# --- Lógica principal de la página del Hospital ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Hospital':
        st.sidebar.title("Navegación Hospital 🧭")
        menu = ["Perfil", "Campañas Publicadas", "Publicar Nueva Campaña"]
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            hospital_perfil()
        elif opcion == "Campañas Publicadas":
            hospital_campanas_publicadas()
        elif opcion == "Publicar Nueva Campaña":
            hospital_publicar_campana()
    else:
        st.warning("⚠️ Debes iniciar sesión como **Hospital** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()


            