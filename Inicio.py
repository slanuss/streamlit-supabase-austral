import streamlit as st
from pages.donante1 import donante_page
from pages.pag1 import hospital_page  # <-- Importa la función hospital_page aquí

# Inicializar el estado de la sesión
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Inicio"

def set_page(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

if st.session_state["current_page"] == "Inicio":
    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            username = st.text_input("Usuario (cualquier valor)")
            password = st.text_input("Contraseña (cualquier valor)", type="password")
            user_type = st.radio("¿Qué tipo de usuario eres?", ["Hospital", "Donante", "Beneficiario"])
            submitted = st.form_submit_button("Ingresar")

            if submitted:
                if username and password:
                    st.session_state["logged_in"] = True
                    st.session_state["user_type"] = user_type
                    st.success(f"Ingreso exitoso como {user_type}!")
                    if user_type == "Donante":
                        set_page("donante1")  # Cambia la página actual a "donante1"
                    elif user_type == "Hospital":
                        set_page("pag1")  # Cambia la página a "pag1" para hospitales
                    elif user_type == "Beneficiario":
                        set_page("pag2")  # Cambia la página a "pag2" para beneficiarios
                else:
                    st.error("Por favor, ingresa usuario y contraseña.")
    else:
        # Si ya está logueado, redirige directamente
        if st.session_state["user_type"] == "Donante":
            set_page("donante1")
        elif st.session_state["user_type"] == "Hospital":
            set_page("pag1")
        elif st.session_state["user_type"] == "Beneficiario":
            set_page("pag2")

elif st.session_state["current_page"] == "donante1":
    donante_page()
elif st.session_state["current_page"] == "pag1":
    hospital_page()  # <-- Aquí se llama la función que muestra la página del hospital con el formulario
elif st.session_state["current_page"] == "pag2":
    st.title("Página del Beneficiario")
    st.write("Contenido específico para beneficiarios.")

# Barra lateral de navegación (si el usuario está logueado)
if st.session_state["logged_in"]:
    st.sidebar.title("Navegación")
    menu = ["Inicio", "donante1", "pag1", "pag2"]
    current_selection = st.sidebar.radio("Selecciona una página", menu, index=menu.index(st.session_state["current_page"]))

    if current_selection != st.session_state["current_page"]:
        set_page(current_selection)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.session_state["user_type"] = None
        st.session_state["current_page"] = "Inicio"
        st.rerun()
