import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carga las variables de entorno para Supabase
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializa el cliente de Supabase una vez
# Se añade una comprobación para asegurar que las variables de entorno están cargadas
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase en beneficiario.py: {e}")
        supabase_client: Client = None # Asegurarse de que sea None si hay un error
else:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env en beneficiario.py.")
    supabase_client: Client = None


def get_beneficiario_data(beneficiario_id):
    """Obtiene los datos del beneficiario desde la base de datos de forma más robusta."""
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del beneficiario.")
        return None
    try:
        # Eliminamos .single() para evitar errores si no se encuentra el registro o hay múltiples
        response = supabase_client.table("beneficiario").select("*").eq("id_beneficio", beneficiario_id).limit(1).execute()
        if response.data:
            return response.data[0] # Retorna el primer (y único esperado) resultado
        return None
    except Exception as e:
        st.error(f"Error al obtener datos del beneficiario: {e}")
        return None

def get_beneficiario_campaign(beneficiario_id):
    """
    Verifica si el beneficiario tiene una campaña activa.
    ASUMIMOS:
    - Que la tabla de campañas se llama 'campana' (o 'campania' si es el caso).
    - Que tiene una columna 'id_beneficio' que se relaciona con el beneficiario.
    - Que tiene una columna 'estado' que puede ser 'activa', 'finalizada', etc.
    """
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos de campaña.")
        return None
    try:
        # Busca campañas activas asociadas a este beneficiario
        response = supabase_client.table("campana").select("*").eq("id_beneficio", beneficiario_id).eq("estado", "activa").limit(1).execute()
        if response.data:
            return response.data[0] # Retorna la primera campaña activa encontrada
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
            "id_beneficio": beneficiario_id, # Columna que relaciona con el beneficiario
            "tipo_sangre_requerida": tipo_sangre_requerida, # ASUME este nombre de columna
            "cantidad_requerida": cantidad_requerida, # ASUME este nombre de columna
            "descripcion": descripcion, # ASUME este nombre de columna
            "fecha_limite": fecha_limite, # ASUME este nombre de columna
            "estado": "activa" # Estado inicial de la campaña
            # Aquí podrías añadir 'id_hospital' si los hospitales también pueden crear campañas,
            # o 'fecha_creacion' si tu tabla no tiene una columna para ello.
        }
        response = supabase_client.table("campana").insert(data).execute()
        if response.data:
            st.success("Campaña creada exitosamente!")
            return True
        else:
            st.error(f"Error al crear campaña: {response.status_code} - {response.data}")
            return False
    except Exception as e:
        st.error(f"Error al crear campaña en Supabase: {e}")
        return False

def beneficiario_perfil():
    st.markdown("## Área de Beneficiario")

    # Obtener el ID del beneficiario de la sesión
    beneficiario_id = st.session_state.get('user_db_id')
    
    # ¡IMPORTANTE! Verificar que el beneficiario_id no sea None
    if not beneficiario_id:
        st.warning("No se pudo cargar el perfil del beneficiario. Por favor, asegúrate de haber iniciado sesión correctamente.")
        st.info("Si el problema persiste, verifica la configuración de tu `SUPABASE_URL` y `SUPABASE_KEY` en el archivo `.env` y el `id_columna_db` en `main.py` para el beneficiario.")
        return

    # Pestañas
    tab1, tab2 = st.tabs(["📊 Mi Perfil", "📢 Mis Campañas"])

    with tab1:
        st.markdown("### Datos de tu Perfil")
        beneficiario_data = get_beneficiario_data(beneficiario_id)
        if beneficiario_data:
            st.write(f"**Nombre:** {beneficiario_data.get('nombre', 'N/A')}")
            st.write(f"**Email:** {beneficiario_data.get('mail', 'N/A')}")
            st.write(f"**Teléfono:** {beneficiario_data.get('telefono', 'N/A')}")
            st.write(f"**Dirección:** {beneficiario_data.get('direccion', 'N/A')}")
            st.write(f"**Tipo de Sangre Requerido:** {beneficiario_data.get('tipo_de_sangre', 'N/A')}")
            # Aquí podrías añadir un botón para editar el perfil si lo deseas
        else:
            st.info("Cargando datos del perfil o el perfil no se encontró. Asegúrate de que el ID del beneficiario sea correcto.")

    with tab2:
        st.markdown("### Gestión de Campañas de Donación")
        
        current_campaign = get_beneficiario_campaign(beneficiario_id)

        if current_campaign:
            st.success("¡Tienes una campaña de donación en curso!")
            st.write(f"**Campaña ID:** {current_campaign.get('id_campana', 'N/A')}") # ASUME 'id_campana' como ID de campaña
            st.write(f"**Tipo de Sangre Requerida:** {current_campaign.get('tipo_sangre_requerida', 'N/A')}")
            st.write(f"**Cantidad Requerida:** {current_campaign.get('cantidad_requerida', 'N/A')} unidades")
            st.write(f"**Descripción:** {current_campaign.get('descripcion', 'N/A')}")
            st.write(f"**Fecha Límite:** {current_campaign.get('fecha_limite', 'N/A')}")
            st.write(f"**Estado:** {current_campaign.get('estado', 'N/A')}")
            
            # Aquí podrías añadir botones para 'Finalizar Campaña', 'Ver Progreso', etc.
            if st.button("Finalizar Campaña (no funcional aún)"):
                st.info("Funcionalidad para finalizar campaña en desarrollo.")

        else:
            st.info("Actualmente no tienes ninguna campaña de donación activa.")
            st.markdown("### Crea una Nueva Campaña")
            
            with st.form("create_campaign_form", clear_on_submit=True):
                # Obtener el tipo de sangre del beneficiario automáticamente
                beneficiario_data = get_beneficiario_data(beneficiario_id)
                if beneficiario_data and beneficiario_data.get('tipo_de_sangre'):
                    default_blood_type = beneficiario_data.get('tipo_de_sangre')
                    st.write(f"**Tu tipo de sangre es:** {default_blood_type}")
                    st.markdown("---")
                    st.info("La campaña se creará para tu tipo de sangre.")
                    # No permitimos cambiarlo para simplificar, se asume que piden para ellos.
                else:
                    st.warning("No se pudo determinar tu tipo de sangre. Por favor, asegúrate de que esté registrado en tu perfil.")
                    default_blood_type = None # Cambiado a None si no se encuentra
                
                campaign_cantidad = st.number_input("Cantidad de Unidades Requeridas", min_value=1, max_value=10, value=1, help="¿Cuántas unidades de sangre necesitas?")
                campaign_descripcion = st.text_area("Descripción de la Campaña (opcional)", help="Ej: 'Urgente para cirugía de emergencia', 'Para tratamiento continuo'")
                campaign_fecha_limite = st.date_input("Fecha Límite (opcional)", help="Hasta cuándo te gustaría que esté activa la campaña.")

                create_campaign_button = st.form_submit_button("Crear Campaña")

                if create_campaign_button:
                    if not default_blood_type:
                        st.error("No se puede crear la campaña sin un tipo de sangre definido. Por favor, completa tu perfil.")
                    elif not campaign_cantidad:
                         st.error("Por favor, ingresa la cantidad de unidades requeridas.")
                    else:
                        # Llama a la función para crear la campaña
                        if create_new_campaign_db(beneficiario_id, default_blood_type, campaign_cantidad, campaign_descripcion, campaign_fecha_limite):
                            st.success("Campaña creada. Actualizando...")
 