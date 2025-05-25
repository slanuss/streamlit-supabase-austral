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
def obtener_datos_hospital(hospital_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del hospital.")
        return None
    try:
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

# --- Funciones para Campañas Publicadas por el Hospital (renombrada a Campañas Solidarias) ---
def obtener_campanas_solidarias_hospital(hospital_id):
    if supabase_client:
        try:
            # Asumo que la tabla 'campaña' tiene una columna 'ID_Hospital'
            response = supabase_client.table("campaña").select("*").eq("ID_Hospital", hospital_id).order("Fecha_Limite", desc=False).execute()
            if response.data:
                return response.data
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas solidarias: {e}")
            return []
    return []

def crear_nueva_campana_solidaria(datos_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña solidaria.")
        return False
    try:
        data, count = supabase_client.table("campaña").insert(datos_campana).execute()
        if data and len(data) > 0:
            st.success("🎉 ¡Nueva campaña solidaria publicada con éxito!")
            return True
        else:
            st.error("❌ No se pudo publicar la nueva campaña solidaria.")
            return False
    except Exception as e:
        st.error(f"❌ Error al crear nueva campaña solidaria: {e}")
        return False

# --- NUEVAS FUNCIONES DE SECCIÓN PARA EL HOSPITAL ---

def hospital_solicitudes():
    st.markdown("<h2 style='color: #4CAF50;'>Solicitudes de Sangre de Beneficiarios 📩</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes ver las solicitudes de sangre enviadas por los beneficiarios y gestionarlas.")

    hospital_id_logueado = st.session_state.get('user_db_id')

    if not hospital_id_logueado:
        st.warning("⚠️ Para ver solicitudes, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    # Lógica para obtener solicitudes de la base de datos
    # Asumo que hay una tabla 'solicitudes_beneficiarios' con 'ID_Hospital_Destino'
    if supabase_client:
        try:
            response = supabase_client.table("solicitudes_beneficiarios").select("*").eq("ID_Hospital_Destino", hospital_id_logueado).order("Fecha_Solicitud", desc=True).execute()
            solicitudes = response.data
            
            if solicitudes:
                for solicitud in solicitudes:
                    with st.expander(f"Solicitud de: {solicitud.get('Nombre_Beneficiario', 'N/A')} (Tipo: {solicitud.get('Tipo_Sangre_Requerida', 'N/A')})"):
                        st.write(f"**ID Solicitud:** {solicitud.get('ID_Solicitud', 'N/A')}")
                        st.write(f"**Descripción:** {solicitud.get('Descripcion_Solicitud', 'N/A')}")
                        st.write(f"**Fecha de Solicitud:** {solicitud.get('Fecha_Solicitud', 'N/A')}")
                        st.write(f"**Tipo de Sangre:** {solicitud.get('Tipo_Sangre_Requerida', 'N/A')}")
                        st.write(f"**Cantidad Necesaria:** {solicitud.get('Cantidad_Necesaria', 'N/A')} unidades")
                        st.write(f"**Estado:** `{solicitud.get('Estado_Solicitud', 'Pendiente')}`")
                        
                        # Puedes añadir botones para "Aceptar", "Rechazar" o "Contactar Beneficiario"
                        # st.button(f"Aceptar Solicitud {solicitud.get('ID_Solicitud')}", key=f"accept_{solicitud.get('ID_Solicitud')}")
                st.markdown("---")
            else:
                st.info("ℹ️ No hay solicitudes de sangre pendientes de beneficiarios en este momento.")
        except Exception as e:
            st.error(f"❌ Error al obtener solicitudes de beneficiarios: {e}")
    else:
        st.error("Conexión a Supabase no disponible para obtener solicitudes.")


def hospital_campanas_beneficiarios():
    st.markdown("<h2 style='color: #4CAF50;'>Campañas de Beneficiarios (Públicas) 🌐</h2>", unsafe_allow_html=True)
    st.write("Explora las campañas de donación de sangre publicadas por otros beneficiarios que necesitan ayuda.")

    # Lógica para obtener todas las campañas de beneficiarios (no solo las del hospital)
    # Asumo que la tabla 'campaña_beneficiario' tiene 'ID_Beneficiario', 'Tipo_Sangre_Requerida', 'Estado_Campaña', etc.
    if supabase_client:
        try:
            # Obtener todas las campañas de beneficiarios activas o relevantes
            response = supabase_client.table("campana_beneficiario").select("*").eq("Estado_Campaña", "En Curso").order("Fecha_Fin", desc=False).execute()
            campanas_beneficiarios = response.data
            
            if campanas_beneficiarios:
                for campana in campanas_beneficiarios:
                    with st.expander(f"Campaña de: {campana.get('Nombre_Beneficiario', 'Beneficiario Anónimo')} (Tipo: {campana.get('Tipo_Sangre_Requerida', 'N/A')})"):
                        st.write(f"**ID Campaña:** {campana.get('ID_Campaña_Beneficiario', 'N/A')}")
                        st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('Fecha_Fin', 'N/A')}")
                        st.write(f"**Tipo de Sangre:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
                        st.write(f"**Cantidad Necesaria:** {campana.get('Cantidad_Necesaria', 'N/A')} unidades")
                        st.write(f"**Estado:** `{campana.get('Estado_Campaña', 'N/A')}`")
                        st.write(f"**Contacto Beneficiario:** {campana.get('Contacto_Beneficiario', 'N/A')}")
                        # Puedes añadir un botón para que el hospital decida ayudar o contactar
                        # st.button(f"Ofrecer Ayuda a Campaña {campana.get('ID_Campaña_Beneficiario')}", key=f"help_camp_ben_{campana.get('ID_Campaña_Beneficiario')}")
                    st.markdown("---")
            else:
                st.info("ℹ️ No hay campañas de beneficiarios activas en este momento.")
        except Exception as e:
            st.error(f"❌ Error al obtener campañas de beneficiarios: {e}")
    else:
        st.error("Conexión a Supabase no disponible para obtener campañas de beneficiarios.")


def hospital_campanas_solidarias():
    st.markdown("<h2 style='color: #4CAF50;'>Mis Campañas Solidarias (Recolección en Hospital) 📢</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes ver las campañas de donación de sangre que tu hospital ha organizado para la recolección en sus propias instalaciones, así como crear nuevas campañas.")

    hospital_id_logueado = st.session_state.get('user_db_id')

    if not hospital_id_logueado:
        st.warning("⚠️ Para gestionar campañas solidarias, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    # --- Sección para CREAR Nueva Campaña Solidaria ---
    st.markdown("### Crear Nueva Campaña Solidaria")
    with st.form("nueva_campana_solidaria_form"):
        nombre_campana = st.text_input("Nombre de la Campaña", placeholder="Jornada de Donación - Verano 2025")
        descripcion_campana = st.text_area("Descripción de la Campaña", placeholder="Campaña anual para reponer nuestras reservas de sangre. ¡Tu donación es vida!")
        fecha_inicio = st.date_input("Fecha de Inicio de la Campaña", value=datetime.today().date())
        fecha_fin = st.date_input("Fecha de Fin de la Campaña", value=datetime.today().date())
        
        # Aquí puedes añadir el tipo de sangre que MÁS se necesita en general para esta campaña
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Cualquiera"]
        tipo_sangre_enfasis = st.selectbox("Énfasis en Tipo de Sangre (opcional)", sangre_options)
        
        estado_campana = st.selectbox("Estado Inicial de la Campaña", ["Próxima", "En Curso"])

        guardar_campana = st.form_submit_button("🚀 Publicar Campaña Solidaria")

        if guardar_campana:
            # Puedes ajustar estas columnas según la tabla 'campaña' que ya tengas
            datos_campana = {
                "ID_Hospital": hospital_id_logueado,
                "Nombre_Campaña": nombre_campana,
                "Descripcion_Campaña": descripcion_campana,
                "Fecha_Inicio": fecha_inicio.isoformat(),
                "Fecha_Limite": fecha_fin.isoformat(), # Usamos Fecha_Limite como Fecha_Fin
                "Tipo_Sangre_Requerida": tipo_sangre_enfasis, # Para indicar el énfasis
                "Estado_Campaña": estado_campana, # Nuevo campo para estado
                "Fecha_Publicacion": datetime.now().isoformat()
            }
            if crear_nueva_campana_solidaria(datos_campana):
                st.balloons()
                # st.rerun() # Opcional: recargar para verla inmediatamente en la lista de abajo

    st.markdown("---")
    st.markdown("### Mis Campañas Solidarias Activas")

    # --- Sección para VER Campañas Solidarias Existentes ---
    campanas = obtener_campanas_solidarias_hospital(hospital_id_logueado)

    if campanas:
        for campana in campanas:
            # Aquí podrías añadir 'Estado_Campaña' si lo agregas a tu tabla 'campaña'
            estado = campana.get('Estado_Campaña', 'N/A') # Asumo que agregaste esta columna
            fecha_fin = campana.get('Fecha_Limite', 'N/A')
            
            with st.expander(f"Campaña: {campana.get('Nombre_Campaña', 'Sin Nombre')} (Estado: {estado})"):
                st.write(f"**ID Campaña:** {campana.get('ID_Campaña', 'N/A')}")
                st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                st.write(f"**Fecha de Inicio:** {campana.get('Fecha_Inicio', 'N/A')}") # Asumo que agregaste esta columna
                st.write(f"**Fecha de Fin:** {fecha_fin}")
                st.write(f"**Énfasis en Tipo de Sangre:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
                
                # Aquí podrías añadir botones para editar o cerrar la campaña
                # if st.button(f"Editar Campaña {campana.get('ID_Campaña')}", key=f"edit_solidaria_{campana.get('ID_Campaña')}"):
                #     st.info("Funcionalidad de edición en desarrollo.")
                # if st.button(f"Finalizar Campaña {campana.get('ID_Campaña')}", key=f"end_solidaria_{campana.get('ID_Campaña')}"):
                #     st.info("Funcionalidad de finalizar en desarrollo.")
            st.markdown("---")
    else:
        st.info("ℹ️ No has publicado ninguna campaña solidaria de recolección aún. ¡Usa el formulario de arriba para crear una!")


# --- Lógica principal de la página del Hospital ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Hospital':
        st.sidebar.title("Navegación Hospital 🧭")
        # Menú actualizado para el Hospital
        menu = ["Perfil", "Solicitudes", "Campañas de Beneficiarios", "Campañas Solidarias"] 
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            hospital_perfil()
        elif opcion == "Solicitudes":
            hospital_solicitudes()
        elif opcion == "Campañas de Beneficiarios":
            hospital_campanas_beneficiarios()
        elif opcion == "Campañas Solidarias":
            hospital_campanas_solidarias()
    else:
        st.warning("⚠️ Debes iniciar sesión como **Hospital** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()