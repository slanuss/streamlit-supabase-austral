import streamlit as st
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Importar las páginas de los roles
import pages.donante1 as donante_page # Asegúrate de que este archivo exista en 'pages'
# import pages.beneficiario as beneficiario_page # Si tienes una página de beneficiario, descomenta
import pages.hospital as hospital_page # <-- ¡NUEVO! Importa la página del hospital

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Plataforma de Donación de Sangre",
    page_icon="🩸",
    layout="centered",
    initial_sidebar_state="auto"
)

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, confíguralas para que la conexión a la base de datos funcione.")
    supabase_client: Client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
        supabase_client: Client = None

# --- Funciones de autenticación ---
def verificar_credenciales_desde_db(email, password, user_type):
    """
    Verifica las credenciales de usuario contra tus tablas 'donante', 'beneficiario' o 'hospital' en Supabase.
    Asume una contraseña simple "123" para el ejemplo.
    ADVERTENCIA: ESTO NO ES SEGURO PARA PRODUCCIÓN. LAS CONTRASEÑAS DEBEN ESTAR HASEADAS.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede verificar credenciales.")
        return False, None, None

    tabla = None
    columna_email = "mail" 
    
    if user_type == "Donante":
        tabla = "donante"
        id_columna_db = "ID_Donante" 
    elif user_type == "Beneficiario":
        tabla = "beneficiario"
        id_columna_db = "ID_Beneficiario" 
    elif user_type == "Hospital": # <-- ¡NUEVO!
        tabla = "hospital"
        id_columna_db = "ID_Hospital" # Asegúrate de que esta columna exista en tu tabla 'hospital'
    else:
        st.error("Tipo de usuario no válido.")
        return False, None, None

    try:
        response = supabase_client.table(tabla).select("*").eq(columna_email, email).limit(1).execute()
        
        if response.data:
            usuario_db = response.data[0]
            
            # --- SIMULACIÓN DE CONTRASEÑA DE PRUEBA ---
            if password == "123":
                user_db_id = usuario_db.get(id_columna_db)
                if user_db_id is None:
                    st.warning(f"No se encontró la columna de ID '{id_columna_db}' en la tabla '{tabla}' para el usuario {email}. La aplicación podría no funcionar correctamente para funcionalidades que requieran el ID.")
                return True, email, user_db_id
            else:
                st.warning("Contraseña incorrecta. La contraseña de prueba es '123'.")
                return False, None, None
        else:
            st.error(f"El email '{email}' no se encontró en la tabla de {user_type}.")
            return False, None, None
    except Exception as e:
        st.error(f"Error al verificar credenciales en Supabase: {e}")
        return False, None, None


# --- Inicializa el estado de la sesión ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_db_id' not in st.session_state:
    st.session_state['user_db_id'] = None


# --- Lógica principal de la aplicación ---
if st.session_state['logged_in']:
    # Contenido para usuarios logueados
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({'logged_in': False, 'user_type': None, 'user_email': None, 'user_db_id': None}))
    st.sidebar.success(f"Sesión iniciada como: **{st.session_state['user_type']}**")
    
    st.markdown(f"<h1 style='text-align: center; color: #B22222;'>¡Bienvenido, {st.session_state['user_email']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Tu aporte es vital para salvar vidas.</p>", unsafe_allow_html=True)
    
    # Esto ya no muestra la "Bienvenida" estática, sino que carga la página específica del rol.
    # st.write("---")
    # st.info("Utiliza el menú de la izquierda para navegar a tu perfil y gestionar tu información.")
    # st.markdown("<h3 style='color: #4682B4;'>Juntos, hacemos la diferencia.</h3>", unsafe_allow_html=True)

    # --- Redirección a la página específica del rol ---
    if st.session_state['user_type'] == 'Donante':
        donante_page.donante_perfil() # Carga la función principal de la página del donante
    elif st.session_state['user_type'] == 'Beneficiario':
        # Asegúrate de tener un archivo 'pages/beneficiario.py' con una función 'beneficiario_perfil()'
        # beneficiario_page.beneficiario_perfil() 
        st.info("Funcionalidad para Beneficiarios en desarrollo. ¡Bienvenido!")
    elif st.session_state['user_type'] == 'Hospital': # <-- ¡NUEVO!
        hospital_page.hospital_perfil() # Carga la función principal de la página del hospital
    else:
        st.error("Tipo de usuario no reconocido. Por favor, contacta al soporte.")


else: # Si el usuario NO está logueado, muestra el formulario de inicio de sesión
    st.markdown("<h1 style='text-align: center; color: #B22222;'>🩸 Salva Vidas, Dona Sangre 🩸</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #333333;'>Una comunidad unida por la vida. Inicia sesión para ser parte.</p>", unsafe_allow_html=True)
    
    st.write("---")

    col1, col2, col3 = st.columns([1,2,1]) 

    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Inicia Sesión Aquí")
            email = st.text_input("📧 Email de Usuario", help="Debe ser un email existente en tu tabla de Donante/Beneficiario/Hospital en Supabase.") 
            password = st.text_input("🔒 Contraseña", type="password", help="La contraseña de prueba es '123'.")
            user_type = st.selectbox("👤 Tipo de Usuario", ["Donante", "Beneficiario", "Hospital"]) # <-- "Hospital" añadido
            
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
                else:
                    st.error("Inicio de sesión fallido. Revisa el email y la contraseña de prueba ('123').")

    st.write("---")
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #888888;'>¿Eres nuevo? Explora la aplicación para ver cómo puedes ayudar.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: #BBBBBB;'>Recordatorio: Para un entorno real y seguro, considera usar Supabase Auth o implementar un hashing de contraseñas robusto.</p>", unsafe_allow_html=True)