# pages/donante1.py
import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime # Necesario para fechas de campañas

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, configúralas para que la conexión a la base de datos funcione.")
    supabase_client: Client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
        supabase_client: Client = None

# --- Función para obtener datos del donante ---
def obtener_datos_donante(donante_email): # Cambiado a email como identificador
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del donante.")
        return None
    try:
        response = supabase_client.table("donante").select("*").eq("mail", donante_email).execute() # Buscar por mail
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del donante: {e}")
        return None

# --- Función para actualizar datos del donante ---
def actualizar_datos_donante(donante_email, datos): # Cambiado a email como identificador
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del donante.")
        return False
    try:
        response = supabase_client.table("donante").update(datos).eq("mail", donante_email).execute() # Actualizar por mail
        if response.data:
            st.success("✅ ¡Perfil actualizado con éxito!")
            time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
            st.rerun() # Recargar la página para mostrar los datos actualizados
            return True
        else:
            st.error(f"❌ Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False

# --- Funciones de Campañas (sin cambios) ---
def obtener_campanas_activas():
    if supabase_client:
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            response = supabase_client.table("campaña").select("*").gte("Fecha_Limite", hoy).order("Fecha_Limite", desc=False).execute()
            if response.data:
                return response.data
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas desde Supabase: {e}")
            return []
    return []

def inscribirse_campana(campana_id: int, donante_id: int):
    if supabase_client:
        try:
            existing_inscription = supabase_client.table("inscripciones_campana").select("*").eq("ID_Campaña", campana_id).eq("ID_Donante", donante_id).execute()
            if existing_inscription.data:
                st.warning("⚠️ Ya estás inscrito en esta campaña.")
                return False

            data, count = supabase_client.table("inscripciones_campana").insert({
                "ID_Campaña": campana_id,
                "ID_Donante": donante_id,
                "Fecha_Inscripcion": datetime.now().strftime("%Y-%m-%d")
            }).execute()
            if data and len(data) > 0:
                st.success(f"🎉 ¡Te has inscrito exitosamente a la campaña {campana_id}!")
                return True
            else:
                st.error("❌ No se pudo completar la inscripción.")
                return False
        except Exception as e:
            st.error(f"❌ Error al inscribirse en la campaña: {e}")
            return False
    return False

# --- Definición de las funciones de sección ---
def donante_perfil():
    st.markdown("<h2 style='color: #B22222;'>Mi Perfil de Donante 📝</h2>", unsafe_allow_html=True)
    st.write("Actualiza y gestiona tu información personal para ayudarnos a conectar mejor con quienes te necesitan.")

    email_usuario_logueado = st.session_state.get('user_email', 'donante@ejemplo.com')
    donante_id_logueado = st.session_state.get('user_db_id') # ID de la DB si lo obtuvimos

    perfil_existente = obtener_datos_donante(email_usuario_logueado) # Usar la función actualizada

    valores_iniciales = {
        "nombred": "", "mail": email_usuario_logueado, "telefono": "", "direccion": "",
        "edad": 18, "sexo": "Masculino", "tipo_de_sangre": "A+",
        "antecedentes": "", "medicaciones": "", "cumple_requisitos": False, "ultimadonacion": None # <-- CORRECCIÓN AQUÍ
    }
    
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombred', 'N/A')}**")
        valores_iniciales["nombred"] = perfil_existente.get("nombred", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["edad"] = perfil_existente.get("edad", 18)
        
        sexo_opciones = ["Masculino", "Femenino", "Otro"]
        if perfil_existente.get("sexo") in sexo_opciones:
            valores_iniciales["sexo"] = perfil_existente.get("sexo")

        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("tipo_de_sangre") in sangre_opciones:
            valores_iniciales["tipo_de_sangre"] = perfil_existente.get("tipo_de_sangre")
        
        valores_iniciales["antecedentes"] = perfil_existente.get("antecedentes", "")
        valores_iniciales["medicaciones"] = perfil_existente.get("medicaciones", "")
        valores_iniciales["cumple_requisitos"] = perfil_existente.get("cumple_requisitos", False)
        valores_iniciales["ultimadonacion"] = perfil_existente.get("ultimadonacion", None) # <-- CORRECCIÓN AQUÍ


    with st.form("perfil_form"):
        st.markdown("#### Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre y Apellido", value=valores_iniciales["nombred"])
            mail = st.text_input("Mail Personal", value=valores_iniciales["mail"], disabled=True)
            telefono = st.text_input("Teléfono", value=valores_iniciales["telefono"])
        with col2:
            direccion = st.text_input("Dirección", value=valores_iniciales["direccion"])
            edad = st.number_input("Edad", min_value=18, max_value=100, step=1, value=valores_iniciales["edad"])
            
            sexo_options = ["Masculino", "Femenino", "Otro"]
            sexo_index = sexo_options.index(valores_iniciales["sexo"]) if valores_iniciales["sexo"] in sexo_options else 0
            sexo = st.selectbox("Sexo", sexo_options, index=sexo_index)

        st.markdown("#### Información Médica")
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        sangre_index = sangre_options.index(valores_iniciales["tipo_de_sangre"]) if valores_iniciales["tipo_de_sangre"] in sangre_options else 0
        tipo_de_sangre = st.selectbox("Tipo de Sangre", sangre_options, index=sangre_index)

        antecedentes = st.text_area("Antecedentes Médicos (ej. alergias, cirugías previas)", value=valores_iniciales["antecedentes"])
        medicaciones = st.text_area("Medicaciones Actuales (ej. medicamentos que tomas)", value=valores_iniciales["medicaciones"])
        
        cumple_requisitos_cb = st.checkbox("¿Cumples con los requisitos generales para donar sangre?", value=valores_iniciales["cumple_requisitos"])
        
        # Manejo de la fecha de última donación
        ultima_donacion_val = None
        if valores_iniciales["ultimadonacion"]: # <-- CORRECCIÓN AQUÍ
            try:
                ultima_donacion_val = datetime.strptime(str(valores_iniciales["ultimadonacion"]).split("T")[0], "%Y-%m-%d").date() # <-- CORRECCIÓN AQUÍ
            except ValueError:
                ultima_donacion_val = None # Si el formato no es válido, no precargar
        
        ultima_donacion_date_input = st.date_input("Fecha de Última Donación", value=ultima_donacion_val if ultima_donacion_val else datetime.today().date())

        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "nombred": nombre, "mail": mail, "telefono": telefono, "direccion": direccion,
                "edad": edad, "sexo": sexo, "tipo_de_sangre": tipo_de_sangre,
                "antecedentes": antecedentes, "medicaciones": medicaciones,
                "cumple_requisitos": cumple_requisitos_cb,
                "ultimadonacion": ultima_donacion_date_input.isoformat() # <-- CORRECCIÓN AQUÍ
            }
            if perfil_existente:
                actualizar_datos_donante(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de donante aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el donante ya exista en la base de datos para poder actualizar su perfil.")


# --- Funciones de Campañas y Hospitales (Hospitales sin mapa) ---
def donante_campanas():
    st.markdown("<h2 style='color: #B22222;'>Campañas de Donación Disponibles ❤️</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes explorar las solicitudes de donación de sangre y ofrecer tu ayuda.")

    campanas = obtener_campanas_activas()
    donante_id_logueado = st.session_state.get('user_db_id')

    if not donante_id_logueado:
        st.warning("⚠️ Para inscribirte a campañas, asegúrate de que tu perfil de donante esté completo y tenga un ID válido. Completa el formulario de 'Perfil'.")

    if campanas:
        for campana in campanas:
            with st.expander(f"Campaña: {campana.get('Nombre_Campaña', 'Sin Nombre')} (Sangre: {campana.get('Tipo_Sangre_Requerida', 'N/A')})"):
                st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                st.write(f"**Fecha Límite:** {campana.get('Fecha_Limite', 'N/A')}")
                st.write(f"**ID de Campaña:** {campana.get('ID_Campaña', 'N/A')}")
                
                if donante_id_logueado:
                    if st.button(f"✨ Inscribirme a esta Campaña", key=f"inscribir_{campana.get('ID_Campaña')}"):
                        if inscribirse_campana(campana.get("ID_Campaña"), donante_id_logueado):
                            st.balloons()
                        else:
                            st.error("Fallo la inscripción.")
                else:
                    st.info("Inicia sesión y completa tu perfil para poder inscribirte.")
            st.markdown("---")
    else:
        st.info("ℹ️ No hay campañas de donación activas en este momento. ¡Vuelve pronto!")

def donante_hospitales():
    st.markdown("<h2 style='color: #B22222;'>Hospitales Asociados 🏥</h2>", unsafe_allow_html=True)
    st.info("Aquí se mostrará la lista de hospitales asociados. La funcionalidad de mapa ha sido temporalmente deshabilitada para evitar errores de instalación.")
    st.write("Puedes contactar a los siguientes hospitales para donar:")
    st.markdown("""
    * **Hospital General de Agudos Dr. Juan A. Fernández**
    * **Hospital Alemán**
    * **Hospital Británico de Buenos Aires**
    * **Hospital Italiano de Buenos Aires**
    * **Hospital de Clínicas José de San Martín**
    """)
    st.markdown("---")
    st.info("💡 **Consejo:** Para futuras mejoras, podemos volver a implementar un mapa interactivo una vez que las dependencias estén estables.")

def donante_requisitos():
    st.markdown("<h2 style='color: #B22222;'>Requisitos para Donar Sangre ✅</h2>", unsafe_allow_html=True)
    st.write("Infórmate sobre los criterios esenciales para ser un donante apto. Tu salud es nuestra prioridad.")
    st.markdown("""
    * **Edad:** Generalmente entre 18 y 65 años (con excepciones).
    * **Peso:** Mínimo de 50 kg.
    * **Salud General:** Sentirse bien y no tener enfermedades graves.
    * **Hemoglobina:** Nivel adecuado de hemoglobina.
    * **No haber donado recientemente:** Esperar el tiempo indicado entre donaciones.
    * **Sin tatuajes o piercings recientes:** Respetar el período de espera.
    * **Sin ciertas medicaciones o antecedentes:** Consultar con el personal médico.
    """)
    st.info("Esta es una lista general. Siempre consulta los requisitos específicos del centro de donación.")


def donante_manual():
    st.markdown("<h2 style='color: #B22222;'>Manual del Donante 📖</h2>", unsafe_allow_html=True)
    st.write("Guía completa para donantes, desde la preparación hasta el cuidado posterior a la donación.")
    st.info("Próximamente: Contenido detallado sobre el proceso de donación.")

def donante_info_donaciones():
    st.markdown("<h2 style='color: #B22222;'>Información sobre Donaciones 💡</h2>", unsafe_allow_html=True)
    st.write("Artículos y recursos útiles sobre la importancia de la donación de sangre y cómo impacta vidas.")
    st.info("Próximamente: Datos, mitos y verdades sobre la donación.")

# --- Lógica principal de la página del Donante ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Donante':
        st.sidebar.title("Navegación Donante 🧭")
        menu = ["Perfil", "Campañas Disponibles", "Información sobre Donaciones", "Hospitales", "Requisitos", "Manual del Donante"]
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            donante_perfil()
        elif opcion == "Campañas Disponibles":
            donante_campanas()
        elif opcion == "Información sobre Donaciones":
            donante_info_donaciones()
        elif opcion == "Hospitales":
            donante_hospitales()
        elif opcion == "Requisitos":
            donante_requisitos()
        elif opcion == "Manual del Donante":
            donante_manual()
    else:
        st.warning("⚠️ Debes iniciar sesión como **Donante** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()