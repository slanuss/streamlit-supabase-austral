import streamlit as st
from pages.donante1 import donante_page # Importa la función donante_page

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
        donante_page() # Llama a la función para mostrar la página del donante
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
                    navigate_to_page(PAGES[user_type]) # Redirige a la página del usuario
                else:
                    st.error("Por favor, ingresa tanto el usuario como la contraseña.")
    else:
        # Si ya está logueado, redirige directamente según el tipo de usuario
        if st.session_state["user_type"] == "Donante":
            navigate_to_page("donante_page")
        elif st.session_state["user_type"] == "Hospital":
            navigate_to_page("hospital_page")
        elif st.session_state["user_type"] == "Beneficiario":
            navigate_to_page("beneficiario_page")