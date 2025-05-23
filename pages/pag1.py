# pages/donante1.py
import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import folium # ¡Importado de nuevo!
from streamlit_folium import st_folium # ¡Importado de nuevo!

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
def obtener_datos_donante(donante_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del donante.")
        return None
    try:
        response = supabase_client.table("donante").select("*").eq("mail", donante_email).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del donante: {e}")
        return None

# --- Función para actualizar datos del donante ---
def actualizar_datos_donante(donante_email, datos):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del donante.")
        return False
    try:
        response = supabase_client.table("donante").update(datos).eq("mail", donante_email).execute()
        if response.data:
            return True
        else:
            st.error(f"Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error inesperado al actualizar datos: {e}")
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
    donante_id_logueado = st.session_state.get('user_db_id')

    perfil_existente = obtener_datos_donante(email_usuario_logueado)

    valores_iniciales = {
        "Nombre_Apellido": "", "mail": email_usuario_logueado, "telefono": "", "direccion": "",
        "Edad": 18, "sexo": "Masculino", "Tipo_sangre": "A+",
        "Antecedentes": "", "Medicaciones": "", "Tiene_tatuajes": False, "Ultima_donacion": None
    }
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('Nombre_Apellido', 'N/A')}**")
        valores_iniciales["Nombre_Apellido"] = perfil_existente.get("Nombre_Apellido", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["Edad"] = perfil_existente.get("Edad", 18)
        
        sexo_opciones = ["Masculino", "Femenino", "Otro"]
        if perfil_existente.get("sexo") in sexo_opciones:
            valores_iniciales["sexo"] = perfil_existente.get("sexo")

        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("Tipo_sangre") in sangre_opciones:
            valores_iniciales["Tipo_sangre"] = perfil_existente.get("Tipo_sangre")
        
        valores_iniciales["Antecedentes"] = perfil_existente.get("Antecedentes", "")
        valores_iniciales["Medicaciones"] = perfil_existente.get("Medicaciones", "")
        valores_iniciales["Tiene_tatuajes"] = perfil_existente.get("Tiene_tatuajes", False)
        valores_iniciales["Ultima_donacion"] = perfil_existente.get("Ultima_donacion", None)


    with st.form("perfil_form"):
        st.markdown("#### Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            nombre_apellido = st.text_input("Nombre y Apellido", value=valores_iniciales["Nombre_Apellido"])
            mail = st.text_input("Mail Personal", value=valores_iniciales["mail"], disabled=True)
            telefono = st.text_input("Teléfono", value=valores_iniciales["telefono"])
        with col2:
            direccion = st.text_input("Dirección", value=valores_iniciales["direccion"])
            edad = st.number_input("Edad", min_value=18, max_value=100, step=1, value=valores_iniciales["Edad"])
            
            sexo_options = ["Masculino", "Femenino", "Otro"]
            sexo_index = sexo_options.index(valores_iniciales["sexo"]) if valores_iniciales["sexo"] in sexo_options else 0
            sexo = st.selectbox("Sexo", sexo_options, index=sexo_index)

        st.markdown("#### Información Médica")
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        sangre_index = sangre_options.index(valores_iniciales["Tipo_sangre"]) if valores_iniciales["Tipo_sangre"] in sangre_options else 0
        tipo_de_sangre = st.selectbox("Tipo de Sangre", sangre_options, index=sangre_index)

        antecedentes = st.text_area("Antecedentes Médicos (ej. alergias, cirugías previas)", value=valores_iniciales["Antecedentes"])
        medicaciones = st.text_area("Medicaciones Actuales (ej. medicamentos que tomas)", value=valores_iniciales["Medicaciones"])
        tiene_tatuajes = st.checkbox("¿Tienes tatuajes o perforaciones?", value=valores_iniciales["Tiene_tatuajes"])
        
        ultima_donacion_val = None
        if valores_iniciales["Ultima_donacion"]:
            try:
                ultima_donacion_val = datetime.strptime(str(valores_iniciales["Ultima_donacion"]).split("T")[0], "%Y-%m-%d").date()
            except ValueError:
                ultima_donacion_val = None
        
        ultima_donacion_date_input = st.date_input("Fecha de Última Donación", value=ultima_donacion_val if ultima_donacion_val else datetime.today().date())

        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "Nombre_Apellido": nombre_apellido, "mail": mail, "telefono": telefono, "direccion": direccion,
                "Edad": edad, "sexo": sexo, "Tipo_sangre": tipo_de_sangre,
                "Antecedentes": antecedentes, "Medicaciones": medicaciones,
                "Tiene_tatuajes": tiene_tatuajes, "Ultima_donacion": ultima_donacion_date_input.isoformat()
            }
            if perfil_existente:
                actualizar_datos_donante(mail, datos_a_guardar)
            else:
                guardar_perfil_supabase(datos_a_guardar, actualizar=False)

# --- Funciones de Campañas y Hospitales (Hospitales con mapa) ---
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

# FUNCIÓN PARA MOSTRAR MAPA DE HOSPITALES (RE-HABILITADA)
def donante_hospitales():
    st.markdown("<h2 style='color: #B22222;'>Hospitales Asociados Cerca de Ti 🏥</h2>", unsafe_allow_html=True)
    st.write("Explora los hospitales de nuestra red. Puedes moverte por el mapa y hacer zoom para ver detalles.")

    # --- DATOS DE HOSPITALES DE EJEMPLO ---
    # Para que esto funcione con tus datos reales, tu tabla 'hospital' en Supabase
    # DEBERÍA tener columnas como 'nombre', 'latitud', 'longitud'.
    # Si las tienes, puedes reemplazarlas con una consulta a Supabase.
    
    # Ejemplo de hospitales en Buenos Aires
    hospitales = [
        {"nombre": "Hospital General de Agudos Dr. Juan A. Fernández", "lat": -34.5828, "lon": -58.4064},
        {"nombre": "Hospital Alemán", "lat": -34.5937, "lon": -58.4035},
        {"nombre": "Hospital Británico de Buenos Aires", "lat": -34.6212, "lon": -58.3972},
        {"nombre": "Hospital Italiano de Buenos Aires", "lat": -34.6062, "lon": -58.4239},
        {"nombre": "Hospital de Clínicas José de San Martín", "lat": -34.5997, "lon": -58.3965},
        {"nombre": "Hospital Universitario Austral", "lat": -34.4690, "lon": -58.8953}, # Pilar (ejemplo más lejano)
    ]

    # Coordenadas iniciales del mapa (Muñiz, Buenos Aires)
    initial_coords = [-34.5300, -58.7000] # Aproximadamente Muñiz/San Miguel, Buenos Aires

    # Crear el objeto mapa de Folium
    m = folium.Map(location=initial_coords, zoom_start=12)

    # Añadir marcadores para cada hospital
    for h in hospitales:
        folium.Marker(
            location=[h["lat"], h["lon"]],
            popup=f"<b>{h['nombre']}</b><br>Haz clic para más info.",
            tooltip=h["nombre"],
            icon=folium.Icon(color="red", icon="hospital", prefix="fa")
        ).add_to(m)

    # Mostrar el mapa en Streamlit
    st_folium(m, width=700, height=500)

    st.markdown("---")
    st.info("💡 **Consejo:** Para una lista completa y más precisa, deberías cargar los hospitales desde tu base de datos de Supabase, incluyendo sus coordenadas de latitud y longitud.")
    st.markdown("Para futuras mejoras, podemos agregar un buscador de hospitales por ubicación, o filtrar por tipo de sangre.")

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