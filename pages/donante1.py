import streamlit as st

def donante_perfil():
    st.header("Perfil del Donante")
    with st.form("perfil_form"):
        nombre_apellido = st.text_input("Nombre y Apellido")
        mail = st.text_input("Mail Personal")
        telefono = st.text_input("Teléfono")
        direccion = st.text_input("Dirección")
        edad = st.number_input("Edad", min_value=18, max_value=100, step=1)
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
        tipo_sangre = st.selectbox("Tipo de Sangre", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        antecedentes_medicos = st.text_area("Antecedentes Médicos (separados por coma o en líneas diferentes)")
        medicado = st.radio("¿Está actualmente medicado?", ["Sí", "No"])
        cumple_requisitos = st.checkbox("Declaro cumplir con los requisitos básicos para donar")
        guardar = st.form_submit_button("Guardar Perfil")

        if guardar:
            st.success("Perfil guardado exitosamente!")
            # Aquí podrías guardar los datos en una base de datos o similar
            st.write("Datos guardados:")
            st.write(f"Nombre y Apellido: {nombre_apellido}")
            st.write(f"Mail: {mail}")
            st.write(f"Teléfono: {telefono}")
            st.write(f"Dirección: {direccion}")
            st.write(f"Edad: {edad}")
            st.write(f"Sexo: {sexo}")
            st.write(f"Tipo de Sangre: {tipo_sangre}")
            st.write(f"Antecedentes Médicos: {antecedentes_medicos}")
            st.write(f"¿Medicado?: {medicado}")
            st.write(f"Cumple Requisitos: {'Sí' if cumple_requisitos else 'No'}")

def donante_campanas():
    st.header("Campañas de Donación Disponibles")
    st.info("Aquí se mostrarán las campañas de donación activas.")
    # Aquí iría la lógica para mostrar las campañas

def donante_hospitales():
    st.header("Hospitales")
    st.info("Aquí se mostrará la lista de hospitales asociados.")
    # Aquí iría la lógica para mostrar los hospitales

def donante_requisitos():
    st.header("Requisitos para Donar")
    st.info("Aquí se detallarán los requisitos necesarios para ser donante.")
    # Aquí iría la información sobre los requisitos

def donante_manual():
    st.header("Manual del Donante")
    st.info("Aquí se proporcionará un manual con información útil para los donantes.")
    # Aquí iría el contenido del manual

def donante_page():
    st.sidebar.title("Navegación Donante")
    menu = ["Perfil", "Campañas Disponibles", "Hospitales", "Requisitos", "Manual del Donante"]
    opcion = st.sidebar.selectbox("Selecciona una sección", menu)

    if opcion == "Perfil":
        donante_perfil()
    elif opcion == "Campañas Disponibles":
        donante_campanas()
    elif opcion == "Hospitales":
        donante_hospitales()
    elif opcion == "Requisitos":
        donante_requisitos()
    elif opcion == "Manual del Donante":
        donante_manual()

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
        donante_page() # Llamamos a la función que muestra la página del donante
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