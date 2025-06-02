import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import time
from datetime import date

# Carga las variables de entorno para Supabase
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


def perfil_beneficiario_tab():
    st.header("Datos de mi Perfil")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')
    user_email = st.session_state.get('user_email')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    try:
        # Obtener los datos del beneficiario de Supabase
        response = supabase_client.table("beneficiario").select("*").eq("id_beneficiario", user_db_id).limit(1).execute()

        if response.data:
            beneficiario_data = response.data[0]

            # Formulario para mostrar y modificar el perfil
            with st.form("perfil_form", clear_on_submit=False):
                st.info("Solo se pueden modificar los campos habilitados.")
                # CORRECCIÓN: Usar 'nombreb' para obtener el valor inicial
                nombre = st.text_input("Nombre", value=beneficiario_data.get('nombreb', ''))
                # El email y tipo de sangre no se deberían poder cambiar fácilmente desde aquí
                email = st.text_input("Email", value=beneficiario_data.get('mail', ''), disabled=True)
                telefono = st.text_input("Teléfono", value=beneficiario_data.get('telefono', ''))
                direccion = st.text_input("Dirección", value=beneficiario_data.get('direccion', ''))
                tipo_sangre_beneficiario = st.text_input("Tipo de Sangre (Registrado)", value=beneficiario_data.get('tipo_de_sangre', ''), disabled=True)

                st.markdown("---")
                update_button = st.form_submit_button("Actualizar Perfil")

                if update_button:
                    # Validar si algo cambió
                    # CORRECCIÓN: Usar 'nombreb' para comparar con el valor original
                    if (nombre == beneficiario_data.get('nombreb', '') and
                        telefono == beneficiario_data.get('telefono', '') and
                        direccion == beneficiario_data.get('direccion', '')):
                        st.warning("No hay cambios para actualizar.")
                        return

                    # Actualizar los datos en Supabase
                    update_data = {
                        "nombreb": nombre, # CORRECCIÓN: Usar 'nombreb' como clave para la actualización
                        "telefono": telefono,
                        "direccion": direccion,
                    }
                    update_response = supabase_client.table("beneficiario").update(update_data).eq("id_beneficiario", user_db_id).execute()

                    if update_response.data:
                        st.success("¡Perfil actualizado con éxito!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error al actualizar el perfil: {update_response.error.message}")
                        st.warning("Detalles técnicos: " + str(update_response.error))

        else:
            st.warning("No se pudieron cargar los datos de tu perfil. Intenta nuevamente.")
            if st.button("Recargar Perfil"):
                st.rerun()
            return

    except Exception as e:
        st.error(f"Error al cargar/actualizar los datos del perfil: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la conexión a Supabase esté activa y las RLS permitan la lectura/escritura de tu perfil.")

# Nueva función para obtener la lista de hospitales
def obtener_hospitales():
    if supabase_client is None:
        return []
    try:
        response = supabase_client.table("hospital").select("id_hospital, nombre_hospital").order("nombre_hospital").execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"Error al obtener la lista de hospitales: {e}")
        return []

def crear_campana_tab():
    st.header("💉 Crear Nueva Campaña de Donación")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    # Obtener hospitales para el selectbox
    hospitales = obtener_hospitales()
    hospital_options = {h['nombre_hospital']: h['id_hospital'] for h in hospitales}
    hospital_nombres = list(hospital_options.keys())

    with st.form("nueva_campana_form", clear_on_submit=True):
        st.markdown("Completa los siguientes datos para solicitar una donación de sangre.")

        nombre_campana = st.text_input("Nombre de la Campaña", help="Un título para tu solicitud de donación, ej: 'Urgente para Juan Pérez'.")
        descripcion = st.text_area("📝 Descripción Detallada", help="Ej: 'Se necesita sangre para operación de emergencia en Hospital Central.', 'Para paciente con anemia crónica, se agradecerá cualquier tipo de sangre.'.")
        
        today = date.today()
        
        fecha_inicio_display = st.date_input("🗓️ Fecha de Inicio (automática)", value=today, disabled=True)
        fecha_fin = st.date_input("🗓️ Fecha Límite para la Donación", min_value=today, value=today, help="Fecha hasta la cual necesitas la donación.")
        
        # CAMBIO: Selectbox para elegir hospital en lugar de campo de ubicación
        selected_hospital_name = st.selectbox(
            "🏥 Selecciona el Hospital para la Campaña",
            hospital_nombres,
            help="Elige el hospital donde se realizará la donación."
        )
        selected_hospital_id = hospital_options.get(selected_hospital_name) # Obtener ID del hospital seleccionado
        
        try:
            beneficiario_response = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", user_db_id).limit(1).execute()
            if beneficiario_response.data:
                tipo_sangre_beneficiario = beneficiario_response.data[0]['tipo_de_sangre']
                st.info(f"Tu tipo de sangre registrado es: **{tipo_sangre_beneficiario}**. Esto se asociará a la campaña.")
            else:
                st.warning("No se pudo obtener tu tipo de sangre registrado.")
                tipo_sangre_beneficiario = None
        except Exception as e:
            st.error(f"Error al obtener el tipo de sangre del beneficiario: {e}")
            tipo_sangre_beneficiario = None
            
        
        submit_button = st.form_submit_button("Crear Campaña")

        if submit_button:
            if not nombre_campana or not descripcion or not selected_hospital_id: # Validar que se seleccionó un hospital
                st.error("Por favor, completa todos los campos obligatorios: Nombre de la Campaña, Descripción y selecciona un Hospital.")
            elif fecha_fin < fecha_inicio_display:
                st.error("La fecha límite no puede ser anterior a la fecha de inicio.")
            else:
                try:
                    data_to_insert = {
                        "nombre_campana": nombre_campana,
                        "descripcion": descripcion, # Ahora esta columna existe en la DB
                        "fecha_inicio": str(fecha_inicio_display),
                        "fecha_fin": str(fecha_fin),
                        "id_hospital": selected_hospital_id, # Guardar el ID del hospital seleccionado
                        "id_beneficiario": user_db_id,
                        "estado_campana": "En curso"
                    }

                    insert_response = supabase_client.table("campana").insert(data_to_insert).execute()

                    if insert_response.data:
                        st.success(f"¡Campaña '{nombre_campana}' creada exitosamente!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error al crear la campaña: {insert_response.error.message}")
                        st.warning("Detalles técnicos: " + str(insert_response.error))

                except Exception as e:
                    st.error(f"Error al conectar con Supabase para crear campaña: {e}")
                    st.exception(e)


def mis_campanas_tab():
    st.header("📣 Mis Campañas Actuales")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    # Obtener hospitales para mostrar el nombre
    hospitales_data = obtener_hospitales()
    hospital_names_map = {h['id_hospital']: h['nombre_hospital'] for h in hospitales_data}

    try:
        campanas_response = supabase_client.table("campana").select("*").eq("id_beneficiario", user_db_id).order("fecha_fin", desc=False).execute()

        if campanas_response.data:
            st.subheader("Campañas Pendientes/En Curso:")
            found_active = False
            for campana in campanas_response.data:
                estado_lower = campana.get('estado_campana', '').lower()
                if estado_lower in ['en curso', 'próxima', 'activa']:
                    found_active = True
                    with st.container(border=True):
                        st.markdown(f"#### {campana.get('nombre_campana', 'Campaña sin nombre')}")
                        st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}") # Mostrar descripción
                        st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                        
                        # Mostrar el nombre del hospital en lugar de la ubicación
                        hospital_id = campana.get('id_hospital')
                        hospital_name = hospital_names_map.get(hospital_id, 'Hospital Desconocido')
                        st.write(f"**Hospital:** {hospital_name}")
                        
                        st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")

                        if st.button(f"Finalizar Campaña", key=f"finalizar_{campana['id_campana']}"):
                            try:
                                update_response = supabase_client.table("campana").update({"estado_campana": "Finalizada"}).eq("id_campana", campana['id_campana']).execute()
                                if update_response.data:
                                    st.success(f"Campaña '{campana.get('nombre_campana', '')}' finalizada con éxito.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Error al finalizar la campaña: {update_response.error.message}")
                                    st.warning("Detalles técnicos: " + str(update_response.error))
                            except Exception as e:
                                st.error(f"Error al conectar con Supabase para finalizar campaña: {e}")
                                st.exception(e)
                        st.markdown("---")
            if not found_active:
                st.info("No tienes campañas activas o próximas en este momento.")

            st.subheader("Campañas Finalizadas:")
            found_finished = False
            for campana in campanas_response.data:
                if campana.get('estado_campana', '').lower() == 'finalizada':
                    found_finished = True
                    with st.expander(f"Campaña '{campana.get('nombre_campana', 'Sin nombre')}' - Finalizada"):
                        st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                        st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                        
                        hospital_id = campana.get('id_hospital')
                        hospital_name = hospital_names_map.get(hospital_id, 'Hospital Desconocido')
                        st.write(f"**Hospital:** {hospital_name}") # Mostrar el nombre del hospital
                        
                        st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")
            if not found_finished:
                st.info("No tienes campañas finalizadas.")


        else:
            st.info("Aún no has creado ninguna campaña de donación. ¡Anímate a crear una!")

    except Exception as e:
        st.error(f"Error al cargar tus campañas: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la tabla 'campana' exista y las RLS permitan la lectura.")


def beneficiario_perfil_page():
    st.title("👤 Panel de Beneficiario")
    st.markdown("---")

    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Beneficiario':
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["Mi Perfil", "Crear Campaña", "Mis Campañas"])

    with tab1:
        perfil_beneficiario_tab()
    with tab2:
        crear_campana_tab()
    with tab3:
        mis_campanas_tab()

if __name__ == "__main__":
    beneficiario_perfil_page()
