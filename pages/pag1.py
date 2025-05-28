<<<<<<< Updated upstream
=======
import streamlit as st
from datetime import date
from supabase import create_client, Client
from dotenv import load_dotenv

def hospital_page():
    # Cargar claves desde .env
    load_dotenv()
    SUPABASE_URL = "https://ocqcjqltxynqsnnuvjbo.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIs..."

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 🌟 Encabezado con imagen decorativa centrada
    st.markdown(
        """
        <div style='text-align: center;'>
            <img src='gotita.png' width='120'>
            <h1 style='color: #d90429;'>🩸 Crear nueva solicitud de sangre</h1>
            <p style='font-size: 18px;'>Complete el siguiente formulario para solicitar unidades de sangre.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 📋 Formulario
    with st.form("formulario_solicitud"):
        st.markdown("### 📝 Datos de la solicitud")
        tipo_sangre = st.selectbox("🔴 Tipo de sangre necesario:", [
            "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"
        ])
        cantidad = st.number_input("🧪 Cantidad de unidades necesarias:", min_value=1, max_value=50, step=1)
        fecha_limite = st.date_input("📅 Fecha límite para la donación:", min_value=date.today())
        notas = st.text_area("📄 Notas adicionales (opcional):", placeholder="Ej: paciente pediátrico, cirugía urgente...")

        enviar = st.form_submit_button("📤 Enviar solicitud")

    # 💾 Enviar a Supabase
    if enviar:
        data = {
            "tipo_sangre": tipo_sangre,
            "cantidad": cantidad,
            "fecha_limite": str(fecha_limite),
            "notas": notas,
            "estado": "pendiente"
        }

        try:
            response = supabase.table("solicitudes_sangre").insert(data).execute()
            st.success("✅ Solicitud enviada con éxito.")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error al guardar en Supabase: {e}")



>>>>>>> Stashed changes
