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
                nombre = st.text_input("Nombre", value=beneficiario_data.get('nombre', ''))
                # El email y tipo de sangre no se deberían poder cambiar fácilmente desde aquí
                email = st.text_input("Email", value=beneficiario_data.get('mail', ''), disabled=True)
                telefono = st.text_input("Teléfono", value=beneficiario_data.get('telefono', ''))
                direccion = st.text_input("Dirección", value=beneficiario_data.get('direccion', ''))
                tipo_sangre_beneficiario = st.text_input("Tipo de Sangre (Registrado)", value=beneficiario_data.get('tipo_de_sangre', ''), disabled=True)

                st.markdown("---")
                update_button = st.form_submit_button("Actualizar Perfil")

                if update_button:
                    # Validar si algo cambió
                    if (nombre == beneficiario_data.get('nombre', '') and
                        telefono == beneficiario_data.get('telefono', '') and
                        direccion == beneficiario_data.get('direccion', '')):
                        st.warning("No hay cambios para actualizar.")
                        return

                    # Actualizar los datos en Supabase
                    update_data = {
                        "nombre": nombre,
                        "telefono": telefono,
                        "direccion": direccion,
                    }
                    update_response = supabase_client.table("beneficiario").update(update_data).eq("id_beneficiario", user_db_id).execute()

                    if update_response.data:
                        st.success("¡Perfil actualizado con éxito!")
                        st.balloons()
                        time.sleep(1)
                        st.experimental_rerun()  # Recargar para mostrar los cambios
                    else:
                        st.error(f"Error al actualizar el perfil: {update_response.error.message}")
                        st.warning("Detalles técnicos: " + str(update_response.error))

        else:
            st.warning("No se pudieron cargar los datos de tu perfil. Intenta nuevamente.")
            # Puedes ofrecer una opción para recargar o contactar soporte
            if st.button("Recargar Perfil"):
                st.experimental_rerun()
            return

    except Exception as e:
        st.error(f"Error al cargar/actualizar los datos del perfil: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la conexión a Supabase esté activa y las RLS permitan la lectura/escritura de tu perfil.")


def crear_campana_tab():
    st.header("💉 Crear Nueva Campaña de Donación")
    st.markdown("---")

    user_db_id = st.session_state.get('user_db_id')

    if not user_db_id:
        st.warning("No se encontró el ID de beneficiario en la sesión. Por favor, reinicia la sesión.")
        return

    # Formulario para crear una nueva campaña
    with st.form("nueva_campana_form", clear_on_submit=True):
        st.markdown("Completa los siguientes datos para solicitar una donación de sangre.")

        nombre_campana = st.text_input("Nombre de la Campaña", help="Un título para tu solicitud de donación, ej: 'Urgente para Juan Pérez'.")
        descripcion = st.text_area("📝 Descripción Detallada", help="Ej: 'Se necesita sangre para operación de emergencia en Hospital Central.', 'Para paciente con anemia crónica, se agradecerá cualquier tipo de sangre.'.")
        
        # Obtener la fecha actual
        today = date.today()
        
        # Asumo que fecha_inicio es la fecha actual y fecha_fin es la fecha límite
        fecha_inicio = st.date_input("🗓️ Fecha de Inicio (automática)", value=today, disabled=True)
        fecha_fin = st.date_input("🗓️ Fecha Límite para la Donación", min_value=today, value=today, help="Fecha hasta la cual necesitas la donación.")
        
        ubicacion = st.text_input("📍 Ubicación de la Donación", help="Ej: 'Hospital Central, Sala 3', 'Clínica San Martín'.")
        
        # Si tienes el tipo de sangre del beneficiario, lo puedes mostrar aquí como referencia
        try:
            beneficiario_response = supabase_client.table("beneficiario").select("tipo_de_sangre").eq("id_beneficiario", user_db_id).limit(1).execute()
            if beneficiario_response.data:
                tipo_sangre_beneficiario = beneficiario_response.data[0]['tipo_de_sangre']
                st.info(f"Tu tipo de sangre registrado es: **{tipo_sangre_beneficiario}**. Esto se asociará a la campaña.")
            else:
                st.warning("No se pudo obtener tu tipo de sangre registrado.")
                tipo_sangre_beneficiario = None # Asegurarse de que no falle si no se encuentra
        except Exception as e:
            st.error(f"Error al obtener el tipo de sangre del beneficiario: {e}")
            tipo_sangre_beneficiario = None
            
        # Consideración: Si `id_hospital` en tu tabla `campaña` no es NULL, podrías necesitar un selectbox aquí.
        # Por ahora, lo dejaremos como NULL si no se pide un hospital específico.
        # id_hospital_asociado = st.selectbox("Asociar a Hospital (Opcional)", ["Ninguno", "Hospital A", "Hospital B"])
        # Aquí necesitarías cargar los hospitales de tu base de datos si lo implementas.
        
        submit_button = st.form_submit_button("Crear Campaña")

        if submit_button:
            if not nombre_campana or not descripcion or not ubicacion:
                st.error("Por favor, completa todos los campos obligatorios: Nombre de la Campaña, Descripción y Ubicación.")
            elif fecha_fin < fecha_inicio:
                st.error("La fecha límite no puede ser anterior a la fecha de inicio.")
            else:
                try:
                    data_to_insert = {
                        "nombre_campana": nombre_campana,
                        "descripcion": descripcion,
                        "fecha_inicio": str(fecha_inicio),
                        "fecha_fin": str(fecha_fin),
                        "ubicacion": ubicacion,
                        "id_beneficiario": user_db_id,
                        # "id_hospital": None, # O el ID del hospital si lo seleccionas
                        "estado_campana": "En curso" # Estado inicial
                        # Si necesitas el tipo de sangre en la campaña, debes añadir la columna 'tipo_de_sangre_requerido' a tu tabla 'campaña'
                        # "tipo_de_sangre_requerido": tipo_sangre_beneficiario,
                    }

                    insert_response = supabase_client.table("campaña").insert(data_to_insert).execute()

                    if insert_response.data:
                        st.success(f"¡Campaña '{nombre_campana}' creada exitosamente!")
                        st.balloons()
                        time.sleep(1)
                        st.experimental_rerun() # Recarga para mostrar la nueva campaña en la pestaña "Mis Campañas"
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

    try:
        # Obtener las campañas del beneficiario
        # Asumo que 'id_beneficiario' es la FK en 'campaña' que apunta a 'beneficiario'
        campanas_response = supabase_client.table("campaña").select("*").eq("id_beneficiario", user_db_id).order("fecha_fin", desc=False).execute()

        if campanas_response.data:
            st.subheader("Campañas Pendientes/En Curso:")
            found_active = False
            for campana in campanas_response.data:
                # Opcional: Filtrar o clasificar por estado_campana
                if campana.get('estado_campana', '').lower() == 'en curso' or campana.get('estado_campana', '').lower() == 'próxima':
                    found_active = True
                    st.markdown(f"#### {campana.get('nombre_campana', 'Campaña sin nombre')}")
                    st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                    st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                    st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                    st.write(f"**Ubicación:** {campana.get('ubicacion', 'N/A')}")
                    st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")
                    # if campana.get('tipo_de_sangre_requerido'): # Si añades esta columna
                    #     st.write(f"**Tipo de Sangre Necesario:** {campana.get('tipo_de_sangre_requerido', 'N/A')}")
                    st.markdown("---")
            if not found_active:
                st.info("No tienes campañas activas o próximas en este momento.")

            # Opcional: Mostrar campañas finalizadas
            st.subheader("Campañas Finalizadas:")
            found_finished = False
            for campana in campanas_response.data:
                if campana.get('estado_campana', '').lower() == 'finalizada':
                    found_finished = True
                    with st.expander(f"Campaña '{campana.get('nombre_campana', 'Sin nombre')}' - Finalizada"):
                        st.write(f"**Descripción:** {campana.get('descripcion', 'N/A')}")
                        st.write(f"**Fecha Inicio:** {campana.get('fecha_inicio', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}")
                        st.write(f"**Ubicación:** {campana.get('ubicacion', 'N/A')}")
                        st.write(f"**Estado:** `{campana.get('estado_campana', 'N/A')}`")
            if not found_finished:
                st.info("No tienes campañas finalizadas.")


        else:
            st.info("Aún no has creado ninguna campaña de donación. ¡Anímate a crear una!")

    except Exception as e:
        st.error(f"Error al cargar tus campañas: {e}")
        st.exception(e)
        st.warning("Asegúrate de que la tabla 'campaña' exista y las RLS permitan la lectura.")


def beneficiario_perfil_page():
    st.title("👤 Panel de Beneficiario")
    st.markdown("---")

    # Asegurarse de que el usuario esté logueado como beneficiario
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Beneficiario':
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        st.stop() # Detiene la ejecución de la página

    # Definir las pestañas
    tab1, tab2, tab3 = st.tabs(["Mi Perfil", "Crear Campaña", "Mis Campañas"])

    with tab1:
        perfil_beneficiario_tab()
    with tab2:
        crear_campana_tab()
    with tab3:
        mis_campanas_tab()

# Punto de entrada principal para esta página
if __name__ == "__main__":
    beneficiario_perfil_page()