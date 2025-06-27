import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, time as dt_time

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Panel de Hospital",
    page_icon="🏥", # Hospital icon
    layout="centered",
    initial_sidebar_state="auto"
)

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, confíguralas para que la conexión a la base de datos funcione.")
else:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
        supabase_client = None

# --- Estilos CSS Personalizados (copia exacta de inicio.py) ---
st.markdown("""
<style>
    /* Paleta de colores */
    :root {
        --primary-red: #E05A47; /* Rojo suave */
        --light-red: #F28C7D; /* Rojo más claro para acentos */
        --white: #FFFFFF;
        --light-grey: #F8F9FA; /* Fondo muy claro */
        --dark-grey-text: #333333; /* Color de texto principal */
        --medium-grey-text: #6c757d; /* Color de texto secundario */
    }

    body {
        font-family: 'Inter', sans-serif;
        color: var(--dark-grey-text);
        background-color: var(--light-grey); /* Fondo general de la app */
    }

    /* Títulos principales */
    h1 {
        color: var(--primary-red);
        text-align: center;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }

    h2 {
        color: var(--primary-red);
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    h3 {
        color: var(--primary-red);
        font-weight: 500;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    /* Subtítulos y texto informativo */
    p {
        color: var(--dark-grey-text);
        line-height: 1.6;
    }

    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* Estilo para botones */
    .stButton > button {
        background-color: var(--primary-red);
        color: var(--white);
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.25rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        background-color: var(--light-red);
        color: var(--white);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }

    /* Estilo para text_input y text_area */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea, 
    .stDateInput > div > div {
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 0.5rem 1rem;
        background-color: var(--white);
        color: var(--dark-grey-text);
    }

    /* Estilo para radio buttons (st.radio) */
    .stRadio > label {
        color: var(--dark-grey-text); /* Color del texto de la etiqueta del radio */
    }
    .stRadio div[data-baseweb="radio"] {
        background-color: var(--white); /* Fondo de cada opción de radio */
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 0.5rem;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s ease;
    }
    .stRadio div[data-baseweb="radio"]:hover {
        background-color: var(--light-grey);
    }
    /* Estilo para la opción de radio seleccionada */
    .stRadio div[data-baseweb="radio"][aria-checked="true"] {
        background-color: var(--primary-red); /* Fondo de la opción seleccionada */
        color: var(--white) !important; /* Color del texto de la opción seleccionada */
        border-color: var(--primary-red);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stRadio div[data-baseweb="radio"][aria-checked="true"] label {
        color: var(--white) !important; /* Fuerza el color del texto de la opción seleccionada */
    }
    /* Estilo del círculo del radio button */
    .stRadio div[data-baseweb="radio"] svg {
        fill: var(--primary-red); /* Color del círculo cuando no está seleccionado */
    }
    .stRadio div[data-baseweb="radio"][aria-checked="true"] svg {
        fill: var(--white); /* Color del círculo cuando está seleccionado */
    }


    /* Contenedores con borde */
    .stContainer {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: var(--white);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Sidebar */
    .css-1d391kg { /* Selector para el fondo del sidebar */
        background-color: var(--light-grey);
    }
    .css-1lcbmhc { /* Selector para el texto del sidebar */
        color: var(--dark-grey-text);
    }
    .css-1lcbmhc h1 { /* Título del sidebar */
        color: var(--primary-red);
    }
    .css-1lcbmhc .st-bd { /* Elementos del selectbox en sidebar */
        color: var(--dark-grey-text);
    }
    .css-1lcbmhc .st-by { /* Botones en sidebar */
        background-color: var(--primary-red);
        color: var(--white);
    }
    .css-1lcbmhc .st-by:hover {
        background-color: var(--light-red);
    }

</style>
""", unsafe_allow_html=True)


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
            # Incluir 'descripcion' y 'fecha_fin' para mostrar detalles completos
            response = supabase_client.table("campana").select("id_campana, nombre_campana, fecha_inicio, fecha_fin, estado_campana, descripcion, id_beneficiario").eq("id_hospital", hospital_id).order("fecha_inicio", desc=False).execute()
            if response.data:
                return response.data
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas solidarias: {e}")
            return []
    return []

# Función corregida: Usar "*" para el conteo de inscripciones
def obtener_conteo_inscripciones_campana(id_campana):
    if supabase_client is None:
        return 0
    try:
        # Se ha corregido la selección a "*" para evitar el error de columna inexistente
        response = supabase_client.table("donaciones").select("*", count="exact").eq("id_campana", id_campana).execute()
        if response.count is not None:
            return response.count
        else:
            return 0
    except Exception as e:
        st.error(f"❌ Error al obtener conteo de inscripciones para campaña {id_campana}: {e}")
        return 0


def crear_nueva_campana_solidaria(datos_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña solidaria.")
        return False
    try:
        # Asegúrate de que 'id_beneficiario' sea None para campañas creadas por hospitales
        # La tabla 'campana' debe permitir NULL en 'id_beneficiario' si esta es la intención.
        # Si la columna 'id_beneficiario' no debe ser enviada cuando es NULL, entonces elimínala del diccionario
        # si es None. Aquí la enviamos explícitamente como None.
        
        data, count = supabase_client.table("campana").insert(datos_campana).execute()
        if data and len(data) > 0:
            st.success("🎉 ¡Nueva campaña solidaria publicada con éxito!")
            return True
        else:
            st.error(f"❌ No se pudo publicar la nueva campaña solidaria. Detalles: {data}")
            return False
    except Exception as e:
        st.error(f"❌ Error al crear nueva campaña solidaria: {e}")
        return False

def finalizar_campana_solidaria(campana_id):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede finalizar la campaña.")
        return False
    try:
        response = supabase_client.table("campana").update({"estado_campana": "Finalizada"}).eq("id_campana", campana_id).execute()
        if response.data:
            st.success(f"✅ Campaña {campana_id} finalizada con éxito.")
            return True
        else:
            st.error(f"❌ Error al finalizar campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al finalizar campaña: {e}")
        return False


# --- Nuevas funciones para la gestión de solicitudes de campaña por el hospital ---

def obtener_solicitudes_campana_pendientes(hospital_id):
    """Obtiene las solicitudes de campaña de beneficiarios que están pendientes de aprobación."""
    if supabase_client is None:
        return []
    try:
        response = supabase_client.table("campana").select("id_campana, nombre_campana, descripcion, fecha_inicio, fecha_fin, id_beneficiario, estado_campana").eq("id_hospital", hospital_id).eq("estado_aprobacion_hospital", "Pendiente").order("fecha_inicio", desc=False).execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"❌ Error al obtener solicitudes de campaña pendientes: {e}")
        return []

def obtener_nombre_beneficiario(beneficiario_id):
    """Obtiene el nombre de un beneficiario dado su ID."""
    if supabase_client is None:
        return "Desconocido"
    try:
        response = supabase_client.table("beneficiario").select("nombreb").eq("id_beneficiario", beneficiario_id).limit(1).execute()
        if response.data and response.data[0]['nombreb']:
            return response.data[0]['nombreb']
        else:
            return "Beneficiario Desconocido"
    except Exception as e:
        # st.error(f"Error al obtener nombre del beneficiario {beneficiario_id}: {e}") # Comentado para evitar spam de errores si muchos beneficiarios no tienen nombre
        return "Beneficiario Desconocido"

def aceptar_solicitud_campana(campana_id):
    """Actualiza el estado de una campaña a 'Aprobada' y 'En Curso'."""
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede aceptar la solicitud.")
        return False
    try:
        response = supabase_client.table("campana").update({
            "estado_aprobacion_hospital": "Aprobada",
            "estado_campana": "En Curso" # La campaña se activa cuando es aprobada
        }).eq("id_campana", campana_id).execute()
        
        if response.data:
            st.success(f"✅ Solicitud de campaña {campana_id} **APROBADA** con éxito. La campaña ya está activa para donantes.")
            return True
        else:
            st.error(f"❌ Error al aceptar solicitud de campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al aceptar solicitud: {e}")
        return False

def rechazar_solicitud_campana(campana_id):
    """Actualiza el estado de una campaña a 'Rechazada'."""
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede rechazar la solicitud.")
        return False
    try:
        response = supabase_client.table("campana").update({
            "estado_aprobacion_hospital": "Rechazada",
            "estado_campana": "Rechazada" # La campaña también cambia su estado principal a rechazada
        }).eq("id_campana", campana_id).execute()
        
        if response.data:
            st.warning(f"🚫 Solicitud de campaña {campana_id} **RECHAZADA** con éxito.")
            return True
        else:
            st.error(f"❌ Error al rechazar solicitud de campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al rechazar solicitud: {e}")
        return False


def hospital_solicitudes_campana():
    st.markdown("## Solicitudes de Campaña Pendientes 📬")
    st.markdown("---")
    st.write("Revisa las solicitudes de campañas de donación enviadas por los beneficiarios que requieren tu aprobación.")

    hospital_id_logueado = st.session_state.get("user_db_id")

    if not hospital_id_logueado:
        st.warning("⚠️ No se encontró el ID de hospital en la sesión. Por favor, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return
    
    solicitudes_pendientes = obtener_solicitudes_campana_pendientes(hospital_id_logueado)

    if solicitudes_pendientes:
        for solicitud in solicitudes_pendientes:
            campana_id = solicitud.get('id_campana')
            nombre_beneficiario = obtener_nombre_beneficiario(solicitud.get('id_beneficiario'))
            
            with st.container(border=True):
                st.markdown(f"### Solicitud: {solicitud.get('nombre_campana', 'Campaña sin nombre')}")
                st.write(f"**De:** {nombre_beneficiario}")
                st.write(f"**Descripción:** {solicitud.get('descripcion', 'N/A')}")
                st.write(f"**Fecha de Inicio Solicitada:** {solicitud.get('fecha_inicio', 'N/A')}")
                st.write(f"**Fecha Límite Solicitada:** {solicitud.get('fecha_fin', 'N/A')}")
                st.write(f"**Estado Actual:** `{solicitud.get('estado_campana', 'N/A')}` (Aprobación: `Pendiente`)")

                col_aprobar, col_rechazar = st.columns(2)
                with col_aprobar:
                    if st.button(f"✅ Aceptar Solicitud", key=f"aceptar_{campana_id}"):
                        if aceptar_solicitud_campana(campana_id):
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                with col_rechazar:
                    if st.button(f"❌ Rechazar Solicitud", key=f"rechazar_{campana_id}"):
                        if rechazar_solicitud_campana(campana_id):
                            time.sleep(1)
                            st.rerun()
            st.markdown("---")
    else:
        st.info("🎉 No hay solicitudes de campaña pendientes para tu hospital en este momento.")


# --- Definición de las funciones de sección del Hospital ---
def hospital_perfil():
    st.markdown("## Mi Perfil de Hospital 🏥")
    st.markdown("---")
    st.write("Gestiona la información de tu hospital y asegura que tus datos estén actualizados.")

    email_usuario_logueado = st.session_state.get("user_email", "hospital@ejemplo.com")
    hospital_id_logueado = st.session_state.get("user_db_id")

    perfil_existente = obtener_datos_hospital(email_usuario_logueado)

    valores_iniciales = {
        "nombre_hospital": "",
        "mail": email_usuario_logueado,
        "telefono": "",
        "direccion": "",
        "sitio_web": "",
        "descripcion": "",
    }

    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombre_hospital', 'N/A')}**")
        valores_iniciales["nombre_hospital"] = perfil_existente.get("nombre_hospital", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["sitio_web"] = perfil_existente.get("sitio_web", "")
        valores_iniciales["descripcion"] = perfil_existente.get("descripcion", "")

    with st.form("hospital_perfil_form", border=True):
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
                "descripcion": descripcion,
            }
            if perfil_existente:
                actualizar_datos_hospital(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de hospital aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el hospital ya exista en la base de datos para poder actualizar su perfil.")


def hospital_campanas_solidarias():
    st.markdown("## Mis Campañas Solidarias (Recolección en Hospital) 📢")
    st.markdown("---")
    st.write("Aquí puedes gestionar las campañas de donación de sangre que tu hospital ha organizado para la recolección en sus propias instalaciones.")

    hospital_id_logueado = st.session_state.get("user_db_id")

    if not hospital_id_logueado:
        st.warning("⚠️ Para gestionar campañas solidarias, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    # --- Sección para CREAR Nueva Campaña Solidaria ---
    st.markdown("### ➕ Crear Nueva Campaña Solidaria")
    with st.form("nueva_campana_solidaria_form", border=True):
        nombre_campana = st.text_input("Nombre de la Campaña", placeholder="Jornada de Donación - Verano 2025")
        
        # Validar que la fecha de inicio no sea en el pasado
        fecha_inicio_campana = st.date_input("Fecha de Inicio de la Campaña", value=datetime.today().date(), min_value=datetime.today().date())
        
        # Validar que la fecha de fin no sea anterior a la de inicio
        fecha_fin_campana = st.date_input("Fecha de Fin de la Campaña", value=fecha_inicio_campana, min_value=fecha_inicio_campana)

        descripcion_campana = st.text_area("Descripción de la Campaña", help="Detalles sobre el objetivo, horario o requisitos específicos de esta campaña de recolección.")
        
        estado_campana_seleccionado = st.selectbox("Estado de la Campaña", ["Próxima", "En Curso", "Finalizada"], index=0) # Default to 'Próxima'

        guardar_campana = st.form_submit_button("🚀 Publicar Campaña")

        if guardar_campana:
            if not nombre_campana or not descripcion_campana:
                st.error("Por favor, completa el nombre y la descripción de la campaña.")
            elif fecha_fin_campana < fecha_inicio_campana:
                st.error("La fecha de fin no puede ser anterior a la fecha de inicio.")
            else:
                datos_campana = {
                    "id_hospital": hospital_id_logueado,
                    "nombre_campana": nombre_campana,
                    "descripcion": descripcion_campana,
                    "fecha_inicio": fecha_inicio_campana.isoformat(),
                    "fecha_fin": fecha_fin_campana.isoformat(),
                    "estado_campana": estado_campana_seleccionado,
                    "id_beneficiario": None, # Explícitamente None para campañas de hospital
                    "estado_aprobacion_hospital": "Aprobada" # Las campañas creadas por el hospital se auto-aprueban
                }
                if crear_nueva_campana_solidaria(datos_campana):
                    st.balloons()
                    st.rerun()

    st.markdown("---")
    st.markdown("### Campañas Solidarias Existentes")

    campanas = obtener_campanas_solidarias_hospital(hospital_id_logueado)

    if campanas:
        for campana in campanas:
            # Solo mostrar campañas que son propias del hospital (id_beneficiario es None) o que ya están aprobadas
            if campana.get('id_beneficiario') is None or campana.get('estado_aprobacion_hospital') == 'Aprobada':
                estado = campana.get("estado_campana", "N/A")
                nombre_campana = campana.get('nombre_campana', 'Sin Nombre')
                descripcion = campana.get('descripcion', 'N/A')
                fecha_inicio = campana.get('fecha_inicio', 'N/A')
                fecha_fin = campana.get('fecha_fin', 'N/A')
                
                conteo_inscripciones = obtener_conteo_inscripciones_campana(campana.get('id_campana'))

                with st.container(border=True):
                    st.markdown(f"#### {nombre_campana}")
                    st.write(f"**Estado:** `{estado}`")
                    st.write(f"**Descripción:** {descripcion}")
                    st.write(f"**Fecha de Inicio:** {fecha_inicio}")
                    st.write(f"**Fecha de Fin:** {fecha_fin}")
                    st.write(f"**Donantes Inscriptos:** {conteo_inscripciones}")
                    
                    # Botón para finalizar campaña solo si no está ya finalizada
                    if estado != "Finalizada":
                        if st.button(f"Finalizar Campaña '{nombre_campana}'", key=f"finalizar_{campana.get('id_campana')}"):
                            if finalizar_campana_solidaria(campana.get("id_campana")):
                                st.rerun()
                    else:
                        st.info("Esta campaña ha sido finalizada.")
                st.markdown("---")
    else:
        st.info("No hay campañas solidarias disponibles para tu hospital.")


# --- Función principal de la página del Hospital ---
def hospital_panel_page():
    # Inicializa las session_state variables si no existen
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_type' not in st.session_state:
        st.session_state['user_type'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'user_db_id' not in st.session_state:
        st.session_state['user_db_id'] = None

    # Verifica si el usuario está logueado como Hospital
    if not st.session_state.get("logged_in") or st.session_state.get("user_type") != "Hospital":
        st.warning("⚠️ Debes iniciar sesión como **Hospital** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()
        st.stop() # Detiene la ejecución si no está logueado como Hospital

    st.markdown(f"<h1 style='color: var(--primary-red);'>🏥 Panel de Hospital</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: var(--dark-grey-text);'>Gestiona tu perfil y organiza campañas de donación.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Botón de cerrar sesión en la barra lateral
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None}))
    st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")

    # Navegación por pestañas
    tab1, tab2, tab3 = st.tabs(["Mi Perfil", "Campañas Solidarias", "Solicitudes de Campaña"]) # Nueva pestaña para solicitudes

    with tab1:
        hospital_perfil()
    with tab2:
        hospital_campanas_solidarias()
    with tab3: # Nueva pestaña
        hospital_solicitudes_campana()


if __name__ == "__main__":
    hospital_panel_page()
