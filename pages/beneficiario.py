import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import time

# Carga las variables de entorno para Supabase (esto es redundante si main.py ya lo hace, pero asegura que funcione si se accede directamente a la página por alguna razón)
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase en beneficiario.py: {e}")
else:
    st.error("SUPABASE_URL o SUPABASE_KEY no están configuradas en .env. No se puede conectar a la base de datos.")


def beneficiario_perfil():
    st.title("👤 Mi Perfil de Beneficiario")
    st.markdown("---")

    # Asegurarse de que el usuario esté logueado como beneficiario
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Beneficiario':
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        st.stop() # Detiene la ejecución de la página

    user_db_id = st.session_state['user_db_id']
    user_email = st.session_state['user_email']

    if not user_db_id:
        st.error("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    st.header("Datos de mi Perfil")

    try:
        # Obtener los datos del beneficiario de Supabase
        response = supabase_client.table("beneficiario").select("*").eq("id_beneficiario", user_db_id).limit(1).execute()

        if response.data:
            beneficiario_data = response.data[0]
            st.write(f"**Nombre:** {beneficiario_data.get('nombre', 'N/A')}")
            st.write(f"**Email:** {beneficiario_data.get('mail', 'N/A')}")
            st.write(f"**Teléfono:** {beneficiario_data.get('telefono', 'N/A')}")
            st.write(f"**Dirección:** {beneficiario_data.get('direccion', 'N/A')}")
            st.write(f"**Tipo de Sangre (Requerido):** {beneficiario_data.get('tipo_de_sangre', 'N/A')}")
            # Puedes añadir más campos si los tienes en tu tabla de beneficiario
        else:
            st.error("No se pudieron cargar los datos de tu perfil. Intenta nuevamente.")
            return

    except Exception as e:
        st.error(f"Error al cargar los datos del perfil: {e}")
        st.exception(e)
        return

    st.markdown("---")
    st.header("💉 Crear Nueva Campaña de Donación")

    # Formulario para crear una nueva campaña
    with st.form("nueva_campana_form", clear_on_submit=True):
        st.markdown("Completa los siguientes datos para solicitar una donación de sangre.")

        # Puedes pre-llenar el tipo de sangre con el del beneficiario
        tipo_sangre_requerido = beneficiario_data.get('tipo_de_sangre', "O+")
        
        # Obtener la fecha actual para el campo 'fecha_limite'
        from datetime import date
        today = date.today()

        fecha_limite = st.date_input("🗓️ Fecha Límite para la Donación", min_value=today, value=today, help="Fecha hasta la cual necesitas la donación.")
        
        descripcion = st.text_area("📝 Descripción de la Campaña", 
                                   help="Ej: 'Se necesita sangre para operación de emergencia', 'Para paciente con anemia crónica'.")
        
        # El tipo de sangre ya está asociado al beneficiario, pero se puede mostrar como referencia.
        st.text_input("Tipo de Sangre Requerido (automático)", value=tipo_sangre_requerido, disabled=True, help="Este campo se pre-llena con tu tipo de sangre.")
        
        submit_button = st.form_submit_button("Crear Campaña")

        if submit_button:
            if not descripcion:
                st.error("Por favor, ingresa una descripción para la campaña.")
            else:
                try:
                    # Datos para insertar en la tabla 'solicitudes_sangre'
                    data_to_insert = {
                        "fecha_limite": str(fecha_limite), # Convertir a string para Supabase
                        "descripcion": descripcion,
                        "id_beneficiario": user_db_id, # El ID del beneficiario logueado
                        "tipo_de_sangre_requerido": tipo_sangre_requerido,
                        "estado": "Activa" # Estado inicial de la campaña
                    }

                    insert_response = supabase_client.table("solicitudes_sangre").insert(data_to_insert).execute()

                    if insert_response.data:
                        st.success("¡Campaña de donación creada exitosamente! Podrás verla en tus campañas activas.")
                        st.balloons()
                        # Opcional: recargar la página o redirigir
                        time.sleep(1)
                        st.experimental_rerun() # Esto recarga la página para mostrar cualquier cambio

                    else:
                        st.error(f"Error al crear la campaña: {insert_response.status_code} - {insert_response.data}")
                        st.warning("Detalles técnicos: " + str(insert_response.data)) # Para depuración
                        
                except Exception as e:
                    st.error(f"Error al conectar con Supabase para crear campaña. Detalles técnicos: {e}")
                    st.exception(e)
                    if "connection refused" in str(e).lower():
                        st.warning("Supabase no está conectado. ¿Están correctas tus credenciales o el servicio está en línea?")

# Si estás usando el mecanismo de "pages/" de Streamlit, no necesitas llamar a la función directamente aquí.
# Streamlit la llamará cuando se navegue a esta página.
# Pero si por alguna razón necesitas un punto de entrada explícito, puedes añadir:
if __name__ == "__main__":
    beneficiario_perfil()