import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, time as dt_time # Importar time específicamente para horarios


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


# --- Función para obtener datos del hospital ---
def obtener_datos_hospital(hospital_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del hospital.")
        return None
    try:
        response = supabase_client.table("hospital").select("*").eq("mail", hospital_email).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener datos del hospital: {e}")
        return None


# --- Función para actualizar datos del hospital ---
def actualizar_datos_hospital(hospital_email, datos):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del hospital.")
        return False
    try:
        response = supabase_client.table("hospital").update(datos).eq("mail", hospital_email).execute()
        if response.data:
            st.success("✅ ¡Perfil del Hospital actualizado con éxito!")
            time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
            st.rerun() # Recargar la página para ver los cambios
            return True
        else:
            st.error(f"❌ Error al actualizar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False


# --- Funciones para Campañas Solidarias del Hospital (recolección) ---
def obtener_campanas_solidarias_hospital(hospital_id):
    if supabase_client:
        try:
            # Ordenar por estado para que las "En Curso" y "Próximas" aparezcan primero
            # Luego, ordenar por Fecha_Inicio para las próximas o en curso
            response = supabase_client.table("campaña").select("*").eq("ID_Hospital", hospital_id).order("Estado_Campaña", desc=False).order("Fecha_Inicio", desc=False).execute()
            if response.data:
                return response.data
            else:
                return []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas solidarias: {e}")
            return []
    return []

def crear_nueva_campana_solidaria(datos_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña solidaria.")
        return False
    try:
        # Aquí insertamos los datos en la tabla 'campaña'
        data, count = supabase_client.table("campaña").insert(datos_campana).execute()
        if data and len(data) > 0:
            st.success("🎉 ¡Nueva campaña solidaria publicada con éxito!")
            return True
        else:
            st.error("❌ No se pudo publicar la nueva campaña solidaria.")
            return False
    except Exception as e:
        st.error(f"❌ Error al crear nueva campaña solidaria: {e}")
        return False

def finalizar_campana_solidaria(campana_id):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede finalizar la campaña.")
        return False
    try:
        response = supabase_client.table("campaña").update({"Estado_Campaña": "Finalizada"}).eq("ID_Campaña", campana_id).execute()
        if response.data:
            st.success(f"✅ Campaña {campana_id} finalizada con éxito.")
            return True
        else:
            st.error(f"❌ Error al finalizar campaña: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al finalizar campaña: {e}")
        return False


# --- Definición de las funciones de sección del Hospital ---
def hospital_perfil():
    st.markdown("<h2 style='color: #4CAF50;'>Mi Perfil de Hospital 🏥</h2>", unsafe_allow_html=True)
    st.write("Gestiona la información de tu hospital y asegura que tus datos estén actualizados.")

    email_usuario_logueado = st.session_state.get("user_email", "hospital@ejemplo.com")
    hospital_id_logueado = st.session_state.get("user_db_id") # Este ID no es usado en esta función directamente, pero es bueno tenerlo

    perfil_existente = obtener_datos_hospital(email_usuario_logueado)

    valores_iniciales = {
        "nombre_hospital": "",
        "mail": email_usuario_logueado,
        "telefono": "",
        "direccion": "",
        "sitio_web": "",
        "descripcion": "",
    }

    if perfil_existente:
        st.info(f"✨ Datos de perfil cargados para: **{perfil_existente.get('nombre_hospital', 'N/A')}**")
        valores_iniciales["nombre_hospital"] = perfil_existente.get("nombre_hospital", "")
        valores_iniciales["mail"] = perfil_existente.get("mail", email_usuario_logueado)
        valores_iniciales["telefono"] = perfil_existente.get("telefono", "")
        valores_iniciales["direccion"] = perfil_existente.get("direccion", "")
        valores_iniciales["sitio_web"] = perfil_existente.get("sitio_web", "")
        valores_iniciales["descripcion"] = perfil_existente.get("descripcion", "")

    with st.form("hospital_perfil_form"):
        st.markdown("#### Información del Hospital")
        col1, col2 = st.columns(2)
        with col1:
            nombre_hospital = st.text_input("Nombre del Hospital", value=valores_iniciales["nombre_hospital"])
            mail = st.text_input("Mail de Contacto", value=valores_iniciales["mail"], disabled=True)
            telefono = st.text_input("Teléfono del Hospital", value=valores_iniciales["telefono"])
        with col2:
            direccion = st.text_input("Dirección del Hospital", value=valores_iniciales["direccion"])
            sitio_web = st.text_input("Sitio Web (opcional)", value=valores_iniciales["sitio_web"])

        descripcion = st.text_area("Breve Descripción del Hospital", value=valores_iniciales["descripcion"])

        st.write("---")
        guardar = st.form_submit_button("💾 Guardar Perfil" if not perfil_existente else "🔄 Actualizar Perfil")

        if guardar:
            datos_a_guardar = {
                "nombre_hospital": nombre_hospital,
                "mail": mail,
                "telefono": telefono,
                "direccion": direccion,
                "sitio_web": sitio_web,
                "descripcion": descripcion,
            }
            if perfil_existente:
                actualizar_datos_hospital(mail, datos_a_guardar)
            else:
                st.warning("⚠️ La funcionalidad para crear un nuevo perfil de hospital aún no está implementada aquí.")
                st.info("Por favor, asegúrate de que el hospital ya exista en la base de datos para poder actualizar su perfil.")


def hospital_campanas_beneficiarios():
    st.markdown("<h2 style='color: #4CAF50;'>Campañas de Beneficiarios (Públicas) 🌐</h2>", unsafe_allow_html=True)
    st.write("Explora las campañas de donación de sangre publicadas por otros beneficiarios que necesitan ayuda, y gestiona las asociaciones con tu hospital.")

    hospital_id_logueado = st.session_state.get("user_db_id")

    if not hospital_id_logueado:
        st.warning("⚠️ Para ver y gestionar campañas de beneficiarios, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    if supabase_client:
        try:
            # Obtener información de beneficiarios para mostrar nombres
            response = supabase_client.table("beneficiario").select("ID_Beneficiario, Nombre, ID_Hospital_Asociado, mail").execute()
            beneficiarios = {b["ID_Beneficiario"]: b for b in response.data}

            # Obtener campañas de beneficiarios (solo "En Curso" por ahora)
            response_campanas = supabase_client.table("campana_beneficiario").select("*").eq("Estado_Campaña", "En Curso").order("Fecha_Fin", desc=False).execute()
            campanas_beneficiarios = response_campanas.data

            st.markdown("### Campañas Activas de Beneficiarios")
            if campanas_beneficiarios:
                for campana in campanas_beneficiarios:
                    beneficiario_info = beneficiarios.get(campana.get("ID_Beneficiario"))
                    beneficiario_nombre = beneficiario_info.get("Nombre", "Beneficiario Anónimo") if beneficiario_info else "Beneficiario Anónimo"

                    with st.expander(f"Campaña de: {beneficiario_nombre} (Tipo: {campana.get('Tipo_Sangre_Requerida', 'N/A')})"):
                        st.write(f"**ID Campaña:** {campana.get('ID_Campaña_Beneficiario', 'N/A')}")
                        st.write(f"**Descripción:** {campana.get('Descripcion_Campaña', 'N/A')}")
                        st.write(f"**Fecha Límite:** {campana.get('Fecha_Fin', 'N/A')}")
                        st.write(f"**Tipo de Sangre:** {campana.get('Tipo_Sangre_Requerida', 'N/A')}")
                        st.write(f"**Cantidad Necesaria:** {campana.get('Cantidad_Necesaria', 'N/A')} unidades")
                        st.write(f"**Estado:** `{campana.get('Estado_Campaña', 'N/A')}`")

                        hospital_asociado_id = beneficiario_info.get("ID_Hospital_Asociado") if beneficiario_info else None
                        if hospital_asociado_id:
                            if hospital_asociado_id == hospital_id_logueado:
                                st.success(f"**Asociado con tu Hospital:** ✅ (ID: {hospital_asociado_id})")
                            else:
                                st.info(f"**Asociado con otro Hospital:** (ID: {hospital_asociado_id})")
                        else:
                            st.warning("**No asociado a ningún Hospital.**")

                        if beneficiario_info and not hospital_asociado_id: # Solo mostrar botón si no está asociado
                            if st.button(f"Asociar Beneficiario {beneficiario_nombre} a mi Hospital", key=f"associate_ben_{campana.get('ID_Campaña_Beneficiario')}"):
                                try:
                                    supabase_client.table("beneficiario").update({"ID_Hospital_Asociado": hospital_id_logueado}).eq("ID_Beneficiario", campana.get('ID_Beneficiario')).execute()
                                    st.success(f"Beneficiario {beneficiario_nombre} asociado a tu hospital.")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al asociar beneficiario: {e}")

                    st.markdown("---") # Separador entre campañas
            else:
                st.info("ℹ️ No hay campañas de beneficiarios activas en este momento.")
        except Exception as e:
            st.error(f"❌ Error al obtener campañas de beneficiarios: {e}")
    else:
        st.error("Conexión a Supabase no disponible para obtener campañas de beneficiarios.")


def hospital_campanas_solidarias():
    st.markdown("<h2 style='color: #4CAF50;'>Mis Campañas Solidarias (Recolección en Hospital) 📢</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes gestionar las campañas de donación de sangre que tu hospital ha organizado para la recolección en sus propias instalaciones.")

    hospital_id_logueado = st.session_state.get("user_db_id")

    if not hospital_id_logueado:
        st.warning("⚠️ Para gestionar campañas solidarias, asegúrate de que tu perfil de hospital esté completo y tenga un ID válido.")
        return

    # --- Sección para CREAR Nueva Campaña Solidaria ---
    st.markdown("### ➕ Crear Nueva Campaña Solidaria")
    with st.form("nueva_campana_solidaria_form"):
        nombre_campana = st.text_input("Nombre de la Campaña", placeholder="Jornada de Donación - Verano 2025")
        ubicacion = st.text_input("Ubicación de la Campaña", placeholder="Ej: Hall principal, Salón de usos múltiples")
        fecha_campana = st.date_input("Fecha de la Campaña", value=datetime.today().date())
        horario_inicio = st.time_input("Hora de Inicio", value=dt_time(9, 0))
        horario_fin = st.time_input("Hora de Fin", value=dt_time(17, 0))
        estado_campana = st.selectbox("Estado de la Campaña", ["Próxima", "En Curso", "Finalizada"])

        guardar_campana = st.form_submit_button("🚀 Publicar Campaña")

        if guardar_campana:
            # Validaciones básicas
            if not nombre_campana or not ubicacion:
                st.error("Por favor, completa el nombre y la ubicación de la campaña.")
            elif horario_inicio >= horario_fin:
                st.error("La hora de inicio debe ser anterior a la hora de fin.")
            else:
                datos_campana = {
                    "ID_Hospital": hospital_id_logueado,
                    "Nombre_Campaña": nombre_campana,
                    "Ubicacion": ubicacion,
                    "Fecha_Inicio": fecha_campana.isoformat(), # Formato ISO para la base de datos
                    "Horario_Inicio": horario_inicio.isoformat(), # Formato ISO
                    "Horario_Fin": horario_fin.isoformat(), # Formato ISO
                    "Estado_Campaña": estado_campana,
                    # No se agrega Fecha_Limite aquí si no está en el formulario de creación.
                    # Si tu tabla `campaña` tiene `Fecha_Limite` como campo obligatorio
                    # y no es lo mismo que `Fecha_Inicio`, deberás añadirlo al formulario.
                }
                if crear_nueva_campana_solidaria(datos_campana):
                    # No es necesario un st.success() aquí porque ya está en la función
                    st.balloons()
                    st.rerun()

    st.markdown("---")
    st.markdown("### Campañas Solidarias Existentes")

    # --- Sección para VER y Gestionar Campañas Solidarias Existentes ---
    campanas = obtener_campanas_solidarias_hospital(hospital_id_logueado)

    if campanas:
        for campana in campanas:
            estado = campana.get("Estado_Campaña", "N/A")
            # Usa Fecha_Inicio si Fecha_Limite no es relevante para tu visualización aquí
            fecha_display = campana.get("Fecha_Inicio", "N/A") 

            with st.expander(f"Campaña: {campana.get('Nombre_Campaña', 'Sin Nombre')} (Estado: {estado})"):
                st.write(f"**ID Campaña:** {campana.get('ID_Campaña', 'N/A')}")
                st.write(f"**Ubicación:** {campana.get('Ubicacion', 'N/A')}")
                st.write(f"**Fecha:** {fecha_display}")
                st.write(f"**Horario:** {campana.get('Horario_Inicio', 'N/A')} - {campana.get('Horario_Fin', 'N/A')}")
                
                # Botón para finalizar campaña, solo si está "En Curso" o "Próxima"
                if estado == "En Curso" or estado == "Próxima":
                    if st.button(f"Finalizar Campaña '{campana.get('Nombre_Campaña')}'", key=f"finalizar_{campana.get('ID_Campaña')}"):
                        if finalizar_campana_solidaria(campana.get("ID_Campaña")):
                            st.rerun() # Recargar la página después de finalizar
                elif estado == "Finalizada":
                    st.info("Esta campaña ha sido finalizada.")
            st.markdown("---")
    else:
        st.info("No hay campañas solidarias disponibles para tu hospital.")


# --- Lógica principal de la página del Hospital ---
if __name__ == "__main__":
    if st.session_state.get("logged_in") and st.session_state.get("user_type") == "Hospital":
        st.sidebar.title("Navegación Hospital 🧭")
        menu = ["Perfil", "Campañas de Beneficiarios", "Campañas Solidarias"]
        opcion = st.sidebar.selectbox("Selecciona una sección", menu)

        if opcion == "Perfil":
            hospital_perfil()
        elif opcion == "Campañas de Beneficiarios":
            hospital_campanas_beneficiarios()
        elif opcion == "Campañas Solidarias":
            hospital_campanas_solidarias()
    else:
        st.warning("⚠️ Debes iniciar sesión como **Hospital** para acceder a esta página.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()