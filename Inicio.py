import streamlit as st
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="One Drop - Plataforma de Donación de Sangre", # Cambiado el título de la pestaña del navegador
    page_icon="�",
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

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
    /* Paleta de colores */
    :root {
        --primary-red: #E05A47; /* Rojo suave */
        --light-red: #F28C7D; /* Rojo más claro para acentos */
        --white: #FFFFFF;
        --light-grey: #F8F9FA; /* Fondo muy claro */
        --dark-grey-text: #333333; /* Color de texto principal */
        --medium-grey: #6c757d; /* Color de texto secundario */
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

    /* Centra la imagen y limita su ancho para el logo */
    .stImage {
        display: block; /* Asegura que la imagen sea un bloque */
        margin-left: auto; /* Centra horizontalmente */
        margin-right: auto; /* Centra horizontalmente */
        max-width: 150px; /* Limita el ancho máximo del logo */
    }

</style>
""", unsafe_allow_html=True)


# --- Funciones de autenticación y registro ---
def verificar_credenciales_desde_db(email, password, user_type):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede verificar credenciales.")
        return False, None, None

    tabla = None
    id_columna_db = None

    if user_type == "Donante":
        tabla = "donante"
        id_columna_db = "id_donante"
    elif user_type == "Beneficiario":
        tabla = "beneficiario"
        id_columna_db = "id_beneficiario"
    elif user_type == "Hospital":
        tabla = "hospital"
        id_columna_db = "id_hospital"
    else:
        st.error("Tipo de usuario no válido.")
        return False, None, None

    try:
        response = supabase_client.table(tabla).select(f"*, contrafija, {id_columna_db}").eq("mail", email).limit(1).execute()
        
        if response.data:
            usuario_db = response.data[0]
            
            if usuario_db.get("contrafija") == password:
                user_db_id = usuario_db.get(id_columna_db)
                if user_db_id is None:
                    st.warning(f"No se encontró la columna de ID '{id_columna_db}' en la tabla '{tabla}' para el usuario {email}. La aplicación podría no funcionar correctamente para funcionalidades que requieran el ID. Verifica tu esquema de base de datos.")
                    return False, None, None
                return True, email, user_db_id
            else:
                st.warning("Contraseña incorrecta. Por favor, verifica tu contraseña.")
                return False, None, None
        else:
            st.error(f"El email '{email}' no se encontró en la tabla de {user_type}.")
            return False, None, None
    except Exception as e:
        st.error(f"Error al verificar credenciales en Supabase: {e}")
        st.exception(e)
        return False, None, None

def registrar_donante_en_db(nombre, dni, mail, telefono, direccion, tipo_sangre, edad, sexo, antecedentes, medicaciones, contrafija):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede registrar.")
        return False
    try:
        existing_dni = supabase_client.table("donante").select("dni").eq("dni", dni).execute()
        if existing_dni.data and len(existing_dni.data) > 0:
            st.error("El DNI ya está registrado. Por favor, **inicia sesión** si ya tienes una cuenta, o verifica tus datos.")
            return False
        existing_mail = supabase_client.table("donante").select("mail").eq("mail", mail).execute()
        if existing_mail.data and len(existing_mail.data) > 0:
            st.error("El email ya está registrado. Por favor, **inicia sesión** si ya tienes una cuenta, o verifica tus datos.")
            return False
        data = {
            "nombred": nombre,
            "dni": dni,
            "mail": mail,
            "telefono": telefono,
            "direccion": direccion,
            "tipo_de_sangre": tipo_sangre,
            "edad": edad,
            "sexo": sexo,
            "antecedentes": antecedentes,
            "medicaciones": medicaciones,
            "contrafija": contrafija,
            "cumple_requisitos": False
        }
        response = supabase_client.table("donante").insert(data).execute()
        if response.data:
            st.success("¡Registro de donante exitoso! Ahora puedes iniciar sesión.")
            return True
        else:
            st.error(f"Error al registrar donante: {response.status_code} - {response.data}")
            st.warning("Detalles técnicos del error: " + str(response.error)) 
            return False
    except Exception as e:
        st.error(f"Error al registrar donante en Supabase: {e}")
        st.exception(e)
        return False

def registrar_beneficiario_en_db(nombre, mail, telefono, direccion, tipo_sangre, contrafija):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede registrar.")
        return False
    try:
        existing_mail = supabase_client.table("beneficiario").select("mail").eq("mail", mail).execute()
        if existing_mail.data and len(existing_mail.data) > 0:
            st.error("El email ya está registrado. Por favor, **inicia sesión** si ya tienes una cuenta, o verifica tus datos.")
            return False
        data = {
            "nombreb": nombre,
            "mail": mail, "telefono": telefono,
            "direccion": direccion, "tipo_de_sangre": tipo_sangre,
            "contrafija": contrafija
        }
        response = supabase_client.table("beneficiario").insert(data).execute()
        if response.data:
            st.success("¡Registro de beneficiario exitoso! Ahora puedes iniciar sesión.")
            return True
        else:
            st.error(f"Error al registrar beneficiario: {response.status_code} - {response.data}")
            st.warning("Detalles técnicos del error: " + str(response.error))
            return False
    except Exception as e:
        st.error(f"Error al registrar beneficiario en Supabase: {e}")
        st.exception(e)
        return False

def registrar_hospital_en_db(nombre_hospital, direccion, telefono, mail, contrafija):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede registrar.")
        return False
    try:
        existing_mail = supabase_client.table("hospital").select("mail").eq("mail", mail).execute()
        if existing_mail.data and len(existing_mail.data) > 0:
            st.error("El email ya está registrado para un hospital. Por favor, **inicia sesión** si ya tienes una cuenta, o verifica tus datos.")
            return False
        existing_name = supabase_client.table("hospital").select("nombre_hospital").eq("nombre_hospital", nombre_hospital).execute()
        if existing_name.data and len(existing_name.data) > 0:
            st.error("Ya existe un hospital registrado con ese nombre. Por favor, verifica tus datos.")
            return False
        data = {
            "nombre_hospital": nombre_hospital, "direccion": direccion,
            "telefono": telefono, "mail": mail, "contrafija": contrafija
        }
        response = supabase_client.table("hospital").insert(data).execute()
        if response.data:
            st.success("¡Registro de hospital exitoso! Ahora puedes iniciar sesión.")
            return True
        else:
            st.error(f"Error al registrar hospital: {response.status_code} - {response.data}")
            st.warning("Detalles técnicos del error: " + str(response.error))
            return False
    except Exception as e:
        st.error(f"Error al registrar hospital en Supabase: {e}")
        st.exception(e)
        return False

# --- Inicializa el estado de la sesión ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_db_id' not in st.session_state:
    st.session_state['user_db_id'] = None
if 'show_register_form' not in st.session_state:
    st.session_state['show_register_form'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'

# --- Lógica principal de la aplicación ---
if st.session_state['logged_in']:
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None, 'show_register_form': False, 'current_page': 'home'}))
    st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")
    
    # Título de bienvenida con el nuevo color
    st.markdown(f"<h1 style='color: var(--primary-red);'>¡Bienvenido, {st.session_state['user_email']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: var(--dark-grey-text);'>Selecciona una opción del menú lateral.</p>", unsafe_allow_html=True)

else: # Si el usuario NO está logueado (mostrar login/registro)
    
    # Contenedor para centrar el logo y el nombre de la app
    logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
    with logo_col2:
        # Ruta al archivo de imagen de tu logo
        # ¡IMPORTANTE! Asegúrate de que el archivo 'logo.png' esté en la misma carpeta que tu script de Streamlit ('Inicio.py').
        # Si no lo está, deberás especificar la ruta completa o la ruta relativa correcta, por ejemplo:
        # st.image("./imagenes/logo.png", ...) si está en una subcarpeta 'imagenes'.
        st.image("logo.png", use_container_width=True) # Se usa use_container_width para que se adapte al ancho de la columna
        # st.markdown("<h1 style='color: var(--primary-red);'>ONE DROP</h1>", unsafe_allow_html=True) # Eliminado el título "ONE DROP" duplicado
        st.markdown("<p style='text-align: center; font-size: 1.2em; color: var(--medium-grey);'>Salva Vidas, Dona Sangre. Una comunidad unida por la vida.</p>", unsafe_allow_html=True)
    
    st.write("---")

    col1, col2, col3 = st.columns([1,2,1]) 

    with col2:
        if not st.session_state['show_register_form']:
            with st.form("login_form", clear_on_submit=False):
                st.subheader("Inicia Sesión Aquí")
                email = st.text_input("📧 Email de Usuario", help="Debe ser un email existente en tu tabla de Donante/Beneficiario/Hospital en Supabase.")
                password = st.text_input("🔒 Contraseña", type="password", help="Usa la 'contrafija' de tu tabla de usuario (ej. 'hosp1' para hospital1@email.com).")
                
                user_type = st.radio("👤 Tipo de Usuario", ["Donante", "Beneficiario", "Hospital"], index=0)
                
                st.write("")
                login_button = st.form_submit_button("Ingresar")

                if login_button:
                    login_exitoso, user_email_logueado, user_db_id = verificar_credenciales_desde_db(email, password, user_type)
                    
                    if login_exitoso:
                        st.session_state['logged_in'] = True
                        st.session_state['user_type'] = user_type
                        st.session_state['user_email'] = user_email_logueado
                        st.session_state['user_db_id'] = user_db_id
                        st.success(f"¡Bienvenido, {user_email_logueado}! Sesión iniciada como {user_type}.")
                        time.sleep(1)
                        st.rerun()

            st.markdown("---")
            if st.button("¿No tenés cuenta? ¡Registrate!"):
                st.session_state['show_register_form'] = True
                st.rerun()

        else: # Formulario de registro
            st.subheader("Crea tu Cuenta Nueva")
            register_user_type = st.radio("👤 ¿Qué tipo de cuenta deseas crear?", ["Donante", "Beneficiario", "Hospital"], index=0, key="reg_user_type_radio")
            
            with st.form("register_form", clear_on_submit=True):
                new_email = st.text_input("📧 Email", key="reg_email", help="Tu email será tu identificador principal.")
                new_password = st.text_input("🔒 Contraseña", type="password", key="reg_password")
                confirm_password = st.text_input("🔄 Confirma Contraseña", type="password", key="reg_confirm_password")

                if register_user_type == "Donante":
                    st.write("---")
                    st.markdown("##### Datos del Donante")
                    new_nombre = st.text_input("Nombre", key="don_nombre")
                    new_dni = st.text_input("DNI", key="don_dni")
                    new_telefono = st.text_input("Teléfono", key="don_telefono")
                    new_direccion = st.text_input("Dirección", key="don_direccion")
                    
                    new_edad = st.number_input("Edad", min_value=18, max_value=99, key="don_edad", help="Debes tener al menos 18 años para ser donante.")
                    new_sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], key="don_sexo")
                    new_antecedentes = st.text_area("Antecedentes Médicos (opcional)", help="Ej: 'Alergia al polen', 'Hipertensión leve'", key="don_antecedentes")
                    new_medicaciones = st.text_area("Medicaciones Actuales (opcional)", help="Ej: 'Antihistamínicos', 'Losartan'", key="don_medicaciones")

                    tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                    new_tipo_sangre = st.selectbox("Tipo de Sangre", tipos_sangre, key="don_tipo_sangre")

                    register_button = st.form_submit_button("Registrar Donante")
                    if register_button:
                        if new_password != confirm_password:
                            st.error("Las contraseñas no coinciden.")
                        elif not all([new_nombre, new_dni, new_email, new_telefono, new_direccion, new_tipo_sangre, new_edad, new_sexo, new_password]):
                            st.error("Por favor, completa todos los campos obligatorios (Nombre, DNI, Email, Teléfono, Dirección, Tipo de Sangre, Edad, Sexo, Contraseña).")
                        else:
                            if registrar_donante_en_db(new_nombre, new_dni, new_email, new_telefono, new_direccion, new_tipo_sangre, new_edad, new_sexo, new_antecedentes, new_medicaciones, new_password):
                                st.session_state['show_register_form'] = False
                                time.sleep(1)
                                st.rerun()

                elif register_user_type == "Beneficiario":
                    st.write("---")
                    st.markdown("##### Datos del Beneficiario")
                    new_nombre_beneficiario = st.text_input("Nombre", key="ben_nombre")
                    new_telefono_beneficiario = st.text_input("Teléfono", key="ben_telefono")
                    new_direccion_beneficiario = st.text_input("Dirección", key="ben_direccion")
                    
                    tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                    new_tipo_sangre_beneficiario = st.selectbox("Tipo de Sangre Requerido", tipos_sangre, key="ben_tipo_sangre")

                    register_button = st.form_submit_button("Registrar Beneficiario")
                    if register_button:
                        if new_password != confirm_password:
                            st.error("Las contraseñas no coinciden.")
                        elif not all([new_nombre_beneficiario, new_email, new_telefono_beneficiario, new_direccion_beneficiario, new_tipo_sangre_beneficiario, new_password]):
                            st.error("Por favor, completa todos los campos obligatorios para el beneficiario.")
                        else:
                            if registrar_beneficiario_en_db(new_nombre_beneficiario, new_email, new_telefono_beneficiario, new_direccion_beneficiario, new_tipo_sangre_beneficiario, new_password):
                                st.session_state['show_register_form'] = False
                                time.sleep(1)
                                st.rerun()

                elif register_user_type == "Hospital":
                    st.write("---")
                    st.markdown("##### Datos del Hospital")
                    new_nombre_hospital = st.text_input("Nombre del Hospital", key="hosp_nombre")
                    new_direccion_hospital = st.text_input("Dirección del Hospital", key="hosp_direccion")
                    new_telefono_hospital = st.text_input("Teléfono del Hospital", key="hosp_telefono")

                    register_button = st.form_submit_button("Registrar Hospital")
                    if register_button:
                        if new_password != confirm_password:
                            st.error("Las contraseñas no coinciden.")
                        elif not all([new_nombre_hospital, new_direccion_hospital, new_telefono_hospital, new_email, new_password]):
                            st.error("Por favor, completa todos los campos.")
                        else:
                            if registrar_hospital_en_db(new_nombre_hospital, new_direccion_hospital, new_telefono_hospital, new_email, new_password):
                                st.session_state['show_register_form'] = False
                                time.sleep(1)
                                st.rerun()
            
            st.markdown("---")
            if st.button("Volver al Inicio de Sesión"):
                st.session_state['show_register_form'] = False
                st.rerun()

    st.write("---")
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: var(--medium-grey);'>¿Eres nuevo? Explora la aplicación para ver cómo puedes ayudar.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: var(--medium-grey);'>Recordatorio: Para un entorno real y seguro, considera usar Supabase Auth o implementar un hashing de contraseñas robusto.</p>", unsafe_allow_html=True)
