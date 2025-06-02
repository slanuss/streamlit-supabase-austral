import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, confíguralas para que la conexión a la base de datos funcione.")
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
        response = supabase_client.table("donante").select("*, id_donante").eq("mail", donante_email).execute()
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
            st.success("✅ ¡Perfil actualizado con éxito!")
            time.sleep(1)
            st.rerun()
            return True
        else:
            st.error(f"❌ Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False

# --- Funciones de Campañas ---
def obtener_campanas_activas():
    if supabase_client:
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            response = supabase_client.table("campana").select("id_campana, nombre_campana, fecha_inicio, fecha_fin, id_hospital, id_beneficiario, descripcion").order("fecha_fin", desc=False).execute()
            if response.data:
                campanas_filtradas = [
                    c for c in response.data 
                    if c.get('fecha_fin') and datetime.strptime(c['fecha_fin'], "%Y-%m-%d").date() >= datetime.now().date()
                ]
                return campanas_filtradas
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas desde Supabase: {e}")
            return []
    return []

def inscribirse_campana(campana_id: int, donante_id: int):
    if supabase_client:
        try:
            existing_inscription = supabase_client.table("inscripciones_campana").select("*").eq("id_campana", campana_id).eq("id_donante", donante_id).execute()
            if existing_inscription.data:
                st.warning("⚠️ Ya estás inscrito en esta campaña.")
                return False

            data, count = supabase_client.table("inscripciones_campana").insert({
                "id_campana": campana_id,
                "id_donante": donante_id,
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

# NUEVA FUNCIÓN: Obtener conteo de inscripciones por campaña
def obtener_conteo_inscripciones_campana(id_campana):
    if supabase_client is None:
        return 0
    try:
        response = supabase_client.table("inscripciones_campana").select("id_inscripcion", count="exact").eq("id_campana", id_campana).execute()
        if response.count is not None:
            return response.count
        else:
            return 0
    except Exception as e:
        st.error(f"❌ Error al obtener conteo de inscripciones para campaña {id_campana}: {e}")
        return 0

# --- Definición de las funciones de sección ---
def donante_perfil():
    st.markdown("<h2 style='color: #B22222;'>Mi Perfil de Donante 📝</h2>", unsafe_allow_html=True)
    st.write("Actualiza y gestiona tu información personal para ayudarnos a conectar mejor con quienes te necesitan.")

    email_usuario_logueado = st.session_state.get('user_email', 'donante@ejemplo.com')
    donante_id_logueado = st.session_state.get('user_db_id')

    perfil_existente = obtener_datos_donante(email_usuario_logueado)

    valores_iniciales = {
        "nombred": "", "mail": email_usuario_logueado, "telefono": "", "direccion": "",
        "edad": 18, "sexo": "Masculino", "tipo_de_sangre": "A+",
        "antecedentes": "", "medicaciones": "", "cumple_requisitos": False, "dni": ""
    }
    
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombred', 'N/A')}**")
        valores_iniciales["nombred"] = perfil_existente.get("nombred", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["edad"] = perfil_existente.get("edad", 18)
        valores_iniciales["dni"] = perfil_existente.get("dni", "") # Cargar DNI existente
        
        sexo_db = perfil_existente.get("sexo")
        if sexo_db == 'M' or sexo_db == 'Masculino':
            valores_iniciales["sexo"] = "Masculino"
        elif sexo_db == 'F' or sexo_db == 'Femenino':
            valores_iniciales["sexo"] = "Femenino"
        elif sexo_db == 'O' or sexo_db == 'Otro':
            valores_iniciales["sexo"] = "Otro"
        else:
            valores_iniciales["sexo"] = "Masculino"

        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("tipo_de_sangre") in sangre_opciones:
            valores_iniciales["tipo_de_sangre"] = perfil_existente.get("tipo_de_sangre")
        
        valores_iniciales["antecedentes"] = perfil_existente.get("antecedentes", "")
        valores_iniciales["medicaciones"] = perfil_existente.get("medicaciones", "")
        valores_iniciales["cumple_requisitos"] = perfil_existente.get("cumple_requisitos", False)


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
            dni = st.text_input("DNI", value=valores_iniciales["dni"], disabled=True) # DNI no editable por seguridad
            
            sexo_options = ["Masculino", "Femenino", "Otro"]
            sexo_index = sexo_options.index(valores_iniciales["sexo"]) if valores_iniciales["sexo"] in sexo_options else 0
            sexo_seleccionado = st.selectbox("Sexo", sexo_options, index=sexo_index)

        st.markdown("#### Información Médica")
        sangre_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        sangre_index = sangre_options.index(valores_iniciales["tipo_de_sangre"]) if valores_iniciales["tipo_de_sangre"] in sangre_options else 0
        tipo_de_sangre = st.selectbox("Tipo de Sangre", sangre_options, index=sangre_index)

        antecedentes = st.text_area("Antecedentes Médicos (ej. alergias, cirugías previas)", value=valores_iniciales["antecedentes"])
        medicaciones = st.text_area("Medicaciones Actuales (ej. medicamentos que tomas)", value=valores_iniciales["medicaciones"])
        
        cumple_requisitos_cb = st.checkbox("¿Cumples con los requisitos generales para donar sangre?", value=valores_iniciales["cumple_requisitos"])
        
        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "nombred": nombre, "mail": mail, "telefono": telefono, "direccion": direccion,
                "edad": edad, "sexo": sexo_seleccionado, # Guardar la cadena completa
                "tipo_de_sangre": tipo_de_sangre,
                "antecedentes": antecedentes, "medicaciones": medicaciones,
                "cumple_requisitos": cumple_requisitos_cb,
                "dni": dni # Asegurarse de que el DNI se incluya en la actualización si es necesario
            }
            if perfil_existente:
                actualizar_datos_donante(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de donante no se realiza desde aquí.")
                st.info("Por favor, ve a la página principal para 'Crear una Cuenta Nueva' como Donante si aún no tienes una, o 'Inicia Sesión' si ya la tienes y quieres actualizar tu perfil.")


def donante_campanas():
    st.markdown("<h2 style='color: #B22222;'>Campañas de Donación Disponibles ❤️</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes explorar las solicitudes de donación de sangre y ofrecer tu ayuda.")

    campanas = obtener_campanas_activas()
    donante_id_logueado = st.session_state.get('user_db_id')

    if not donante_id_logueado:
        st.warning("⚠️ Para inscribirte a campañas, asegúrate de que tu perfil de donante esté completo y tenga un ID válido. Completa el formulario de 'Perfil'.")

    # Obtener nombres de hospitales para mostrar
    hospitales_data = []
    if supabase_client:
        try:
            response = supabase_client.table("hospital").select("id_hospital, nombre_hospital").execute()
            if response.data:
                hospitales_data = response.data
        except Exception as e:
            st.error(f"Error al obtener la lista de hospitales: {e}")
    hospital_names_map = {h['id_hospital']: h['nombre_hospital'] for h in hospitales_data}


    if campanas:
        for campana in campanas:
            campana_nombre = campana.get('nombre_campana', 'Sin Nombre') 
            campana_id = campana.get('id_campana') 
            hospital_id = campana.get('id_hospital')
            hospital_name = hospital_names_map.get(hospital_id, 'Hospital Desconocido')

            with st.expander(f"Campaña: {campana_nombre} (Hospital: {hospital_name})"):
                st.write(f"**Descripción:** {campana.get('descripcion', 'No disponible')}")
                st.write(f"**Fecha Límite:** {campana.get('fecha_fin', 'N/A')}") 
                st.write(f"**ID de Campaña:** {campana_id if campana_id else 'N/A'}")
                
                conteo_inscripciones = obtener_conteo_inscripciones_campana(campana_id)
                st.write(f"**Personas Inscriptas:** {conteo_inscripciones}")

                if donante_id_logueado and campana_id is not None:
                    if st.button(f"✨ Inscribirme a esta Campaña", key=f"inscribir_{campana_id}"):
                        if inscribirse_campana(campana_id, donante_id_logueado):
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

# NUEVA FUNCIÓN: Mapa de Hospitales
def donante_mapa_hospitales():
    st.markdown("<h2 style='color: #B22222;'>Mapa de Hospitales 🗺️</h2>", unsafe_allow_html=True)
    st.write("Explora la ubicación de los hospitales asociados en el mapa.")

    # Obtener todos los hospitales de la base de datos
    hospitales_data = []
    if supabase_client:
        try:
            # Seleccionar todas las columnas relevantes para el mapa
            response = supabase_client.table("hospital").select("nombre_hospital, direccion, latitud, longitud").execute()
            if response.data:
                hospitales_data = response.data
        except Exception as e:
            st.error(f"Error al obtener datos de hospitales para el mapa: {e}")
            st.warning("Asegúrate de que las columnas 'latitud' y 'longitud' existan en tu tabla 'hospital' si quieres usar coordenadas exactas.")

    # Si no tienes latitud/longitud en tu DB, puedes usar un mapeo manual o geocodificación
    # Para este ejemplo, si no hay coordenadas en la DB, usaremos algunas predefinidas
    # Si tus hospitales tienen latitud y longitud en la DB, asegúrate de que esas columnas existan.
    # Si no existen, deberías añadirlas a tu esquema de DB y llenarlas.
    # Por ahora, usaremos un mapeo manual para los hospitales de ejemplo.
    
    # Coordenadas de ejemplo para los hospitales que tienes en tus datos de inserción
    # Estas son aproximadas y deben ser reemplazadas por coordenadas reales de tus hospitales
    hospital_coords = {
        'Hospital Central': {'lat': -34.6037, 'lng': -58.3816}, # Buenos Aires, Argentina (ejemplo)
        'Hospital Regional': {'lat': -34.9213, 'lng': -57.9544}, # La Plata, Argentina (ejemplo)
        'Hospital Comunitario': {'lat': -34.5833, 'lng': -58.4167} # Palermo, Buenos Aires (ejemplo)
    }

    markers_js = []
    for hosp in hospitales_data:
        name = hosp.get('nombre_hospital', 'Hospital Desconocido')
        address = hosp.get('direccion', 'Dirección Desconocida')
        lat = hosp.get('latitud')
        lng = hosp.get('longitud')

        # Usar coordenadas de la DB si existen, si no, usar las de ejemplo
        if lat is None or lng is None:
            coords = hospital_coords.get(name, {'lat': -34.6037, 'lng': -58.3816}) # Default a Hospital Central si no se encuentra
            lat = coords['lat']
            lng = coords['lng']

        markers_js.append(f"""
            new google.maps.Marker({{
                position: {{lat: {lat}, lng: {lng}}},
                map: map,
                title: '{name}',
                label: '{name[0]}', // Primera letra como etiqueta
            }});
        """)

    # UNE los marcadores en una cadena JavaScript
    markers_js_string = "\n".join(markers_js)

    # TU CLAVE DE API DE GOOGLE MAPS VA AQUÍ
    # Obtén tu clave de API en Google Cloud Console.
    # Es recomendable guardarla en un archivo .env y accederla como os.environ.get("GOOGLE_MAPS_API_KEY")
    google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY") # <-- ¡COLOCA TU CLAVE DE API AQUÍ!

    if not google_maps_api_key:
        st.warning("⚠️ No se encontró la clave de API de Google Maps. El mapa no se mostrará correctamente.")
        st.info("Por favor, obtén una clave de API de Google Maps y configúrala como una variable de entorno 'GOOGLE_MAPS_API_KEY' en tu archivo .env.")
        return

    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mapa de Hospitales</title>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
        <meta charset="utf-8">
        <style>
            #map {{
                height: 500px;
                width: 100%;
                border-radius: 8px; /* Bordes redondeados */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra */
            }}
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f0f2f6;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            function initMap() {{
                const center = {{ lat: -34.6037, lng: -58.3816 }}; // Centro de Buenos Aires
                const map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 10,
                    center: center,
                    mapTypeControl: false,
                    streetViewControl: false,
                    fullscreenControl: false,
                }});

                {markers_js_string}
            }}
        </script>
        <script async defer src="https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}&callback=initMap"></script>
    </body>
    </html>
    """
    st.components.v1.html(map_html, height=550)


# --- Función principal de la página de Donante ---
def donante_perfil_page():
    st.title("💖 Panel de Donante")
    st.markdown("---")

    # Verifica si el usuario está logueado como Donante
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'Donante':
        st.warning("Debes iniciar sesión como Donante para acceder a esta página.")
        st.stop() # Detiene la ejecución de la página

    # Crea las pestañas para el donante (AÑADIDA PESTAÑA DE MAPA)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mi Perfil", "Campañas Activas", "Hospitales", "Requisitos", "Mapa de Hospitales"])

    with tab1:
        donante_perfil()
    with tab2:
        donante_campanas()
    with tab3:
        donante_hospitales()
    with tab4:
        donante_requisitos()
    with tab5: # NUEVA PESTAÑA
        donante_mapa_hospitales() # Llamada a la nueva función del mapa

if __name__ == "__main__":
    # Si este archivo se ejecuta directamente, llama a la función de la página del donante
    donante_perfil_page()
