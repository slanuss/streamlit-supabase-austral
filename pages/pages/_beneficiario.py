import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import time # Importar time para usar time.sleep()

# Carga las variables de entorno
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env para beneficiario.py.")
    supabase_client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase en beneficiario.py: {e}")
        supabase_client = None

# --- Funciones de interacción con la DB para Beneficiarios ---

def get_beneficiario_data(beneficiario_id):
    """
    Obtiene los datos del beneficiario desde la base de datos usando su ID.
    Utiliza el ID_Beneficio que se guarda en la sesión.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del beneficiario.")
        return None
    try:
        # Aquí se usa 'id_beneficio' como la columna de ID en la tabla 'beneficiario'
        response = supabase_client.table("beneficiario").select("*").eq("id_beneficio", beneficiario_id).limit(1).execute()
        if response.data:
            return response.data[0] # Retorna el primer (y único esperado) resultado
        return None
    except Exception as e:
        st.error(f"Error al obtener datos del beneficiario: {e}")
        return None

def update_beneficiario_profile_db(beneficiario_id, updated_data):
    """
    Actualiza los datos del perfil del beneficiario en la base de datos.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede actualizar el perfil.")
        return False
    try:
        # Se actualiza el registro con el id_beneficio
        response = supabase_client.table("beneficiario").update(updated_data).eq("id_beneficio", beneficiario_id).execute()
        if response.data:
            st.success("Perfil de beneficiario actualizado exitosamente!")
            return True
        else:
            st.error(f"Error al actualizar perfil de beneficiario: {response.status_code} - {response.data}")
            return False
    except Exception as e:
        st.error(f"Error al actualizar perfil en Supabase: {e}")
        return False

def get_beneficiario_campaign(beneficiario_id):
    """
    Verifica si el beneficiario tiene una campaña activa.
    Asume tabla 'campana' con columnas 'id_beneficio' y 'estado'.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos de campaña.")
        return None
    try:
        response = supabase_client.table("campana").select("*").eq("id_beneficio", beneficiario_id).eq("estado", "activa").limit(1).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error al verificar la campaña del beneficiario: {e}")
        return None

def create_new_campaign_db(beneficiario_id, tipo_sangre_requerida, cantidad_requerida, descripcion, fecha_limite):
    """
    Crea una nueva campaña en la base de datos.
    Ajusta los nombres de las columnas según tu tabla 'campana'.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña.")
        return False
    try:
        data = {
            "id_beneficio": beneficiario_id,
            "tipo_sangre_requerida": tipo_sangre_requerida,
            "cantidad_requerida": cantidad_requerida,
            "descripcion": descripcion,
            "fecha_limite": str(fecha_limite), # Asegurar formato de string para Supabase date
            "estado": "activa"
        }
        response = supabase_client.table("campana").insert(data).execute()
        if response.data:
            return True
        else:
            st.error(f"Error al crear campaña: {response.status_code} - {response.data}")
            return False
    except Exception as e:
        st.error(f"Error al crear campaña en Supabase: {e}")
        return False

# --- Secciones de la página del Beneficiario ---
def beneficiario_perfil():
    st.markdown("## Área de Beneficiario")

    beneficiario_id = st.session_state.get('user_db_id')
    
    if not beneficiario_id:
        st.warning("No se pudo cargar el perfil del beneficiario. Por favor, asegúrate de haber iniciado sesión correctamente.")
        st.info("Si el problema persiste, verifica la configuración de tu `SUPABASE_URL` y `SUPABASE_KEY` en el archivo `.env` y el `id_columna_db` en `main.py` para el beneficiario.")
        return

    tab1, tab2 = st.tabs(["📊 Mi Perfil", "📢 Mis Campañas"])

    with tab1:
        st.markdown("### Datos de tu Perfil")
        beneficiario_data = get_beneficiario_data(beneficiario_id)

        # Inicializa los valores para los campos del formulario
        valores_iniciales = {
            "nombre": "",
            "mail": st.session_state.get('user_email', ''), # Email del usuario logueado
            "telefono": "",
            "direccion": "",
            "tipo_de_sangre": "O+", # Tipo de sangre que el beneficiario requiere
        }

        # Si encontramos un perfil existente, actualizamos los valores iniciales
        if beneficiario_data:
            st.info(f"Cargando datos de perfil para: {beneficiario_data.get('nombre', 'N/A')}")
            valores_iniciales["nombre"] = beneficiario_data.get("nombre", "")
            valores_iniciales["mail"] = beneficiario_data.get("mail", st.session_state.get('user_email', ''))
            valores_iniciales["telefono"] = beneficiario_data.get("telefono", "")
            valores_iniciales["direccion"] = beneficiario_data.get("direccion", "")
            if beneficiario_data.get("tipo_de_sangre") in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
                valores_iniciales["tipo_de_sangre"] = beneficiario_data.get("tipo_de_sangre")
        else:
            st.warning("No se encontraron datos de perfil existentes. Por favor, completa y guarda tu perfil.")


        with st.form("perfil_beneficiario_form"):
            # Campos del formulario - AJUSTADOS A TUS COLUMNAS DE SUPABASE
            nombre = st.text_input("Nombre", value=valores_iniciales["nombre"])
            mail = st.text_input("Mail de Contacto", value=valores_iniciales["mail"], disabled=True) # Email debería ser inmutable
            telefono = st.text_input("Teléfono de Contacto", value=valores_iniciales["telefono"])
            direccion = st.text_input("Dirección", value=valores_iniciales["direccion"])

            sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            # Buscar el índice del tipo de sangre actual, si no se encuentra, usar 0
            try:
                sangre_index = sangre_options.index(valores_iniciales["tipo_de_sangre"])
            except ValueError:
                sangre_index = 0 # Valor por defecto si no se encuentra

            tipo_de_sangre = st.selectbox("Tipo de Sangre Requerido", sangre_options, index=sangre_index)
            
            guardar_button = st.form_submit_button("Actualizar Perfil")

            if guardar_button:
                # Construye el diccionario con los datos del formulario para actualizar
                datos_a_actualizar = {
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                    "tipo_de_sangre": tipo_de_sangre,
                    # No actualizamos 'mail' ni 'id_beneficio' desde aquí
                }
                if update_beneficiario_profile_db(beneficiario_id, datos_a_actualizar):
                    st.success("Perfil actualizado. Recargando datos...")
                    time.sleep(1)
                    st.rerun() # Para que los datos actualizados se reflejen


    with tab2:
        st.markdown("### Gestión de Campañas de Donación")
        
        current_campaign = get_beneficiario_campaign(beneficiario_id)

        if current_campaign:
            st.success("¡Tienes una campaña de donación en curso!")
            st.write(f"**Campaña ID:** {current_campaign.get('id_campana', 'N/A')}")
            st.write(f"**Tipo de Sangre Requerida:** {current_campaign.get('tipo_sangre_requerida', 'N/A')}")
            st.write(f"**Cantidad Requerida:** {current_campaign.get('cantidad_requerida', 'N/A')} unidades")
            st.write(f"**Descripción:** {current_campaign.get('descripcion', 'N/A')}")
            st.write(f"**Fecha Límite:** {current_campaign.get('fecha_limite', 'N/A')}")
            st.write(f"**Estado:** {current_campaign.get('estado', 'N/A')}")
            
            if st.button("Finalizar Campaña (no funcional aún)"):
                st.info("Funcionalidad para finalizar campaña en desarrollo.")

        else:
            st.info("Actualmente no tienes ninguna campaña de donación activa.")
            st.markdown("### Crea una Nueva Campaña")
            
            with st.form("create_campaign_form", clear_on_submit=True):
                # Obtener el tipo de sangre del beneficiario automáticamente del perfil actual
                beneficiario_data_for_campaign = get_beneficiario_data(beneficiario_id)
                default_blood_type = None
                if beneficiario_data_for_campaign and beneficiario_data_for_campaign.get('tipo_de_sangre'):
                    default_blood_type = beneficiario_data_for_campaign.get('tipo_de_sangre')
                    st.write(f"**Tu tipo de sangre es:** {default_blood_type}")
                    st.markdown("---")
                    st.info("La campaña se creará para tu tipo de sangre.")
                else:
                    st.warning("No se pudo determinar tu tipo de sangre. Por favor, asegúrate de que esté registrado en tu perfil para crear una campaña.")
                
                campaign_cantidad = st.number_input("Cantidad de Unidades Requeridas", min_value=1, max_value=10, value=1, help="¿Cuántas unidades de sangre necesitas?")
                campaign_descripcion = st.text_area("Descripción de la Campaña (opcional)", help="Ej: 'Urgente para cirugía de emergencia', 'Para tratamiento continuo'")
                campaign_fecha_limite = st.date_input("Fecha Límite (opcional)", help="Hasta cuándo te gustaría que esté activa la campaña.")

                create_campaign_button = st.form_submit_button("Crear Campaña")

                if create_campaign_button:
                    if not default_blood_type:
                        st.error("No se puede crear la campaña sin un tipo de sangre definido en tu perfil.")
                    elif not campaign_cantidad:
                         st.error("Por favor, ingresa la cantidad de unidades requeridas.")
                    else:
                        if create_new_campaign_db(beneficiario_id, default_blood_type, campaign_cantidad, campaign_descripcion, campaign_fecha_limite):
                            st.success("Campaña creada. Recargando la página para mostrar el estado...")
                            time.sleep(2)
                            st.rerun()

# --- Lógica principal de la página del Beneficiario (para ejecución directa si es necesario) ---
if __name__ == "__main__":
    # Este bloque se ejecuta solo si ejecutas 'streamlit run pages/beneficiario.py'
    # Normalmente, esta página se importa y llama desde main.py.
    # Esta parte es solo para pruebas directas del archivo de página.
    st.set_page_config(layout="centered")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_type'] = None
        st.session_state['user_email'] = None
        st.session_state['user_db_id'] = None
    
    # Simular un inicio de sesión de beneficiario para pruebas directas
    if not st.session_state['logged_in'] or st.session_state['user_type'] != 'Beneficiario':
        st.warning("Estás viendo esta página en modo de desarrollo. Para una funcionalidad completa, ejecuta 'main.py' e inicia sesión como Beneficiario.")
        st.session_state['logged_in'] = True
        st.session_state['user_type'] = 'Beneficiario'
        st.session_state['user_email'] = "ricardo.vargas@email.com" # Email de prueba
        st.session_state['user_db_id'] = 1 # ID de prueba, ajusta según tu DB.
        st.info("Simulando inicio de sesión como beneficiario para desarrollo.")
        time.sleep(1)
        st.rerun() # Recarga para aplicar la simulación de sesión
    
    st.sidebar.title("Navegación Beneficiario")
    menu = ["Perfil", "Solicitud de Campañas"] # "Historial de Donaciones" si lo implementas
    opcion = st.sidebar.selectbox("Selecciona una sección", menu)

    if opcion == "Perfil":
        beneficiario_perfil()
    elif opcion == "Solicitud de Campañas":
        # Se ha integrado la lógica de campañas directamente en beneficiario_perfil() en la pestaña
        # pero si deseas una sección separada, puedes mover el contenido de la pestaña 2 aquí.
        st.info("La gestión de campañas está integrada en la pestaña 'Mis Campañas' dentro de la sección 'Perfil'.")
        # beneficiario_campanas_solicitud() # Si decides separarlo
    # elif opcion == "Historial de Donaciones":
    #     beneficiario_historial_donaciones()