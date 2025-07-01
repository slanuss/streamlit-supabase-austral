import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import folium # Importar Folium para mapas
from streamlit_folium import st_folium # Importar para mostrar mapas en Streamlit
import requests # Importar para hacer peticiones HTTP a la API de geocodificación


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
# Nueva variable para la clave API de OpenCage
OPENCAGE_API_KEY = os.environ.get("OPENCAGE_API_KEY")


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


# --- Mapa de compatibilidad de sangre (DONANTE A RECEPTOR) ---
# Este diccionario indica a qué tipos de sangre puede donar cada grupo.
# Por ejemplo, 'O-' puede donar a todos, mientras que 'AB+' solo a 'AB+'.
BLOOD_COMPATIBILITY_MAP = {
    "O-": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], # Donante Universal
    "O+": ["A+", "B+", "AB+", "O+"],
    "A-": ["A+", "A-", "AB+", "AB-"],
    "A+": ["A+", "AB+"],
    "B-": ["B+", "B-", "AB+", "AB-"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB+", "AB-"],
    "AB+": ["AB+"]
}


# --- Función para obtener datos del donante ---
def obtener_datos_donante(donante_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del donante.")
        return None
    try:
        response = supabase_client.table("donante").select("*, id_donante, tipo_de_sangre").eq("mail", donante_email).execute()
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


# --- Función para obtener el tipo de sangre de un beneficiario ---
def obtener_tipo_sangre_beneficiario(beneficiario_id):
    if supabase_client is None:
        return None
    try:
        response = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", beneficiario_id).limit(1).execute()
        if response.data and response.data[0]['tipo_de_sangre']:
            return response.data[0]['tipo_de_sangre']
        else:
            return None
    except Exception as e:
        st.warning(f"No se pudo obtener el tipo de sangre del beneficiario {beneficiario_id}: {e}")
        return None


# --- Funciones de Campañas ---
def obtener_campanas_activas():
    if supabase_client:
        try:
            # Obtener todas las campañas, incluyendo 'id_beneficiario' para la compatibilidad
            # y 'estado_aprobacion_hospital' para filtrar
            response = supabase_client.table("campana").select("id_campana, nombre_campana, fecha_inicio, fecha_fin, id_hospital, id_beneficiario, descripcion, estado_campana, estado_aprobacion_hospital").order("fecha_fin", desc=False).execute()
            
            if response.data:
                hoy = datetime.now().date()
                campanas_filtradas = []
                for c in response.data:
                    # Asegurarse de que los valores existen y son strings antes de llamar a .lower()
                    estado_campana_str = c.get('estado_campana')
                    estado_aprobacion_hospital_str = c.get('estado_aprobacion_hospital')
                    fecha_fin_str = c.get('fecha_fin')

                    is_en_curso = isinstance(estado_campana_str, str) and estado_campana_str.lower() == 'en curso'
                    is_aprobada = isinstance(estado_aprobacion_hospital_str, str) and estado_aprobacion_hospital_str.lower() == 'aprobada'
                    
                    is_valid_date = False
                    if isinstance(fecha_fin_str, str):
                        try:
                            fecha_fin_date = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
                            is_valid_date = fecha_fin_date >= hoy
                        except ValueError:
                            # st.warning(f"Fecha de fin inválida para campaña {c.get('id_campana')}: {fecha_fin_str}")
                            is_valid_date = False

                    if is_en_curso and is_aprobada and is_valid_date:
                        campanas_filtradas.append(c)
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


# --- Función para geocodificar una dirección usando OpenCage Geocoding API ---
def geocode_address(address: str):
    if not OPENCAGE_API_KEY:
        st.error("❌ Error: La clave API de OpenCage no está configurada. Por favor, añádela como variable de entorno 'OPENCAGE_API_KEY'.")
        return None, None
    
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": address,
        "key": OPENCAGE_API_KEY,
        "language": "es", # Idioma de los resultados
        "no_annotations": 1 # No incluir metadatos extra para una respuesta más ligera
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        data = response.json()
        
        if data and data['results']:
            # Tomamos el primer resultado
            lat = data['results'][0]['geometry']['lat']
            lon = data['results'][0]['geometry']['lng']
            return lat, lon
        else:
            st.warning(f"⚠️ No se encontraron coordenadas para la dirección: {address}")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al conectar con la API de geocodificación: {e}")
        return None, None
    except KeyError:
        st.error(f"❌ Error al parsear la respuesta de geocodificación para: {address}. Formato inesperado.")
        return None, None


# --- Definición de las funciones de sección ---
def donante_perfil():
    st.markdown("## Mi Perfil de Donante 📝")
    st.markdown("---")
    st.write("Actualiza y gestiona tu información personal para ayudarnos a conectar mejor con quienes te necesitan.")


    email_usuario_logueado = st.session_state.get('user_email', 'donante@ejemplo.com')
    donante_id_logueado = st.session_state.get('user_db_id')


    perfil_existente = obtener_datos_donante(email_usuario_logueado)

    # Inicialización de valores_iniciales SIEMPRE al principio
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


    donante_id_logueado = st.session_state.get('user_db_id')
    donante_email_logueado = st.session_state.get('user_email')


    if not donante_id_logueado:
        st.warning("⚠️ Para inscribirte a campañas, asegúrate de que tu perfil de donante esté completo y tenga un ID válido. Completa el formulario de 'Perfil'.")
        return

    # Obtener el tipo de sangre del donante logueado
    donante_data = obtener_datos_donante(donante_email_logueado)
    donante_tipo_sangre = donante_data.get('tipo_de_sangre') if donante_data else None

    if not donante_tipo_sangre:
        st.warning("⚠️ No se pudo obtener tu tipo de sangre. Por favor, completa tu perfil para ver campañas compatibles.")
        return

    st.info(f"Tu tipo de sangre registrado es: **{donante_tipo_sangre}**")


    campanas_disponibles = obtener_campanas_activas()
    campanas_compatibles = []

    if campanas_disponibles:
        for campana in campanas_disponibles:
            beneficiario_id = campana.get('id_beneficiario')
            tipo_sangre_requerida = None

            # Si la campaña tiene un beneficiario asociado, obtener su tipo de sangre
            if beneficiario_id:
                tipo_sangre_requerida = obtener_tipo_sangre_beneficiario(beneficiario_id)
            else:
                # Si la campaña no tiene beneficiario (ej. es una campaña de hospital),
                # se asume que puede recibir de cualquier tipo o se filtra por un criterio específico
                # Para este ejemplo, si no hay beneficiario, se considera universalmente compatible.
                tipo_sangre_requerida = "Universal" # Un valor ficticio para indicar universalidad

            # Verificar compatibilidad
            if donante_tipo_sangre in BLOOD_COMPATIBILITY_MAP:
                # Si la campaña es de un beneficiario, verificar si el tipo de sangre del donante
                # puede donar al tipo de sangre requerido por el beneficiario.
                if tipo_sangre_requerida != "Universal" and tipo_sangre_requerida in BLOOD_COMPATIBILITY_MAP[donante_tipo_sangre]:
                    campanas_compatibles.append(campana)
                # Si es una campaña "Universal" (sin beneficiario), siempre es compatible
                elif tipo_sangre_requerida == "Universal":
                     campanas_compatibles.append(campana)
            else:
                st.warning(f"Tipo de sangre '{donante_tipo_sangre}' no reconocido en el mapa de compatibilidad. Por favor, verifica tu perfil.")
                break # Salir del bucle si el tipo de sangre del donante es inválido


    if campanas_compatibles:
        st.subheader("Campañas compatibles con tu tipo de sangre:")
        for campana in campanas_compatibles:
            with st.container(border=True): # Use st.container with border for each campaign
                campana_nombre = campana.get('nombre_campana', 'Sin Nombre')
                beneficiario_id = campana.get('id_beneficiario')
                tipo_sangre_beneficiario = "N/A" # Default para si no hay beneficiario o falla la consulta
                if beneficiario_id and supabase_client:
                    # Aquí volvemos a obtener el tipo de sangre del beneficiario para mostrarlo,
                    # aunque ya lo usamos para el filtro. Podría optimizarse si se guarda
                    # el tipo de sangre directamente en el objeto campana.
                    beneficiario_data = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", beneficiario_id).execute()
                    if beneficiario_data.data:
                        tipo_sangre_beneficiario = beneficiario_data.data[0].get('tipo_de_sangre', 'N/A')


                campana_id = campana.get('id_campana')


                st.markdown(f"### Campaña: {campana_nombre}")
                if beneficiario_id: # Mostrar tipo de sangre requerido solo si es de un beneficiario
                    st.write(f"**Tipo de Sangre Compatible con:** **{tipo_sangre_beneficiario}**") # CAMBIO AQUÍ
                else:
                    st.write(f"**Tipo de Sangre Compatible con:** **Cualquiera** (Campaña solidaria del hospital)") # Mensaje para campañas sin beneficiario
                
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
        st.info("ℹ️ No hay campañas de donación compatibles con tu tipo de sangre en este momento, o no hay campañas activas aprobadas.")


def donante_hospitales():
    st.markdown("## Hospitales Asociados 🏥")
    st.markdown("---")
    st.info("Aquí encontrarás la información de contacto de los hospitales asociados para tus donaciones.")
    
    hospitales = obtener_hospitales()

    if OPENCAGE_API_KEY is None:
        st.warning("⚠️ La clave API de OpenCage Geocoding no está configurada. El mapa no mostrará ubicaciones reales.")
        st.info("Por favor, configura la variable de entorno `OPENCAGE_API_KEY` con tu clave de API de OpenCage.")
    
    if hospitales:
        # Coordenadas aproximadas de Buenos Aires para centrar el mapa si no hay hospitales o falla la geocodificación
        map_center_lat, map_center_lon = -34.6037, -58.3816
        has_geocoded_hospital = False

        m = folium.Map(location=[map_center_lat, map_center_lon], zoom_start=12)

        for hospital in hospitales:
            nombre = hospital.get('nombre_hospital', 'Nombre no disponible')
            direccion = hospital.get('direccion', 'Dirección no disponible')
            telefono = hospital.get('telefono', 'Teléfono no disponible')

            lat, lon = geocode_address(direccion) # Obtener coordenadas reales
            
            if lat is not None and lon is not None:
                has_geocoded_hospital = True
                tooltip_text = f"<b>{nombre}</b><br>Dirección: {direccion}<br>Teléfono: {telefono}"
                folium.Marker(
                    [lat, lon],
                    tooltip=tooltip_text,
                    popup=folium.Popup(tooltip_text, max_width=300), # Pop-up al hacer clic
                    icon=folium.Icon(color="red", icon="hospital", prefix='fa') # Icono de hospital
                ).add_to(m)
            else:
                st.warning(f"⚠️ No se pudo geocodificar la dirección para el hospital: {nombre} ({direccion}).")

        # Ajustar el centro del mapa si se geocodificó al menos un hospital
        if has_geocoded_hospital:
            # Podrías calcular el centroide de los hospitales geocodificados aquí
            # Por ahora, se mantiene el centro por defecto de Buenos Aires si no se ajusta dinámicamente.
            pass


        # Mostrar el mapa
        st_folium(m, width=700, height=500) # Ajusta width y height según necesidad

        
        st.write("También puedes contactar a los siguientes hospitales directamente:")
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
    
    # Columnas para centrar la imagen
    col_left, col_center, col_right = st.columns([1, 3, 1]) # Proporciones para centrar
    with col_center:
        st.image("foto.png", caption="El proceso de donación de sangre", width=300) 
    
    st.write("---") # Separador visual

    with st.expander("Haz clic para ver los requisitos detallados 👇"):
        st.markdown("""
        * **Edad:** Debes tener entre **18 y 65 años**. (Algunas excepciones pueden aplicar, consulta con el personal médico).
        * **Peso:** Tu peso corporal debe ser de al menos **50 kg**.
        * **Salud General:** Es fundamental que te sientas **bien de salud** en el momento de la donación y no presentar síntomas de enfermedad.
        * **Nivel de Hemoglobina:** Se realizará una prueba para asegurar que tu nivel de **hemoglobina** sea el adecuado para donar.
        * **Tiempo entre Donaciones:** Si ya donaste, debes esperar un **período mínimo** establecido antes de volver a donar (generalmente 3 o 4 meses, dependiendo del sexo y tipo de donación).
        * **Tatuajes y Piercings:** Si tienes **tatuajes o piercings recientes**, es necesario que haya transcurrido un período de espera (usualmente entre 6 y 12 meses) antes de poder donar.
        * **Medicaciones y Antecedentes:** Es importante informar sobre cualquier **medicación actual** o **antecedentes médicos relevantes** (ej. cirugías, enfermedades crónicas, alergias). El personal médico evaluará tu situación.
        """)
    
    st.info("⚠️ Esta es una lista general de los requisitos más comunes. **Siempre es crucial consultar los criterios específicos** del centro de donación de sangre al que asistas, ya que pueden variar ligeramente.")
    st.markdown("---")


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
