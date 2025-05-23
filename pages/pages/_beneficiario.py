# pages/beneficiario.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

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
    """
    Guarda o actualiza los datos del perfil del beneficiario en la base de datos Supabase.
    :param datos_beneficiario: Diccionario con los datos del beneficiario.
    :param actualizar: Booleano, si es True, intenta actualizar un registro existente.
    :param beneficiario_mail: El mail del beneficiario para saber qué registro actualizar.
    """
    if supabase_client:
        try:
            if actualizar and beneficiario_mail:
                # Intenta actualizar el registro existente
                data, count = supabase_client.table("beneficiario").update(datos_beneficiario).eq("mail_beneficiario", beneficiario_mail).execute()
                if data and len(data) > 0:
                    st.success("Perfil de beneficiario actualizado en Supabase!")
                    return True
                else:
                    st.warning("No se encontró el perfil para actualizar o no hubo cambios.")
                    return False
            else:
                # Intenta insertar un nuevo registro
                data, count = supabase_client.table("beneficiario").insert(datos_beneficiario).execute()
                if data and len(data) > 0:
                    st.success("Perfil de beneficiario guardado en Supabase!")
                    return True
                else:
                    st.error("Error al guardar el perfil del beneficiario en Supabase. No se insertaron registros.")
                    return False
        except Exception as e:
            st.error(f"Error de conexión, inserción o actualización en Supabase (beneficiario): {e}")
            return False
    else:
        st.warning("No se pudo conectar a Supabase para guardar/actualizar el perfil del beneficiario. Revisa tus variables .env.")
        return False

def obtener_perfil_beneficiario(email_beneficiario: str):
    """
    Obtiene los datos del perfil de un beneficiario desde Supabase usando su correo electrónico.
    """
    if supabase_client:
        try:
            # Asumo que la columna de email en tu tabla beneficiario se llama 'mail_beneficiario'
            response = supabase_client.table("beneficiario").select("*").eq("mail_beneficiario", email_beneficiario).limit(1).execute()
            if response.data:
                return response.data[0] # Retorna el primer (y único) registro encontrado
            else:
                return None # No se encontró el beneficiario
        except Exception as e:
            st.error(f"Error al obtener perfil del beneficiario desde Supabase: {e}")
            return None
    return None

# --- Secciones de la página del Beneficiario ---
def beneficiario_perfil():
    st.header("Perfil del Beneficiario")
    st.info("Este es el formulario del perfil del Beneficiario. **AVISO: Los campos de este formulario son EJEMPLOS.** Por favor, proporcióna la estructura de tu tabla 'beneficiario' en Supabase para adaptar los campos correctamente.")

    # Obtener el mail del usuario logueado.
    email_usuario_logueado = st.session_state.get('username', 'beneficiario@ejemplo.com')
    if email_usuario_logueado == "beneficiario": # Si el usuario es "beneficiario", usamos un email de ejemplo
        email_usuario_logueado = "beneficiario@ejemplo.com"

    perfil_existente = obtener_perfil_beneficiario(email_usuario_logueado)

    # Inicializa los valores para los campos del formulario con ejemplos
    valores_iniciales = {
        "nombre_completo": "",
        "mail_beneficiario": email_usuario_logueado,
        "telefono_contacto": "",
        "direccion_beneficiario": "",
        "tipo_sangre_requerido": "O+",
        "condicion_medica": "",
        "urgencia_donacion": "Baja",
        "permite_contacto": False,
    }

    # Si encontramos un perfil existente, actualizamos los valores iniciales
    if perfil_existente:
        st.info(f"Cargando datos de perfil para: {perfil_existente.get('nombre_completo', 'N/A')}")
        valores_iniciales["nombre_completo"] = perfil_existente.get("nombre_completo", "")
        valores_iniciales["mail_beneficiario"] = perfil_existente.get("mail_beneficiario", email_usuario_logueado)
        valores_iniciales["telefono_contacto"] = perfil_existente.get("telefono_contacto", "")
        valores_iniciales["direccion_beneficiario"] = perfil_existente.get("direccion_beneficiario", "")
        
        if perfil_existente.get("tipo_sangre_requerido") in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            valores_iniciales["tipo_sangre_requerido"] = perfil_existente.get("tipo_sangre_requerido")
        
        valores_iniciales["condicion_medica"] = perfil_existente.get("condicion_medica", "")
        
        if perfil_existente.get("urgencia_donacion") in ["Baja", "Media", "Alta"]:
            valores_iniciales["urgencia_donacion"] = perfil_existente.get("urgencia_donacion")
        
        valores_iniciales["permite_contacto"] = perfil_existente.get("permite_contacto", False)


    with st.form("perfil_beneficiario_form"):
        # Campos del formulario de ejemplo - ADAPTAR SEGÚN TU TABLA DE SUPABASE
        nombre_completo = st.text_input("Nombre y Apellido del Beneficiario", value=valores_iniciales["nombre_completo"])
        mail_beneficiario = st.text_input("Mail de Contacto", value=valores_iniciales["mail_beneficiario"], disabled=True)
        telefono_contacto = st.text_input("Teléfono de Contacto", value=valores_iniciales["telefono_contacto"])
        direccion_beneficiario = st.text_input("Dirección del Beneficiario", value=valores_iniciales["direccion_beneficiario"])

        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        sangre_index = sangre_options.index(valores_iniciales["tipo_sangre_requerido"]) if valores_iniciales["tipo_sangre_requerido"] in sangre_options else 0
        tipo_sangre_requerido = st.selectbox("Tipo de Sangre Requerido", sangre_options, index=sangre_index)

        condicion_medica = st.text_area("Enfermedad/Condición Médica", value=valores_iniciales["condicion_medica"])
        
        urgencia_options = ["Baja", "Media", "Alta"]
        urgencia_index = urgencia_options.index(valores_iniciales["urgencia_donacion"]) if valores_iniciales["urgencia_donacion"] in urgencia_options else 0
        urgencia_donacion = st.selectbox("Nivel de Urgencia de Donación", urgencia_options, index=urgencia_index)
        
        permite_contacto = st.checkbox("Permito que los donantes me contacten (si aplica)", value=valores_iniciales["permite_contacto"])
        
        guardar_button = st.form_submit_button("Guardar Perfil" if not perfil_existente else "Actualizar Perfil")

        if guardar_button:
            # Construye el diccionario con los datos del formulario para guardar/actualizar
            datos_a_guardar = {
                "nombre_completo": nombre_completo,
                "mail_beneficiario": mail_beneficiario, # Usamos el mail (deshabilitado) como identificador
                "telefono_contacto": telefono_contacto,
                "direccion_beneficiario": direccion_beneficiario,
                "tipo_sangre_requerido": tipo_sangre_requerido,
                "condicion_medica": condicion_medica,
                "urgencia_donacion": urgencia_donacion,
                "permite_contacto": permite_contacto,
            }
            if perfil_existente:
                guardar_perfil_beneficiario_supabase(datos_a_guardar, actualizar=True, beneficiario_mail=mail_beneficiario)
            else:
                guardar_perfil_beneficiario_supabase(datos_a_guardar)


def beneficiario_campanas_solicitud():
    st.header("Solicitud de Campañas de Donación")
    st.info("Aquí el beneficiario podrá crear o gestionar solicitudes de campañas de donación. Esto se relacionará con la sección 'Campañas Disponibles' del donante.")

def beneficiario_historial_donaciones():
    st.header("Historial de Donaciones Recibidas")
    st.info("Aquí se mostrará el historial de donaciones que el beneficiario ha recibido.")


# --- Lógica principal de la página del Beneficiario ---
# Este bloque se ejecuta cuando Streamlit carga este archivo como una página principal.
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Beneficiario':
        st.sidebar.title("Navegación Beneficiario")
        menu = ["Perfil", "Solicitud de Campañas", "Historial de Donaciones"]
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            beneficiario_perfil()
        elif opcion == "Solicitud de Campañas":
            beneficiario_campanas_solicitud()
        elif opcion == "Historial de Donaciones":
            beneficiario_historial_donaciones()
    else:
        st.warning("Debes iniciar sesión como Beneficiario para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()