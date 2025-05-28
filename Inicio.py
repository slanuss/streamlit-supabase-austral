import streamlit as st
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Ya no necesitamos importar las páginas directamente aquí si el mecanismo de multipágina
# de Streamlit se encarga de ello. Si las mantienes, solo se usarán si las llamas explícitamente.
# Para la estructura de "pages/" no es necesario.
# import pages.donante1 as donante_page
# import pages.beneficiario as beneficiario_page
# import pages.hospital as hospital_page

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Plataforma de Donación de Sangre",
    page_icon="🩸",
    layout="centered", # O "wide" si prefieres más espacio
    initial_sidebar_state="auto" # Esto hace que Streamlit detecte automáticamente los archivos en 'pages/'
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

# --- Funciones de autenticación y registro (SE MANTIENEN IGUAL) ---
def verificar_credenciales_desde_db(email, password, user_type):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede verificar credenciales.")
        return False, None, None

    tabla = None
    id_columna_db = None

    if user_type == "Donante":
        tabla = "donante"
        id_columna_db = "ID_Donante" 
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
        # Aquí también seleccionamos el ID para asegurarnos de que lo obtenemos
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
        if existing_dni.data:
            st.error("El DNI ya está registrado. Por favor, verifica tus datos o inicia sesión.")
            return False
        existing_mail = supabase_client.table("donante").select("mail").eq("mail", mail).execute()
        if existing_mail.data:
            st.error("El email ya está registrado. Por favor, verifica tus datos o inicia sesión.")
            return False
        data = {
            "nombre": nombre, "dni": dni, "mail": mail, "telefono": telefono,
            "direccion": direccion, "tipo_de_sangre": tipo_sangre,
            "edad": edad, "sexo": sexo, "antecedentes": antecedentes,
            "medicaciones": medicaciones, "contrafija": contrafija
        }
        response = supabase_client.table("donante").insert(data).execute()
        if response.data:
            st.success("¡Registro de donante exitoso! Ahora puedes iniciar sesión.")
            return True
        else:
            st.error(f"Error al registrar donante: {response.status_code} - {response.data}")
            return False
    except Exception as e:
        st.error(f"Error al registrar donante en Supabase: {e}")
        return False

def registrar_beneficiario_en_db(nombre, mail, telefono, direccion, tipo_sangre, contrafija):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede registrar.")
        return False
    try:
        existing_mail = supabase_client.table("beneficiario").select("mail").eq("mail", mail).execute()
        if existing_mail.data:
            st.error("El email ya está registrado. Por favor, verifica tus datos o inicia sesión.")
            return False
        data = {
            "nombre": nombre, "mail": mail, "telefono": telefono,
            "direccion": direccion, "tipo_de_sangre": tipo_sangre,
            "contrafija": contrafija
        }
        response = supabase_client.table("beneficiario").insert(data).execute()
        if response.data:
            st.success("¡Registro de beneficiario exitoso! Ahora puedes iniciar sesión.")
            return True
        else:
            st.error(f"Error al registrar beneficiario: {response.status_code} - {response.data}")
            return False
    except Exception as e:
        st.error(f"Error al registrar beneficiario en Supabase: {e}")
        return False

def registrar_hospital_en_db(nombre_hospital, direccion, telefono, mail, contrafija):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede registrar.")
        return False
    try:
        existing_mail = supabase_client.table("hospital").select("mail").eq("mail", mail).execute()
        if existing_mail.data:
            st.error("El email ya está registrado para un hospital. Por favor, verifica tus datos o inicia sesión.")
            return False
        existing_name = supabase_client.table("hospital").select("nombre_hospital").eq("nombre_hospital", nombre_hospital).execute()
        if existing_name.data:
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
            return False
    except Exception as e:
        st.error(f"Error al registrar hospital en Supabase: {e}")
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
# Nuevo: para controlar la página actual (si no usas la detección automática de pages/)
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home' # Página predeterminada


# --- Lógica principal de la aplicación ---
if st.session_state['logged_in']:
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None, 'show_register_form': False, 'current_page': 'home'}))
    st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")
    
    # Después de iniciar sesión, el main.py no debe renderizar el contenido de las páginas de los roles directamente.
    # Streamlit se encarga de eso a través del sidebar si los archivos están en la carpeta 'pages/'.
    # Puedes dejar un mensaje de bienvenida general aquí si quieres, o dejarlo vacío.
    st.markdown(f"<h1 style='text-align: center; color: #B22222;'>¡Bienvenido, {st.session_state['user_email']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Selecciona una opción del menú lateral.</p>", unsafe_allow_html=True)

    # Si tu estructura de páginas con st.sidebar no funciona por algún motivo,
    # y quieres un manejo explícito de páginas, DESCOMENTA LO SIGUIENTE y COMENTA lo de arriba:
    # if st.session_state['user_type'] == 'Donante':
    #     st.session_state['current_page'] = 'donante'
    # elif st.session_state['user_type'] == 'Beneficiario':
    #     st.session_state['current_page'] = 'beneficiario'
    # elif st.session_state['user_type'] == 'Hospital':
    #     st.session_state['current_page'] = 'hospital'
    # st.rerun() # Fuerza una recarga para ir a la página correcta

    # Si usas la detección automática de pages/, no necesitas las llamadas directas:
    # if st.session_state['user_type'] == 'Donante':
    #     donante_page.donante_perfil()
    # elif st.session_state['user_type'] == 'Beneficiario':
    #     beneficiario_page.beneficiario_perfil()
    # elif st.session_state['user_type'] == 'Hospital':
    #     hospital_page.hospital_perfil()
    # else:
    #     st.error("Tipo de usuario no reconocido. Por favor, contacta al soporte.")

else: # Si el usuario NO está logueado (mostrar login/registro)
    st.markdown("<h1 style='text-align: center; color: #B22222;'>🩸 Salva Vidas, Dona Sangre 🩸</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #333333;'>Una comunidad unida por la vida. Inicia sesión para ser parte.</p>", unsafe_allow_html=True)
    
    st.write("---")

    col1, col2, col3 = st.columns([1,2,1]) 

    with col2:
        if not st.session_state['show_register_form']:
            with st.form("login_form", clear_on_submit=False):
                st.subheader("Inicia Sesión Aquí")
                email = st.text_input("📧 Email de Usuario", help="Debe ser un email existente en tu tabla de Donante/Beneficiario/Hospital en Supabase.")
                password = st.text_input("🔒 Contraseña", type="password", help="Usa la 'contrafija' de tu tabla de usuario (ej. 'hosp1' para hospital1@email.com).")
                user_type = st.selectbox("👤 Tipo de Usuario", ["Donante", "Beneficiario", "Hospital"])
                
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
                        st.rerun() # Esto recarga la página, mostrando el contenido para usuarios logueados

            st.markdown("---")
            if st.button("¿No tenés cuenta? ¡Registrate!"):
                st.session_state['show_register_form'] = True
                st.rerun()

        else: # Formulario de registro
            st.subheader("Crea tu Cuenta Nueva")
            register_user_type = st.selectbox("👤 ¿Qué tipo de cuenta deseas crear?", ["Donante", "Beneficiario", "Hospital"])
            
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
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #888888;'>¿Eres nuevo? Explora la aplicación para ver cómo puedes ayudar.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: #BBBBBB;'>Recordatorio: Para un entorno real y seguro, considera usar Supabase Auth o implementar un hashing de contraseñas robusto.</p>", unsafe_allow_html=True)