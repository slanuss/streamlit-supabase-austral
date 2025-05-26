import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, time as dt_time

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Advertencia: Las variables de entorno SUPABASE_URL y SUPABASE_KEY no están configuradas en el .env.")
    st.info("Por favor, confiáguralas para que la conexión a la base de datos funcione.")
    supabase_client: Client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")
        supabase_client: Client = None

# --- Funciones para datos del hospital ---
def obtener_datos_hospital(hospital_email):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden obtener datos del hospital.")
        return None
    try:
        response = supabase_client.table("hospital").select("*").eq("mail", hospital_email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error al obtener datos del hospital: {e}")
        return None

def actualizar_datos_hospital(hospital_email, datos):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se pueden actualizar datos del hospital.")
        return False
    try:
        response = supabase_client.table("hospital").update(datos).eq("mail", hospital_email).execute()
        if response.data:
            st.success("✅ ¡Perfil del Hospital actualizado con éxito!")
            time.sleep(1)
            st.rerun()
            return True
        else:
            st.error("❌ No se pudo actualizar el perfil del hospital.")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al actualizar datos: {e}")
        return False

# --- Funciones para campañas solidarias ---
def obtener_campanas_solidarias_hospital(hospital_id):
    if supabase_client:
        try:
            response = supabase_client.table("campaña").select("*").eq("id_hospital", hospital_id).order("fecha_inicio").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"❌ Error al obtener campañas solidarias: {e}")
            return []
    return []

def crear_nueva_campana_solidaria(datos_campana):
    if supabase_client is None:
        st.error("Conexión a Supabase no disponible. No se puede crear la campaña solidaria.")
        return False
    try:
        data, _ = supabase_client.table("campaña").insert(datos_campana).execute()
        if data:
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
        response = supabase_client.table("campaña").update({"estado_campana": "Finalizada"}).eq("id_campana", campana_id).execute()
        if response.data:
            st.success(f"✅ Campaña {campana_id} finalizada con éxito.")
            return True
        else:
            st.error("❌ No se pudo finalizar la campaña.")
            return False
    except Exception as e:
        st.error(f"❌ Error inesperado al finalizar campaña: {e}")
        return False

# --- Página de perfil del hospital ---
def hospital_perfil():
    st.markdown("<h2 style='color: #4CAF50;'>Mi Perfil de Hospital 🏥</h2>", unsafe_allow_html=True)
    email = st.session_state.get("user_email", "hospital@ejemplo.com")
    perfil = obtener_datos_hospital(email)

    valores = {
        "nombre_hospital": perfil.get("nombre_hospital", "") if perfil else "",
        "mail": email,
        "telefono": perfil.get("telefono", "") if perfil else "",
        "direccion": perfil.get("direccion", "") if perfil else "",
        "sitio_web": perfil.get("sitio_web", "") if perfil else "",
        "descripcion": perfil.get("descripcion", "") if perfil else ""
    }

    with st.form("perfil_hospital_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Hospital", value=valores["nombre_hospital"])
            mail = st.text_input("Mail", value=valores["mail"], disabled=True)
            telefono = st.text_input("Teléfono", value=valores["telefono"])
        with col2:
            direccion = st.text_input("Dirección", value=valores["direccion"])
            sitio = st.text_input("Sitio Web", value=valores["sitio_web"])

        descripcion = st.text_area("Descripción", value=valores["descripcion"])
        submit = st.form_submit_button("Guardar")

        if submit:
            datos = {
                "nombre_hospital": nombre,
                "mail": mail,
                "telefono": telefono,
                "direccion": direccion,
                "sitio_web": sitio,
                "descripcion": descripcion,
            }
            if perfil:
                actualizar_datos_hospital(mail, datos)
            else:
                st.warning("No se permite crear nuevos perfiles desde esta interfaz.")

# --- Página de campañas solidarias ---
def hospital_campanas_solidarias():
    st.markdown("<h2 style='color: #4CAF50;'>Mis Campañas Solidarias 📢</h2>", unsafe_allow_html=True)
    hospital_id = st.session_state.get("user_db_id")

    if not hospital_id:
        st.warning("Completa tu perfil antes de crear campañas.")
        return

    with st.form("crear_campana_form"):
        nombre = st.text_input("Nombre de la Campaña")
        ubicacion = st.text_input("Ubicación")
        fecha = st.date_input("Fecha", value=datetime.today().date())
        hora = st.time_input("Hora de Inicio", value=dt_time(9, 0))
        estado = st.selectbox("Estado", ["Próxima", "En Curso", "Finalizada"])
        submit = st.form_submit_button("Publicar Campaña")

        if submit and nombre and ubicacion:
            datos = {
                "id_hospital": hospital_id,
                "nombre_campana": nombre,
                "ubicacion": ubicacion,
                "fecha_inicio": fecha.isoformat(),
                "horario_inicio": hora.isoformat(),
                "estado_campana": estado,
            }
            if crear_nueva_campana_solidaria(datos):
                st.balloons()
                st.rerun()

    st.markdown("---")
    st.markdown("### Campañas Existentes")
    campañas = obtener_campanas_solidarias_hospital(hospital_id)

    for camp in campañas:
        with st.expander(f"{camp['nombre_campana']} ({camp['estado_campana']})"):
            st.write(f"**Ubicación:** {camp['ubicacion']}")
            st.write(f"**Fecha:** {camp['fecha_inicio']}")
            st.write(f"**Hora de Inicio:** {camp['horario_inicio']}")
            if camp['estado_campana'] in ["Próxima", "En Curso"]:
                if st.button(f"Finalizar {camp['nombre_campana']}", key=f"finalizar_{camp['id_campana']}"):
                    if finalizar_campana_solidaria(camp['id_campana']):
                        st.rerun()

# --- Lógica principal ---
if __name__ == "__main__":
    if st.session_state.get("logged_in") and st.session_state.get("user_type") == "Hospital":
        st.sidebar.title("Navegación Hospital 🧭")
        opcion = st.sidebar.selectbox("Sección", ["Perfil", "Campañas Solidarias"])

        if opcion == "Perfil":
            hospital_perfil()
        elif opcion == "Campañas Solidarias":
            hospital_campanas_solidarias()
    else:
        st.warning("Inicia sesión como Hospital para acceder.")
        if st.button("Ir a Inicio de Sesión"):
            st.session_state["logged_in"] = False
            st.session_state["user_type"] = None
            st.rerun()
