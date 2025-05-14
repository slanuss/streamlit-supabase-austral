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

if __name__ == "__main__":
    donante_page()