# pages/beneficiario.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

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

def guardar_perfil_beneficiario_supabase(datos_beneficiario: dict, actualizar: bool = False, beneficiario_mail: str = None):
    if supabase_client:
        try:
            if actualizar and beneficiario_mail:
                # Asegúrate que 'mail' es la columna correcta para la condición WHERE
                data, count = supabase_client.table("beneficiario").update(datos_beneficiario).eq("mail", beneficiario_mail).execute()
                if data and len(data) > 0:
                    st.success("✅ Perfil de beneficiario actualizado en Supabase con éxito!")
                    return True
                else:
                    st.warning("⚠️ No se encontró el perfil para actualizar o no hubo cambios. ¿El correo existe en la base de datos?")
                    return False
            else:
                data, count = supabase_client.table("beneficiario").insert(datos_beneficiario).execute()
                if data and len(data) > 0:
                    st.success("✅ Perfil de beneficiario guardado en Supabase con éxito!")
                    return True
                else:
                    st.error("❌ Error al guardar el perfil del beneficiario en Supabase. No se insertaron registros.")
                    return False
        except Exception as e:
            st.error(f"❌ Error de conexión, inserción o actualización en Supabase (beneficiario): {e}")
            return False
    else:
        st.warning("⚠️ No se pudo conectar a Supabase para guardar/actualizar el perfil del beneficiario. Revisa tus variables .env.")
        return False

def obtener_perfil_beneficiario(email_beneficiario: str):
    """
    Obtiene el perfil de un beneficiario desde Supabase usando su email.
    Asegúrate que la columna de email en tu tabla 'beneficiario' se llame 'mail'.
    """
    if supabase_client:
        try:
            response = supabase_client.table("beneficiario").select("*").eq("mail", email_beneficiario).limit(1).execute()
            if response.data:
                return response.data[0] # Retorna el primer (y único) registro encontrado
            else:
                st.info(f"ℹ️ No se encontró un perfil de beneficiario con el email: {email_beneficiario}. Crea uno nuevo.")
                return None
        except Exception as e:
            st.error(f"❌ Error al obtener perfil del beneficiario desde Supabase: {e}. Asegúrate que la tabla 'beneficiario' existe y tiene una columna 'mail'.")
            return None
    return None


def crear_campana_supabase(datos_campana: dict):
    if supabase_client:
        try:
            data, count = supabase_client.table("campaña").insert(datos_campana).execute()
            if data and len(data) > 0:
                st.success("🎉 Campaña creada y guardada en Supabase con éxito!")
                return True
            else:
                st.error("❌ Error al guardar la campaña en Supabase. No se insertaron registros.")
                return False
        except Exception as e:
            st.error(f"❌ Error de conexión o inserción en Supabase (campaña): {e}")
            return False
    else:
        st.warning("⚠️ No se pudo conectar a Supabase para guardar la campaña. Revisa tus variables .env.")
        return False

# --- Secciones de la página del Beneficiario ---
def beneficiario_perfil():
    st.markdown("<h2 style='color: #4682B4;'>Mi Perfil de Beneficiario 📝</h2>", unsafe_allow_html=True)
    st.write("Mantén tu información actualizada para que podamos asistirte de la mejor manera.")

    email_usuario_logueado = st.session_state.get('user_email', 'beneficiario@ejemplo.com')
    beneficiario_id_logueado = st.session_state.get('user_db_id')

    # Intentamos obtener el perfil existente basado en el email logueado
    perfil_existente = obtener_perfil_beneficiario(email_usuario_logueado)

    # Inicializa los valores por defecto del formulario
    valores_iniciales = {
        "NombreB": "",
        "mail": email_usuario_logueado,
        "Teléfono": "",
        "Dirección": "",
        "Tipo de Sangre": "O+",  # Valor por defecto
    }

    # Si se encontró un perfil existente, sobrescribe los valores por defecto
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('NombreB', 'N/A')}**")
        valores_iniciales["NombreB"] = perfil_existente.get("NombreB", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["Teléfono"] = perfil_existente.get("Teléfono", "")
        valores_iniciales["Dirección"] = perfil_existente.get("Dirección", "")
        
        # Asegurarse de que el tipo de sangre es una opción válida para el selectbox
        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("Tipo de Sangre") in sangre_opciones:
            valores_iniciales["Tipo de Sangre"] = perfil_existente.get("Tipo de Sangre")
        else: # Si el valor de la DB no es válido, usa el valor por defecto
            valores_iniciales["Tipo de Sangre"] = "O+" 

    with st.form("perfil_beneficiario_form"):
        st.markdown("#### Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            # Asegúrate que el key 'NombreB' exista en tu tabla de Supabase para beneficiarios
            NombreB = st.text_input("Nombre y Apellido", value=valores_iniciales["NombreB"])
            mail = st.text_input("Mail de Contacto", value=valores_iniciales["mail"], disabled=True)
        with col2:
            # Asegúrate que el key 'Teléfono' exista en tu tabla de Supabase para beneficiarios
            Teléfono = st.text_input("Teléfono de Contacto", value=valores_iniciales["Teléfono"])
            # Asegúrate que el key 'Dirección' exista en tu tabla de Supabase para beneficiarios
            Dirección = st.text_input("Dirección del Beneficiario", value=valores_iniciales["Dirección"])

        st.markdown("#### Requerimientos Médicos")
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        # Calcula el índice para el selectbox
        try:
            sangre_index = sangre_options.index(valores_iniciales["Tipo de Sangre"])
        except ValueError:
            sangre_index = 0 # Si el valor de la DB no es válido, selecciona el primero
        
        Tipo_de_Sangre = st.selectbox("Tipo de Sangre Requerido", sangre_options, index=sangre_index)

        st.write("---")
        guardar_button = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar_button:
            datos_a_guardar = {
                "NombreB": NombreB, "mail": mail, "Teléfono": Teléfono, "Dirección": Dirección,
                "Tipo de Sangre": Tipo_de_Sangre,
            }
            if perfil_existente:
                guardar_perfil_beneficiario_supabase(datos_a_guardar, actualizar=True, beneficiario_mail=mail)
            else:
                guardar_perfil_beneficiario_supabase(datos_a_guardar)

def beneficiario_crear_campana():
    st.markdown("<h2 style='color: #4682B4;'>Crea tu Campaña de Donación ✨</h2>", unsafe_allow_html=True)
    st.write("Genera una nueva solicitud para donación de sangre. Sé claro y conciso para atraer a los donantes.")

    beneficiario_id_logueado = st.session_state.get('user_db_id')
    
    if not beneficiario_id_logueado:
        st.warning("⚠️ No se pudo obtener tu ID de Beneficiario. Por favor, asegúrate de haber completado tu perfil en la sección 'Perfil' para que tu ID sea guardado.")
        st.info("El ID de Beneficiario es necesario para asociar la campaña a ti. Si recién creaste tu perfil, cierra sesión y vuelve a iniciarla.")
        return

    with st.form("crear_campana_form"):
        st.markdown("#### Detalles de la Campaña")
        nombre_campana = st.text_input("Nombre de la Campaña", max_chars=100, help="Un título claro para tu solicitud.")
        descripcion_campana = st.text_area("Descripción de la Campaña", max_chars=500, help="Detalla por qué necesitas la donación y qué esperas.")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_sangre_requerida = st.selectbox("Tipo de Sangre Requerida", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], help="El tipo de sangre que necesitas.")
        with col2:
            fecha_limite = st.date_input("Fecha Límite para Donaciones", min_value=datetime.today().date(), help="Fecha hasta la cual se aceptan donaciones.") 
        
        hospital_id = st.number_input("ID del Hospital (donde se donará)", min_value=1, value=1, help="Ingresa el ID del hospital donde se realizará la donación.") 

        st.write("---")
        crear_campana_button = st.form_submit_button("🚀 Crear Campaña")

        if crear_campana_button:
            if not nombre_campana or not descripcion_campana:
                st.error("❌ Por favor, completa el nombre y la descripción de la campaña.")
                return

            datos_campana = {
                "ID_Hospital": hospital_id,
                "Nombre_Campaña": nombre_campana,
                "Descripcion_Campaña": descripcion_campana,
                "Tipo_Sangre_Requerida": tipo_sangre_requerida,
                "Fecha_Limite": fecha_limite.strftime("%Y-%m-%d"),
                "ID_Beneficiario": beneficiario_id_logueado
            }
            crear_campana_supabase(datos_campana)

def beneficiario_historial_donaciones():
    st.markdown("<h2 style='color: #4682B4;'>Historial de Donaciones Recibidas 📊</h2>", unsafe_allow_html=True)
    st.info("Aquí podrás ver un registro de las donaciones que has recibido a través de las campañas.")
    st.markdown("<p><i>Esta sección se desarrollará en futuras actualizaciones.</i></p>", unsafe_allow_html=True)

# --- Lógica principal de la página del Beneficiario ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Beneficiario':
        st.sidebar.title("Navegación Beneficiario 🎯")
        menu = ["Perfil", "Crear Campaña", "Historial de Donaciones"]
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            beneficiario_perfil()
        elif opcion == "Crear Campaña":
            beneficiario_crear_campana()
        elif opcion == "Historial de Donaciones":
            beneficiario_historial_donaciones()
    else:
        st.warning("⚠️ Debes iniciar sesión como **Beneficiario** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()