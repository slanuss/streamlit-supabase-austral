# pages/donante1.py
import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime # Necesario para fechas de campañas, pero no para ultima_donacion si la eliminamos

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
            # Captura el error de Supabase para depuración
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
        "antecedentes": "", "medicaciones": "", "cumple_requisitos": False # <-- ELIMINADO: ultimadonacion
    }
    
    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombred', 'N/A')}**")
        valores_iniciales["nombred"] = perfil_existente.get("nombred", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["edad"] = perfil_existente.get("edad", 18)
        
        sexo_opciones = ["Masculino", "Femenino", "Otro"]
        # Asegurarse de que el valor inicial para sexo sea compatible
        if perfil_existente.get("sexo") and perfil_existente.get("sexo") in sexo_opciones:
            valores_iniciales["sexo"] = perfil_existente.get("sexo")
        # Si sexo es solo 'M' o 'F' en la DB, ajusta la lógica aquí
        elif perfil_existente.get("sexo") == 'M':
            valores_iniciales["sexo"] = "Masculino"
        elif perfil_existente.get("sexo") == 'F':
            valores_iniciales["sexo"] = "Femenino"


        sangre_opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if perfil_existente.get("tipo_de_sangre") in sangre_opciones:
            valores_iniciales["tipo_de_sangre"] = perfil_existente.get("tipo_de_sangre")
        
        valores_iniciales["antecedentes"] = perfil_existente.get("antecedentes", "")
        valores_iniciales["medicaciones"] = perfil_existente.get("medicaciones", "")
        valores_iniciales["cumple_requisitos"] = perfil_existente.get("cumple_requisitos", False)
        # <-- ELIMINADO: valores_iniciales["ultimadonacion"]


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
        
        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "nombred": nombre, "mail": mail, "telefono": telefono, "direccion": direccion,
                "edad": edad, "sexo": sexo, "tipo_de_sangre": tipo_de_sangre,
                "antecedentes": antecedentes, "medicaciones": medicaciones,
                "cumple_requisitos": cumple_requisitos_cb,
                # <-- ELIMINADO: "ultimadonacion": ultima_donacion_date_input.isoformat()
            }
            # *** Debugging para ver los datos antes de enviar ***
            st.write("Datos a guardar:", datos_a_guardar)
            # ***************************************************
            if perfil_existente:
                actualizar_datos_donante(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de donante aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el donante ya exista en la base de datos para poder actualizar su perfil.")


# --- Funciones de Campañas y Hospitales (sin cambios) ---
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



def donante_info_donaciones():
    st.markdown("<h2 style='color: #B22222;'>Información sobre Donaciones 💡</h2>", unsafe_allow_html=True)
    st.write("Explora estos recursos para entender la importancia de tu donación y cómo impacta vidas.")

    st.markdown("---") # Separador visual

    # Sección 1: ¿Por qué es importante donar sangre?
    st.markdown("### ¿Por qué tu Donación Salva Vidas? ❤️")
    st.write("""
    Donar sangre es un acto altruista que tiene un impacto directo y vital en la vida de muchas personas. Cada donación puede salvar hasta tres vidas. La sangre y sus componentes son esenciales para:
    * **Pacientes con cáncer:** Muchos tratamientos de quimioterapia afectan la producción de células sanguíneas.
    * **Cirugías y trasplantes:** Se requieren grandes cantidades de sangre durante y después de procedimientos complejos.
    * **Accidentes y emergencias:** Las víctimas de accidentes a menudo necesitan transfusiones urgentes.
    * **Enfermedades crónicas:** Pacientes con anemia severa, talasemia, o hemofilia necesitan transfusiones regulares.
    * **Madres durante el parto:** Las hemorragias postparto son una causa importante de mortalidad materna.
    """)
    st.info("¡Tu contribución es invaluable y marca una diferencia real!")

    st.markdown("---") # Separador visual

    # Sección 2: El proceso de donación (breve descripción)
    st.markdown("### El Proceso de Donación: ¿Qué Esperar? 🩸")
    st.write("""
    Donar sangre es un proceso seguro y rápido que generalmente toma entre 45 minutos y 1 hora, incluyendo el registro y el descanso post-donación.
    1.  **Registro:** Se te pedirá una identificación y se revisarán tus datos.
    2.  **Cuestionario de Salud:** Se te hará un cuestionario confidencial para asegurar que eres apto para donar.
    3.  **Chequeo Médico:** Un profesional de la salud tomará tu presión arterial, pulso y temperatura, y medirá tus niveles de hemoglobina.
    4.  **Donación:** La extracción de sangre en sí dura solo de 8 a 10 minutos.
    5.  **Descanso y Refrigerio:** Se te ofrecerá un refrigerio y se te pedirá que descanses unos minutos antes de irte.
    """)
    st.success("¡Prepárate para sentirte bien después de hacer el bien!")

    st.markdown("---") # Separador visual

    # Sección 3: Mitos y verdades
    st.markdown("### Mitos y Verdades sobre la Donación 🤔")
    st.write("Despejamos algunas dudas comunes sobre la donación de sangre:")
    st.markdown("""
    * **Mito:** Donar sangre debilita.
        * **Verdad:** Tu cuerpo repone el volumen de sangre en pocas horas y los glóbulos rojos en pocas semanas. No te sentirás débil si sigues las recomendaciones.
    * **Mito:** Puedo contraer enfermedades al donar.
        * **Verdad:** Todo el material utilizado es estéril, de un solo uso y desechable. No hay riesgo de contraer enfermedades.
    * **Mito:** Hay que estar en ayunas para donar.
        * **Verdad:** ¡No! De hecho, se recomienda haber comido algo ligero y beber muchos líquidos antes de donar.
    """)

    st.markdown("---") # Separador visual

    # Sección 4: Consejos para antes y después de donar
    st.markdown("### Consejos para Donantes ✨")
    st.markdown("#### Antes de Donar:")
    st.markdown("""
    * **Hidratación:** Bebe abundante agua y otros líquidos (no alcohólicos) el día antes y el día de la donación.
    * **Alimentación:** Come una comida ligera y nutritiva antes de ir.
    * **Descanso:** Asegúrate de haber dormido bien la noche anterior.
    * **Documentación:** Lleva tu identificación.
    """)
    st.markdown("#### Después de Donar:")
    st.markdown("""
    * **Reposo:** Descansa unos minutos en el centro de donación.
    * **Hidratación:** Continúa bebiendo muchos líquidos en las siguientes 24 horas.
    * **Evita Esfuerzos:** No realices actividades físicas intensas ni levantes objetos pesados durante al menos 24 horas.
    * **Alcohol:** Evita el alcohol y el tabaco por unas horas.
    """)

    st.markdown("---") # Separador visual

    # Sección 5: Preguntas Frecuentes (puedes agregar más aquí)
    st.markdown("### Preguntas Frecuentes (FAQ) ❓")
    st.markdown("""
    * **¿Con qué frecuencia puedo donar sangre?**
        * Generalmente, cada 2 o 3 meses, dependiendo de las regulaciones locales.
    * **¿Mis datos son confidenciales?**
        * Sí, toda tu información es tratada con la máxima confidencialidad.
    * **¿Se me avisará si mi sangre es utilizada?**
        * Algunos centros ofrecen esta notificación; consulta con el personal.
    """)

    st.markdown("<p style='font-size: small; text-align: center; color: gray;'>¡Gracias por tu heroico acto de donación!</p>", unsafe_allow_html=True)

# --- Lógica principal de la página del Donante ---
if __name__ == "__main__":
    if st.session_state.get('logged_in') and st.session_state.get('user_type') == 'Donante':
        st.sidebar.title("Navegación Donante 🧭")
        menu = ["Perfil", "Campañas Disponibles", "Información sobre Donaciones", "Hospitales", "Requisitos"]
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
    else:
        st.warning("⚠️ Debes iniciar sesión como **Donante** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()
