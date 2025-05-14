
import streamlit as st

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="One Drop App- Login",
    page_icon="🩸",
    layout="centered" # "wide" or "centered"
)

# --- Main Application ---
st.title("One Drop")


import streamlit as st

# Función para redirigir a una página específica
def navigate_to_page(page):
    st.session_state["next_page"] = page
    st.rerun()

# Páginas
PAGES = {
    "Hospital": "hospital_page",
    "Donante": "donante_page",
    "Beneficiario": "beneficiario_page"
}

if "next_page" in st.session_state:
    if st.session_state["next_page"] == "hospital_page":
        # Aquí cargarías el contenido de la página del Hospital
        st.title("Página del Hospital")
        st.write("Contenido específico para hospitales.")
    elif st.session_state["next_page"] == "donante_page":
        # Aquí cargarías el contenido de la página del Donante
        st.title("Página del Donante")
        st.write("Contenido específico para donantes.")
    elif st.session_state["next_page"] == "beneficiario_page":
        # Aquí cargarías el contenido de la página del Beneficiario
        st.title("Página del Beneficiario")
        st.write("Contenido específico para beneficiarios.")
    del st.session_state["next_page"] # Limpiar el estado después de la redirección
else:
    # Check if the user is already logged in (using session state)
    if not st.session_state.get("logged_in", False):
        # If not logged in, show the login form and user type selection
        with st.form("login_form"):
            username = st.text_input("Username (any value)")
            password = st.text_input("Password (any value)", type="password")
            user_type = st.radio("¿Qué tipo de usuario eres?", ["Hospital", "Donante", "Beneficiario"])
            submitted = st.form_submit_button("Login")

            if submitted:
                # For this demo, any username/password is accepted
                if username and password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["user_type"] = user_type # Store user type
                    st.success(f"Login successful as {user_type}!")
                    navigate_to_page(PAGES[user_type]) # Redirigir según el tipo de usuario
                else:
                    st.error("Por favor, ingresa tanto el usuario como la contraseña.")
    else:
        # If logged in, show a welcome message and user type
        st.success(f"Bienvenido de nuevo, {st.session_state.get('username', 'Usuario')}!")
        st.info(f"Eres un: {st.session_state.get('user_type', 'Usuario')}")
        st.info("Navega usando la barra lateral izquierda para gestionar las diferentes secciones.")

        # Opcional: Botón de logout
        if st.button("Logout"):
            del st.session_state["logged_in"]
            if "username" in st.session_state:
                del st.session_state["username"]
            if "user_type" in st.session_state:
                del st.session_state["user_type"]
            st.rerun()

import streamlit as st
from pages.donante1 import donante_page # Importa la función donante_page desde el archivo

# Función para redirigir a una página específica
def navigate_to_page(page):
    st.session_state["next_page"] = page
    st.rerun()

# Páginas
PAGES = {
    "Hospital": "hospital_page",
    "Donante": "donante_page",
    "Beneficiario": "beneficiario_page"
}

if "next_page" in st.session_state:
    if st.session_state["next_page"] == "hospital_page":
        st.title("Página del Hospital")
        st.write("Contenido específico para hospitales.")
    elif st.session_state["next_page"] == "donante_page":
        donante_page() # Llama a la función importada para mostrar la página del donante
    elif st.session_state["next_page"] == "beneficiario_page":
        st.title("Página del Beneficiario")
        st.write("Contenido específico para beneficiarios.")
    del st.session_state["next_page"] # Limpiar el estado después de la redirección
else:
    # Check if the user is already logged in (using session state)
    if not st.session_state.get("logged_in", False):
        # If not logged in, show the login form and user type selection
        with st.form("login_form"):
            username = st.text_input("Username (any value)")
            password = st.text_input("Password (any value)", type="password")
            user_type = st.radio("¿Qué tipo de usuario eres?", ["Hospital", "Donante", "Beneficiario"])
            submitted = st.form_submit_button("Login")

            if submitted:
    # Para esta demo, cualquier usuario/contraseña es aceptada
                if username and password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["user_type"] = user_type # Guarda el tipo de usuario
                    st.success(f"Login exitoso como {user_type}!")
                if user_type == "Donante":
                    navigate_to_page("donante_page")
                elif user_type == "Hospital":
                    navigate_to_page("hospital_page")
                elif user_type == "Beneficiario":
                    navigate_to_page("beneficiario_page")
            else:
                st.error("Por favor, ingresa tanto el usuario como la contraseña.")
    else:
        # If logged in, show a welcome message and user type
        st.success(f"Bienvenido de nuevo, {st.session_state.get('username', 'Usuario')}!")
        st.info(f"Eres un: {st.session_state.get('user_type', 'Usuario')}")
        st.info("Navega usando la barra lateral izquierda para gestionar las diferentes secciones.")

        # Opcional: Botón de logout
        if st.button("Logout"):
            del st.session_state["logged_in"]
            if "username" in st.session_state:
                del st.session_state["username"]
            if "user_type" in st.session_state:
                del st.session_state["user_type"]
            st.rerun()