import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.title("¡Bienvenidos a mi Programa!")
st.write("Esta aplicación se creó en VS Code y ahora está alojada en la nube.")

st.write("---")
st.subheader("Descargar Sistema de Asistencia")
st.write("Haz clic en el botón de abajo para obtener el archivo completo de la aplicación:")

# Código inteligente: Genera la descarga usando texto directo en internet
codigo_programa = """# Tu código original de Python va aquí si quieres, o puedes dejar este texto largo
print("¡Instalación Exitosa!")
"""

st.download_button(
    label="📥 Descargar Programa de Asistencia",
    data=codigo_programa,
    file_name="Sistema_Asistencia.py",
    mime="text/plain"
)
