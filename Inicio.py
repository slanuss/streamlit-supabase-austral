import streamlit as st
from pages.donante1 import donante_page

# Inicializar el estado de la sesión para la página actual
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None

if not st.session_state["logged_in"]:
    # Mostrar el formulario de login
    with st.form("login_form"):
        username = st.text_input("Usuario (cualquier valor)")
        password = st.text_input("Contraseña (cualquier valor)", type="password")
        user_type = st.radio("¿Qué tipo de usuario eres?", ["Hospital", "Donante", "Beneficiario"])
        submitted = st.form_submit_button("Ingresar")

        if submitted:
            # Simulación de login exitoso
            if username and password:
                st.session_state["logged_in"] = True
                st.session_state["user_type"] = user_type
                st.success(f"Ingreso exitoso como {user_type}!")
                st.rerun() # Fuerza la recarga para mostrar la página correspondiente
            else:
                st.error("Por favor, ingresa usuario y contraseña.")
else:
    # Redirigir basado en el tipo de usuario logueado
    if st.session_state["user_type"] == "Donante":
        donante_page()
    elif st.session_state["user_type"] == "Hospital":
        st.title("Página del Hospital")
        st.write("Contenido específico para hospitales.")
    elif st.session_state["user_type"] == "Beneficiario":
        st.title("Página del Beneficiario")
        st.write("Contenido específico para beneficiarios.")

    # Botón de Logout (si el usuario está logueado)
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.session_state["user_type"] = None
        st.rerun()