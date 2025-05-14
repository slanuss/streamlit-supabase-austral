import streamlit as st
from pages.donante1 import donante_page

# Inicializar el estado de la sesión para la página actual
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "inicio"

def set_page(page_name):
    st.session_state["current_page"] = page_name

if st.session_state["current_page"] == "inicio":
    # Check if the user is already logged in
    if not st.session_state.get("logged_in", False):
        # If not logged in, show the login form
        with st.form("login_form"):
            username = st.text_input("Username (any value)")
            password = st.text_input("Password (any value)", type="password")
            user_type = st.radio("¿Qué tipo de usuario eres?", ["Hospital", "Donante", "Beneficiario"])
            submitted = st.form_submit_button("Login")

            if submitted:
                if username and password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["user_type"] = user_type
                    st.success(f"Login exitoso como {user_type}!")
                    if user_type == "Donante":
                        set_page("donante")
                    elif user_type == "Hospital":
                        set_page("hospital")
                    elif user_type == "Beneficiario":
                        set_page("beneficiario")
                else:
                    st.error("Por favor, ingresa ambos usuario y contraseña.")
    else:
        # Si ya está logueado, redirige según el tipo de usuario almacenado
        if st.session_state["user_type"] == "Donante":
            set_page("donante")
        elif st.session_state["user_type"] == "Hospital":
            set_page("hospital")
        elif st.session_state["user_type"] == "Beneficiario":
            set_page("beneficiario")

elif st.session_state["current_page"] == "donante":
    donante_page()
elif st.session_state["current_page"] == "hospital":
    st.title("Página del Hospital")
    st.write("Contenido específico para hospitales.")
elif st.session_state["current_page"] == "beneficiario":
    st.title("Página del Beneficiario")
    st.write("Contenido específico para beneficiarios.")

# Logout functionality
if st.session_state.get("logged_in", False):
    if st.sidebar.button("Logout"):
        del st.session_state["logged_in"]
        if "username" in st.session_state:
            del st.session_state["username"]
        if "user_type" in st.session_state:
            del st.session_state["user_type"]
        set_page("inicio") # Volver a la página de inicio después del logout