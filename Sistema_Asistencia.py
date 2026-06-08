import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.title("¡Bienvenidos a mi Programa!")
st.write("Esta aplicación se creó en VS Code y ahora está alojada en la nube.")

st.write("---")
st.subheader("Descargar Sistema de Asistencia")
st.write("Haz clic en el botón de abajo para obtener el archivo completo de la aplicación:")

# Buscamos el segundo archivo independiente en GitHub
with open("programa_real.py", "r", encoding="utf-8") as file:
    codigo_limpio = file.read()

st.download_button(
    label="📥 Descargar Programa de Asistencia",
    data=codigo_limpio,
    file_name="Sistema_Asistencia.py",
    mime="text/plain"
)
