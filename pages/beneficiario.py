# pages/beneficiario.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ ERROR: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el archivo .env.")
    st.info("Por favor, asegúrate de que tu archivo .env esté en la raíz del proyecto y contenga estas variables.")
else:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Opcional: Probar la conexión para asegurar que funciona
        # st.success("✅ Conexión a Supabase establecida.")
    except Exception as e:
        st.error(f"❌ ERROR al inicializar cliente Supabase en beneficiario.py: {e}")
        st.info("Verifica tu URL y Key de Supabase. Podría ser un problema de red o credenciales.")

def beneficiario_perfil():
    st.markdown("<h2 style='text-align: center; color: #B22222;'>Bienvenido a tu Perfil de Beneficiario</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes gestionar tus solicitudes de donación y ver tu información.")

    user_email = st.session_state.get('user_email')
    user_db_id = st.session_state.get('user_db_id')
    user_type = st.session_state.get('user_type') # Obtener el tipo de usuario para depuración

    if not user_email or not user_db_id:
        st.warning("⚠️ No se pudo cargar la información del usuario (email o ID). Por favor, inicia sesión de nuevo.")
        st.write(f"Estado actual de la sesión: Email={user_email}, ID={user_db_id}, Tipo={user_type}")
        return
    
    st.info(f"Sesión activa: Email={user_email}, ID de Beneficiario={user_db_id}")

    st.subheader(f"Hola, {user_email}!")

    tab1, tab2, tab3 = st.tabs(["📊 Mi Perfil", "💉 Mis Campañas de Donación", "✨ Crear Nueva Campaña"])

    with tab1:
        st.header("Información de tu Perfil")
        if supabase_client:
            try:
                # Usar id_beneficiario, que es la columna de ID en la tabla beneficiario
                response = supabase_client.table("beneficiario").select("*").eq("id_beneficiario", user_db_id).limit(1).execute()
                
                if response.data:
                    beneficiario_data = response.data[0]
                    st.write(f"**Nombre:** {beneficiario_data.get('nombre', 'N/A')}")
                    st.write(f"**Email:** {beneficiario_data.get('mail', 'N/A')}")
                    st.write(f"**Teléfono:** {beneficiario_data.get('telefono', 'N/A')}")
                    st.write(f"**Dirección:** {beneficiario_data.get('direccion', 'N/A')}")
                    st.write(f"**Tipo de Sangre Requerido:** {beneficiario_data.get('tipo_de_sangre', 'N/A')}") # Asegúrate de que esta columna exista

                    # Opcional: Permitir editar el perfil
                    st.markdown("---")
                    st.subheader("Actualizar Perfil")
                    with st.form("update_beneficiario_profile"):
                        updated_nombre = st.text_input("Nombre", value=beneficiario_data.get('nombre', ''))
                        updated_telefono = st.text_input("Teléfono", value=beneficiario_data.get('telefono', ''))
                        updated_direccion = st.text_input("Dirección", value=beneficiario_data.get('direccion', ''))
                        
                        tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                        # Asegúrate de que el valor existente esté en la lista para evitar errores de índice
                        current_tipo_sangre = beneficiario_data.get('tipo_de_sangre', 'O+')
                        if current_tipo_sangre not in tipos_sangre:
                            current_tipo_sangre = 'O+' # Valor predeterminado si el tipo de sangre de la DB no está en la lista
                        
                        updated_tipo_sangre = st.selectbox("Tipo de Sangre Requerido", tipos_sangre, index=tipos_sangre.index(current_tipo_sangre))

                        submit_update = st.form_submit_button("Actualizar Información")
                        if submit_update:
                            try:
                                update_data = {
                                    "nombre": updated_nombre,
                                    "telefono": updated_telefono,
                                    "direccion": updated_direccion,
                                    "tipo_de_sangre": updated_tipo_sangre # Nombre de columna consistente
                                }
                                update_response = supabase_client.table("beneficiario").update(update_data).eq("id_beneficiario", user_db_id).execute()
                                if update_response.data:
                                    st.success("¡Perfil actualizado exitosamente!")
                                    st.rerun() # Recarga para mostrar los datos actualizados
                                else:
                                    st.error(f"❌ Error al actualizar el perfil: {update_response.status_code} - {update_response.data}")
                                    st.json(update_response.data) # Mostrar más detalles del error de Supabase
                            except Exception as ex:
                                st.error(f"❌ Error al conectar con Supabase para actualizar: {ex}")
                                st.exception(ex) # Mostrar el traceback completo del error
                else:
                    st.warning(f"⚠️ No se encontraron datos para este beneficiario con ID: {user_db_id}. Verifica que el ID sea correcto en tu base de datos.")
            except Exception as e:
                st.error(f"❌ ERROR al cargar la información del beneficiario desde Supabase: {e}")
                st.exception(e)
        else:
            st.warning("⚠️ Supabase no está conectado para cargar la información del perfil.")

    with tab2:
        st.header("Mis Campañas de Donación")
        if supabase_client:
            try:
                # Ajusta el nombre de la tabla y la columna si son diferentes en tu Supabase
                # Usaremos 'solicitudes_sangre' como se mencionó antes.
                # Asegúrate de que 'id_beneficiario' es la FK correcta.
                campaigns_response = supabase_client.table("solicitudes_sangre").select("*").eq("id_beneficiario", user_db_id).execute()
                
                if campaigns_response.data:
                    st.success(f"✅ Se encontraron {len(campaigns_response.data)} campañas asociadas.")
                    for i, campaign in enumerate(campaigns_response.data):
                        st.markdown(f"#### Campaña #{i+1}: {campaign.get('titulo_campania', 'Sin título')}")
                        st.write(f"**Tipo de Sangre Necesario:** {campaign.get('tipo_sangre_requerido', 'N/A')}")
                        st.write(f"**Cantidad Requerida:** {campaign.get('cantidad_unidades', 'N/A')} unidades")
                        st.write(f"**Fecha Límite:** {campaign.get('fecha_limite', 'N/A')}")
                        st.write(f"**Descripción:** {campaign.get('descripcion', 'N/A')}")
                        st.write(f"**Estado:** {campaign.get('estado', 'Activa')}")
                        st.markdown("---")
                else:
                    st.info("ℹ️ Aún no tienes campañas de donación asociadas. ¡Crea una en la siguiente pestaña!")
            except Exception as e:
                st.error(f"❌ ERROR al cargar tus campañas de donación: {e}")
                st.exception(e)
        else:
            st.warning("⚠️ Supabase no está conectado para cargar las campañas.")


    with tab3:
        st.header("Crear Nueva Campaña de Donación")
        st.write("Completa los detalles para crear una nueva solicitud de donación de sangre.")

        # Reutiliza la lista de tipos_sangre para el selectbox
        tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

        with st.form("new_campaign_form"):
            campaign_title = st.text_input("Título de la Campaña", help="Ej: 'Urgencia de Sangre O+ para [Nombre del Paciente]'")
            required_blood_type = st.selectbox("Tipo de Sangre Necesario", tipos_sangre)
            required_units = st.number_input("Cantidad de Unidades Requeridas", min_value=1, max_value=100, value=1, help="¿Cuántas unidades de sangre necesitas?")
            due_date = st.date_input("Fecha Límite para la Donación", help="¿Hasta cuándo necesitas las donaciones?")
            description = st.text_area("Descripción de la Campaña", help="Proporciona detalles importantes, como la situación, el hospital, etc.")

            create_campaign_button = st.form_submit_button("Crear Campaña")

            if create_campaign_button:
                if not campaign_title or not required_blood_type or not required_units or not due_date or not description:
                    st.error("⚠️ Por favor, completa todos los campos para crear la campaña.")
                elif supabase_client:
                    try:
                        data_to_insert = {
                            "id_beneficiario": user_db_id,
                            "titulo_campania": campaign_title,
                            "tipo_sangre_requerido": required_blood_type,
                            "cantidad_unidades": required_units,
                            "fecha_limite": str(due_date), # Convertir a string para Supabase (formato YYYY-MM-DD)
                            "descripcion": description,
                            "estado": "Activa" # Estado inicial de la campaña
                        }
                        insert_response = supabase_client.table("solicitudes_sangre").insert(data_to_insert).execute()
                        
                        if insert_response.data:
                            st.success("🎉 ¡Campaña de donación creada exitosamente!")
                            st.balloons()
                            # Puedes limpiar el formulario o redirigir
                            # st.session_state['refresh_campaigns'] = True # Si quieres forzar un refresh en otra parte
                            # st.experimental_rerun() # Opcional si quieres un refresh completo
                            # Si quieres limpiar el formulario después de enviar, podrías poner las claves de los inputs en el st.session_state
                            # y reiniciarlas, o simplemente usar un mensaje de éxito y permitir que el usuario siga creando.
                        else:
                            st.error(f"❌ Error al crear la campaña: {insert_response.status_code} - {insert_response.data}")
                            st.json(insert_response.data) # Mostrar la respuesta de error de Supabase
                    except Exception as e:
                        st.error(f"❌ ERROR al conectar con Supabase para crear campaña: {e}")
                        st.exception(e)
                else:
                    st.warning("⚠️ Supabase no está conectado. No se pudo crear la campaña.")

