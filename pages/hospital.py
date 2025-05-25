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

# --- Funciones para Campañas Solidarias del Hospital (recolección) ---
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

# --- Definición de las funciones de sección del Hospital ---
def hospital_perfil():
    st.markdown("<h2 style='color: #4CAF50;'>Mi Perfil de Hospital 🏥</h2>", unsafe_allow_html=True)
    st.write("Gestiona la información de tu hospital y asegura que tus datos estén actualizados.")

    email_usuario_logueado = st.session_state.get('user_email', 'hospital@ejemplo.com')
    hospital_id_logueado = st.session_state.get('user_db_id')

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
            if perfil_existente:
                actualizar_datos_hospital(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de hospital aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el hospital ya exista en la base de datos para poder actualizar su perfil.")


def hospital_campanas_beneficiarios():
    st.markdown("<h2 style='color: #4CAF50;'>Campañas de Beneficiarios (Públicas) 🌐</h2>", unsafe_allow_html=True)
    st.write("Explora las campañas de donación de sangre publicadas por otros beneficiarios que necesitan ayuda, y gestiona las asociaciones con tu hospital.")

    hospital_id_logueado = st.session_state.get('user_db_id')

    if not hospital_id_logueado:
        st.warning("⚠️ Para ver y gestionar campañas de beneficiarios, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    # Lógica para obtener todas las campañas de beneficiarios (no solo las del hospital)
    # Asumo que la tabla 'campana_beneficiario' tiene 'ID_Beneficiario', 'Tipo_Sangre_Requerida', 'Estado_Campaña', etc.
    if supabase_client:
        try:
            # Obtener todas las campañas de beneficiarios activas o relevantes
            # Ahora, también mostramos el hospital asociado si lo hay
            response = supabase_client.table("beneficiario").select("ID_Beneficiario, Nombre, ID_Hospital_Asociado, mail").execute()
            beneficiarios = {b['ID_Beneficiario']: b for b in response.data}
            
            # Obtener campañas de beneficiarios
            response_campanas = supabase_client.table("campana_beneficiario").select("*").eq("Estado_Campaña", "En Curso").order("Fecha_Fin", desc=False).execute()
            campanas_beneficiarios = response_campanas.data
            
            st.markdown("### Campañas Activas de Beneficiarios")
            if campanas_beneficiarios:
                for campana in campanas_beneficiarios:
                    beneficiario_info = beneficiarios.get(campana.get('ID_Beneficiario'))
                    beneficiario_nombre = beneficiario_info.get('Nombre', 'Beneficiario Anónimo') if beneficiario_info else 'Beneficiario Anónimo'
                    
                    with st.expander(f"Campaña de: {beneficiario_nombre} (Tipo: {campana.get('Tipo_Sangre_Requerida', 'N/A')})"):
                        st.write(f"**ID Campaña:** {campana.get('ID_Campaña_Beneficiario', 'N/A')}")
                        st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('Fecha_Fin', 'N/A')}")
                        st.write(f"**Tipo de Sangre:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
                        st.write(f"**Cantidad Necesaria:** {campana.get('Cantidad_Necesaria', 'N/A')} unidades")
                        st.write(f"**Estado:** `{campana.get('Estado_Campaña', 'N/A')}`")
                        
                        # Mostrar el hospital asociado al beneficiario
                        hospital_asociado_id = beneficiario_info.get('ID_Hospital_Asociado') if beneficiario_info else None
                        if hospital_asociado_id:
                            if hospital_asociado_id == hospital_id_logueado:
                                st.success(f"**Asociado con tu Hospital:** ✅ (ID: {hospital_asociado_id})")
                            else:
                                # Podrías obtener el nombre del hospital asociado si es diferente al tuyo
                                st.info(f"**Asociado con otro Hospital:** (ID: {hospital_asociado_id})")
                        else:
                            st.warning("**No asociado a ningún Hospital.**")

                        # Aquí podrías añadir una opción para que el hospital se "asocie" si no lo está
                        if beneficiario_info and not hospital_asociado_id:
                            if st.button(f"Asociar Beneficiario {beneficiario_nombre} a mi Hospital", key=f"associate_ben_{campana.get('ID_Campaña_Beneficiario')}"):
                                try:
                                    supabase_client.table("beneficiario").update({"ID_Hospital_Asociado": hospital_id_logueado}).eq("ID_Beneficiario", campana.get('ID_Beneficiario')).execute()
                                    st.success(f"Beneficiario {beneficiario_nombre} asociado a tu hospital.")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al asociar beneficiario: {e}")

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
        
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Cualquiera"]
        tipo_sangre_enfasis = st.selectbox("Énfasis en Tipo de Sangre (opcional)", sangre_options)
        
        estado_campana = st.selectbox("Estado Inicial de la Campaña", ["Próxima", "En Curso"])

        guardar_campana = st.form_submit_button("🚀 Publicar Campaña Solidaria")

        if guardar_campana:
            datos_campana = {
                "ID_Hospital": hospital_id_logueado,
                "Nombre_Campaña": nombre_campana,
                "Descripcion_Campaña": descripcion_campana,
                "Fecha_Inicio": fecha_inicio.isoformat(),
                "Fecha_Limite": fecha_fin.isoformat(),
                "Tipo_Sangre_Requerida": tipo_sangre_enfasis,
                "Estado_Campaña": estado_campana,
                "Fecha_Publicacion": datetime.now().isoformat()
            }
            if crear_nueva_campana_solidaria(datos_campana):
                st.balloons()
                st.rerun() 

    st.markdown("---")
    st.markdown("### Mis Campañas Solidarias Activas")

    # --- Sección para VER Campañas Solidarias Existentes ---
    campanas = obtener_campanas_solidarias_hospital(hospital_id_logueado)

    if campanas:
        for campana in campanas:
            estado = campana.get('Estado_Campaña', 'N/A')
            fecha_fin = campana.get('Fecha_Limite', 'N/A')
            
            with st.expander(f"Campaña: {campana.get('Nombre_Campaña', 'Sin Nombre')} (Estado: {estado})"):
                st.write(f"**ID Campaña:** {campana.get('ID_Campaña', 'N/A')}")
                st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                st.write(f"**Fecha de Inicio:** {campana.get('Fecha_Inicio', 'N/A')}")
                st.write(f"**Fecha de Fin:** {fecha_fin}")
                st.write(f"**Énfasis en Tipo de Sangre:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
            st.markdown("---")
    else:
        st.info("ℹ️ No has publicado ninguna campaña solidaria de recolección aún. ¡Usa el formulario de arriba para crear una!")


# --- Lógica principal de la página del Hospital ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Hospital':
        st.sidebar.title("Navegación Hospital 🧭")
        # Menú actualizado para el Hospital (sin "Solicitudes")
        menu = ["Perfil", "Campañas de Beneficiarios", "Campañas Solidarias"] 
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            hospital_perfil()
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