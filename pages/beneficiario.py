import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import time
from datetime import date

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Panel de Beneficiario",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="auto"
)

# Carga las variables de entorno para Supabase
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
else:
    st.error("SUPABASE_URL o SUPABASE_KEY no están configuradas en .env. No se puede conectar a la base de datos.")

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


def perfil_beneficiario_tab():
    st.markdown("## Datos de mi Perfil")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')
    user_email = st.session_state.get('user_email')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    try:
        # Obtener los datos del beneficiario de Supabase
        response = supabase_client.table("beneficiario").select("*").eq("id_beneficiario", user_db_id).limit(1).execute()

        if response.data:
            beneficiario_data = response.data[0]

            # Formulario para mostrar y modificar el perfil
            with st.form("perfil_form", clear_on_submit=False):
                st.info("Solo se pueden modificar los campos habilitados.")
                nombre = st.text_input("Nombre", value=beneficiario_data.get('nombreb', ''))
                email = st.text_input("Email", value=beneficiario_data.get('mail', ''), disabled=True)
                telefono = st.text_input("Teléfono", value=beneficiario_data.get('telefono', ''))
                direccion = st.text_input("Dirección", value=beneficiario_data.get('direccion', ''))
                tipo_sangre_beneficiario = st.text_input("Tipo de Sangre (Registrado)", value=beneficiario_data.get('tipo_de_sangre', ''), disabled=True)

                st.markdown("---")
                update_button = st.form_submit_button("Actualizar Perfil")

                if update_button:
                    # Validar si algo cambió
                    if (nombre == beneficiario_data.get('nombreb', '') and
                        telefono == beneficiario_data.get('telefono', '') and
                        direccion == beneficiario_data.get('direccion', '')):
                        st.warning("No hay cambios para actualizar.")
                        return

                    # Actualizar los datos en Supabase
                    update_data = {
                        "nombreb": nombre,
                        "telefono": telefono,
                        "direccion": direccion,
                    }
                    update_response = supabase_client.table("beneficiario").update(update_data).eq("id_beneficiario", user_db_id).execute()

                    if update_response.data:
                        st.success("¡Perfil actualizado con éxito!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error al actualizar el perfil: {update_response.error.message}")
                        st.warning("Detalles técnicos: " + str(update_response.error))

        else:
            st.warning("No se pudieron cargar los datos de tu perfil. Intenta nuevamente.")
            if st.button("Recargar Perfil"):
                st.rerun()
            return

    except Exception as e:
        st.error(f"Error al cargar/actualizar los datos del perfil: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la conexión a Supabase esté activa y las RLS permitan la lectura/escritura de tu perfil.")

# Nueva función para obtener la lista de hospitales
def obtener_hospitales():
    if supabase_client is None:
        return []
    try:
        response = supabase_client.table("hospital").select("id_hospital, nombre_hospital").order("nombre_hospital").execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"Error al obtener la lista de hospitales: {e}")
        return []

def crear_campana_tab():
    st.markdown("## 💉 Crear Nueva Campaña de Donación")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    # Obtener hospitales para el selectbox
    hospitales = obtener_hospitales()
    hospital_options = {h['nombre_hospital']: h['id_hospital'] for h in hospitales}
    hospital_nombres = list(hospital_options.keys())

    with st.form("nueva_campana_form", clear_on_submit=True):
        st.markdown("Completa los siguientes datos para solicitar una donación de sangre.")

        nombre_campana = st.text_input("Nombre de la Campaña", help="Un título para tu solicitud de donación, ej: 'Urgente para Juan Pérez'.")
        descripcion = st.text_area("📝 Descripción Detallada", help="Ej: 'Se necesita sangre para operación de emergencia en Hospital Central.', 'Para paciente con anemia crónica, se agradecerá cualquier tipo de sangre.'.")
        
        today = date.today()
        
        fecha_inicio_display = st.date_input("🗓️ Fecha de Inicio (automática)", value=today, disabled=True)
        fecha_fin = st.date_input("🗓️ Fecha Límite para la Donación", min_value=today, value=today, help="Fecha hasta la cual necesitas la donación.")
        
        selected_hospital_name = st.selectbox(
            "🏥 Selecciona el Hospital para la Campaña",
            hospital_nombres,
            help="Elige el hospital donde se realizará la donación."
        )
        selected_hospital_id = hospital_options.get(selected_hospital_name)
        
        try:
            beneficiario_response = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", user_db_id).limit(1).execute()
            if beneficiario_response.data:
                tipo_sangre_beneficiario = beneficiario_response.data[0]['tipo_de_sangre']
                st.info(f"Tu tipo de sangre registrado es: **{tipo_sangre_beneficiario}**. Esto se asociará a la campaña.")
            else:
                st.warning("No se pudo obtener tu tipo de sangre registrado.")
                tipo_sangre_beneficiario = None
        except Exception as e:
            st.error(f"Error al obtener el tipo de sangre del beneficiario: {e}")
            tipo_sangre_beneficiario = None
            
        
        submit_button = st.form_submit_button("Crear Campaña")

        if submit_button:
            if not nombre_campana or not descripcion or not selected_hospital_id:
                st.error("Por favor, completa todos los campos obligatorios: Nombre de la Campaña, Descripción y selecciona un Hospital.")
            elif fecha_fin < fecha_inicio_display:
                st.error("La fecha límite no puede ser anterior a la fecha de inicio.")
            else:
                try:
                    data_to_insert = {
                        "nombre_campana": nombre_campana,
                        "descripcion": descripcion,
                        "fecha_inicio": str(fecha_inicio_display),
                        "fecha_fin": str(fecha_fin),
                        "id_hospital": selected_hospital_id,
                        "id_beneficiario": user_db_id,
                        "estado_campana": "En curso"
                    }

                    insert_response = supabase_client.table("campana").insert(data_to_insert).execute()

                    if insert_response.data:
                        st.success(f"¡Campaña '{nombre_campana}' creada exitosamente!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error al crear la campaña: {insert_response.error.message}")
                        st.warning("Detalles técnicos: " + str(insert_response.error))

                except Exception as e:
                    st.error(f"Error al conectar con Supabase para crear campaña: {e}")
                    st.exception(e)


def mis_campanas_tab():
    st.markdown("## 📣 Mis Campañas Actuales")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    hospitales_data = obtener_hospitales()
    hospital_names_map = {h['id_hospital']: h['nombre_hospital'] for h in hospitales_data}

    try:
        campanas_response = supabase_client.table("campana").select("*").eq("id_beneficiario", user_db_id).order("fecha_fin", desc=False).execute()

        if campanas_response.data:
            st.subheader("Campañas Pendientes/En Curso:")
            found_active = False
            for campana in campanas_response.data:
                estado_lower = campana.get('estado_campana', '').lower()
                if estado_lower in ['en curso', 'próxima', 'activa']:
                    found_active = True
                    with st.container(border=True):
                        st.markdown(f"#### {campana.get('nombre_campana', 'Campaña sin nombre')}")
                        st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                        st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                        
                        hospital_id = campana.get('id_hospital')
                        hospital_name = hospital_names_map.get(hospital_id, 'Hospital Desconocido')
                        st.write(f"**Hospital:** {hospital_name}")
                        
                        st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")

                        if st.button(f"Finalizar Campaña", key=f"finalizar_{campana['id_campana']}"):
                            try:
                                update_response = supabase_client.table("campana").update({"estado_campana": "Finalizada"}).eq("id_campana", campana['id_campana']).execute()
                                if update_response.data:
                                    st.success(f"Campaña '{campana.get('nombre_campana', '')}' finalizada con éxito.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Error al finalizar la campaña: {update_response.error.message}")
                                    st.warning("Detalles técnicos: " + str(update_response.error))
                            except Exception as e:
                                st.error(f"Error al conectar con Supabase para finalizar campaña: {e}")
                                st.exception(e)
                        st.markdown("---")
            if not found_active:
                st.info("No tienes campañas activas o próximas en este momento.")

            st.subheader("Campañas Finalizadas:")
            found_finished = False
            for campana in campanas_response.data:
                if campana.get('estado_campana', '').lower() == 'finalizada':
                    found_finished = True
                    with st.expander(f"Campaña '{campana.get('nombre_campana', 'Sin nombre')}' - Finalizada"):
                        st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                        st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                        
                        hospital_id = campana.get('id_hospital')
                        hospital_name = hospital_names_map.get(hospital_id, 'Hospital Desconocido')
                        st.write(f"**Hospital:** {hospital_name}")
                        
                        st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")
            if not found_finished:
                st.info("No tienes campañas finalizadas.")


        else:
            st.info("Aún no has creado ninguna campaña de donación. ¡Anímate a crear una!")

    except Exception as e:
        st.error(f"Error al cargar tus campañas: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la tabla 'campana' exista y las RLS permitan la lectura.")


def beneficiario_perfil_page():
    # Asegúrate de que las session_state variables estén inicializadas
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_type' not in st.session_state:
        st.session_state['user_type'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'user_db_id' not in st.session_state:
        st.session_state['user_db_id'] = None

    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Beneficiario':
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        st.stop()

    st.markdown(f"<h1 style='color: var(--primary-red);'>👤 Panel de Beneficiario</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: var(--dark-grey-text);'>Gestiona tu perfil y campañas de donación.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Mover el botón de cerrar sesión a la barra lateral si está logueado
    if st.session_state['logged_in']:
        st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None, 'show_register_form': False}))
        st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")


    tab1, tab2, tab3 = st.tabs(["Mi Perfil", "Crear Campaña", "Mis Campañas"])

    with tab1:
        perfil_beneficiario_tab()
    with tab2:
        crear_campana_tab()
    with tab3:
        mis_campanas_tab()

if __name__ == "__main__":
    beneficiario_perfil_page()