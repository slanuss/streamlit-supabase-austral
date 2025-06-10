import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime


# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Panel de Donante",
    page_icon="🩸", # Using the blood drop icon
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
    st.info("Por favor, configúralas para que la conexión a la base de datos funcione.")
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


# --- Función para obtener datos del donante ---
def obtener_datos_donante(donante_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del donante.")
        return None
    try:
        response = supabase_client.table("donante").select("*, id_donante").eq("mail", donante_email).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del donante: {e}")
        return None


# --- Función para actualizar datos del donante ---
def actualizar_datos_donante(donante_email, datos):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del donante.")
        return False
    try:
        response = supabase_client.table("donante").update(datos).eq("mail", donante_email).execute()
        if response.data:
            st.success("✅ ¡Perfil actualizado con éxito!")
            time.sleep(1)
            st.rerun()
            return True
        else:
            st.error(f"❌ Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False


# --- Funciones de Campañas ---
def obtener_campanas_activas():
    if supabase_client:
        try:
            # Obtener todas las campañas, incluyendo las finalizadas para el filtro de fecha
            response = supabase_client.table("campana").select("id_campana, nombre_campana, fecha_inicio, fecha_fin, id_hospital, id_beneficiario, descripcion, estado_campana").order("fecha_fin", desc=False).execute()
            
            if response.data:
                # Filtrar campañas activas cuya fecha_fin sea posterior o igual a hoy
                hoy = datetime.now().date()
                campanas_filtradas = [
                    c for c in response.data
                    if c.get('estado_campana', '').lower() == 'en curso' and \
                       c.get('fecha_fin') and datetime.strptime(c['fecha_fin'], "%Y-%m-%d").date() >= hoy
                ]
                return campanas_filtradas
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas desde Supabase: {e}")
            return []
    return []


def inscribirse_campana(campana_id: int, donante_id: int):
    if supabase_client:
        try:
            existing_inscription = supabase_client.table("donaciones").select("*").eq("id_campana", campana_id).eq("id_donante", donante_id).execute()
            if existing_inscription.data:
                st.warning("⚠️ Ya estás inscrito en esta campaña.")
                return False

            # --- CORRECCIÓN APLICADA AQUÍ: ELIMINADO 'estado_donacion' ---
            data, count = supabase_client.table("donaciones").insert({
                "id_campana": campana_id,
                "id_donante": donante_id
            }).execute()
            
            if data and len(data) > 0:
                st.success(f"🎉 ¡Te has inscrito exitosamente a la campaña **{campana_id}**!")
                return True
            else:
                st.error("❌ No se pudo completar la inscripción.")
                return False
        except Exception as e:
            st.error(f"❌ Error al inscribirse en la campaña: {e}")
            return False
    return False


# --- Función para obtener datos de hospitales ---
def obtener_hospitales():
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos de hospitales.")
        return []
    try:
        response = supabase_client.table("hospital").select("nombre_hospital, direccion, telefono").execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"Error al obtener datos de hospitales: {e}")
        return []


# --- Definición de las funciones de sección ---
def donante_perfil():
    st.markdown("## Mi Perfil de Donante 📝")
    st.markdown("---")
    st.write("Actualiza y gestiona tu información personal para ayudarnos a conectar mejor con quienes te necesitan.")


    email_usuario_logueado = st.session_state.get('user_email', 'donante@ejemplo.com')
    donante_id_logueado = st.session_state.get('user_db_id')


    perfil_existente = obtener_datos_donante(email_usuario_logueado)


    valores_iniciales = {
        "nombred": "", "mail": email_usuario_logueado, "telefono": "", "direccion": "",
        "edad": 18, "sexo": "Masculino", "tipo_de_sangre": "A+",
        "antecedentes": "", "medicaciones": "", "cumple_requisitos": False
    }
  
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombred', 'N/A')}**")
        valores_iniciales["nombred"] = perfil_existente.get("nombred", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["edad"] = perfil_existente.get("edad", 18)
      
        sexo_db = perfil_existente.get("sexo")
        if sexo_db == 'M':
            valores_iniciales["sexo"] = "Masculino"
        elif sexo_db == 'F':
            valores_iniciales["sexo"] = "Femenino"
        elif sexo_db == 'O':
            valores_iniciales["sexo"] = "Otro"
        else:
            valores_iniciales["sexo"] = "Masculino"


        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("tipo_de_sangre") in sangre_opciones:
            valores_iniciales["tipo_de_sangre"] = perfil_existente.get("tipo_de_sangre")
      
        valores_iniciales["antecedentes"] = perfil_existente.get("antecedentes", "")
        valores_iniciales["medicaciones"] = perfil_existente.get("medicaciones", "")
        valores_iniciales["cumple_requisitos"] = perfil_existente.get("cumple_requisitos", False)


    with st.form("perfil_form", border=True): # Add border to the form
        st.markdown("#### Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre y Apellido", value=valores_iniciales["nombred"])
            mail = st.text_input("Mail Personal", value=valores_iniciales["mail"], disabled=True)
            telefono = st.text_input("Teléfono", value=valores_iniciales["telefono"])
        with col2:
            direccion = st.text_input("Dirección", value=valores_iniciales["direccion"])
            edad = st.number_input("Edad", min_value=18, max_value=100, step=1, value=valores_iniciales["edad"])
          
            sexo_options = ["Masculino", "Femenino", "Otro"]
            sexo_index = sexo_options.index(valores_iniciales["sexo"]) if valores_iniciales["sexo"] in sexo_options else 0
            sexo_seleccionado = st.selectbox("Sexo", sexo_options, index=sexo_index)


        st.markdown("#### Información Médica")
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        sangre_index = sangre_options.index(valores_iniciales["tipo_de_sangre"]) if valores_iniciales["tipo_de_sangre"] in sangre_options else 0
        tipo_de_sangre = st.selectbox("Tipo de Sangre", sangre_options, index=sangre_index)


        antecedentes = st.text_area("Antecedentes Médicos (ej. alergias, cirugías previas)", value=valores_iniciales["antecedentes"])
        medicaciones = st.text_area("Medicaciones Actuales (ej. medicamentos que tomas)", value=valores_iniciales["medicaciones"])
      
        cumple_requisitos_cb = st.checkbox("¿Cumples con los requisitos generales para donar sangre?", value=valores_iniciales["cumple_requisitos"])
      
        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")


        if guardar:
            sexo_para_db = ""
            if sexo_seleccionado == "Masculino":
                sexo_para_db = "M"
            elif sexo_seleccionado == "Femenino":
                sexo_para_db = "F"
            elif sexo_seleccionado == "Otro":
                sexo_para_db = "O"


            datos_a_guardar = {
                "nombred": nombre, "mail": mail, "telefono": telefono, "direccion": direccion,
                "edad": edad, "sexo": sexo_para_db,
                "tipo_de_sangre": tipo_de_sangre,
                "antecedentes": antecedentes, "medicaciones": medicaciones,
                "cumple_requisitos": cumple_requisitos_cb,
            }
            if perfil_existente:
                actualizar_datos_donante(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de donante no se realiza desde aquí.")
                st.info("Por favor, ve a la página principal para 'Crear una Cuenta Nueva' como Donante si aún no tienes una, o 'Inicia Sesión' si ya la tienes y quieres actualizar tu perfil.")


# --- Funciones de Campañas y Hospitales ---
def donante_campanas():
    st.markdown("## Campañas de Donación Disponibles ❤️")
    st.markdown("---")
    st.write("Aquí puedes explorar las solicitudes de donación de sangre y ofrecer tu ayuda.")


    campanas = obtener_campanas_activas()
    donante_id_logueado = st.session_state.get('user_db_id')


    if not donante_id_logueado:
        st.warning("⚠️ Para inscribirte a campañas, asegúrate de que tu perfil de donante esté completo y tenga un ID válido. Completa el formulario de 'Perfil'.")


    if campanas:
        for campana in campanas:
            with st.container(border=True): # Use st.container with border for each campaign
                campana_nombre = campana.get('nombre_campana', 'Sin Nombre')
                beneficiario_id = campana.get('id_beneficiario')
                tipo_sangre_beneficiario = "N/A"
                if beneficiario_id and supabase_client:
                    try:
                        beneficiario_data = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", beneficiario_id).execute()
                        if beneficiario_data.data:
                            tipo_sangre_beneficiario = beneficiario_data.data[0].get('tipo_de_sangre', 'N/A')
                    except Exception as e:
                        st.warning(f"No se pudo obtener el tipo de sangre del beneficiario para la campaña {campana_nombre}: {e}")


                campana_id = campana.get('id_campana')


                st.markdown(f"### Campaña: {campana_nombre}")
                st.write(f"**Tipo de Sangre Requerida:** **{tipo_sangre_beneficiario}**")
                st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                st.write(f"**ID de Campaña:** `{campana_id if campana_id else 'N/A'}`")
              
                if donante_id_logueado and campana_id is not None:
                    if st.button(f"✨ Inscribirme a esta Campaña", key=f"inscribir_{campana_id}"):
                        if inscribirse_campana(campana_id, donante_id_logueado):
                            st.balloons()
                        else:
                            st.error("Fallo la inscripción.")
                else:
                    st.info("Inicia sesión y completa tu perfil para poder inscribirte.")
            st.markdown("---")
    else:
        st.info("ℹ️ No hay campañas de donación activas en este momento. ¡Vuelve pronto!")


def donante_hospitales():
    st.markdown("## Hospitales Asociados 🏥")
    st.markdown("---")
    st.info("Aquí encontrarás la información de contacto de los hospitales asociados para tus donaciones.")
    
    hospitales = obtener_hospitales()

    if hospitales:
        st.write("Puedes contactar a los siguientes hospitales para donar:")
        for hospital in hospitales:
            with st.container(border=True): # Use st.container with border for each hospital
                nombre = hospital.get('nombre_hospital', 'Nombre no disponible')
                direccion = hospital.get('direccion', 'Dirección no disponible')
                telefono = hospital.get('telefono', 'Teléfono no disponible')
                
                st.markdown(f"#### {nombre}")
                st.write(f"**Dirección:** {direccion}")
                st.write(f"**Teléfono:** {telefono}")
            st.markdown("---")
    else:
        st.info("ℹ️ No se encontraron hospitales asociados en la base de datos en este momento.")

    st.info("💡 **Consejo:** Para futuras mejoras, podemos volver a implementar un mapa interactivo una vez que las dependencias estén estables.")


def donante_requisitos():
    st.markdown("## Requisitos para Donar Sangre ✅")
    st.markdown("---")
    st.write("Infórmate sobre los criterios esenciales para ser un donante apto. Tu salud es nuestra prioridad.")
    st.markdown("""
    * **Edad:** Generalmente entre 18 y 65 años (con excepciones).
    * **Peso:** Mínimo de 50 kg.
    * **Salud General:** Sentirse bien y no tener enfermedades graves.
    * **Hemoglobina:** Nivel adecuado de hemoglobina.
    * **No haber donado recientemente:** Esperar el tiempo indicado entre donaciones.
    * **Sin tatuajes o piercings recientes:** Respetar el período de espera.
    * **Sin ciertas medicaciones o antecedentes:** Consultar con el personal médico.
    """)
    st.info("Esta es una lista general. Siempre consulta los requisitos específicos del centro de donación.")


# --- Función principal de la página de Donante ---
def donante_perfil_page():
    # Inicializa las session_state variables si no existen
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_type' not in st.session_state:
        st.session_state['user_type'] = None
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None
    if 'user_db_id' not in st.session_state:
        st.session_state['user_db_id'] = None


    # Verifica si el usuario está logueado como Donante
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Donante':
        st.warning("Debes iniciar sesión como Donante para acceder a esta página.")
        st.stop() # Detiene la ejecución de la página


    st.markdown(f"<h1 style='color: var(--primary-red);'>👤 Panel de Donante</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: var(--dark-grey-text);'>Gestiona tu perfil y descubre campañas de donación.</p>", unsafe_allow_html=True)
    st.markdown("---")


    # Botón de cerrar sesión en la barra lateral
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None}))
    st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")


    # Crea las pestañas para el donante
    tab1, tab2, tab3, tab4 = st.tabs(["Mi Perfil", "Campañas Activas", "Hospitales", "Requisitos"])


    with tab1:
        donante_perfil()
    with tab2:
        donante_campanas()
    with tab3:
        donante_hospitales()
    with tab4:
        donante_requisitos()


if __name__ == "__main__":
    donante_perfil_page()