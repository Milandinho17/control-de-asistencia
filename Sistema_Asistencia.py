#import tkinter as tk
#from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random
import os
#from tkcalendar import DateEntry
# Recuerda tener instalado Pillow: pip install Pillow
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.title("¡Bienvenidos a mi Programa!")
st.write("Esta aplicación se creó en VS Code y ahora está alojada en la nube.")

st.write("---")
st.subheader("Descargar Sistema de Asistencia")
st.write("Haz clic en el botón de abajo para obtener el archivo completo de la aplicación:")

# Código limpio para descargar el archivo directamente desde internet
with open("Sistema_Asistencia.py", "rb") as file:
    st.download_button(
        label="📥 Descargar Programa de Asistencia",
        data=file,
        file_name="Sistema_Asistencia.py",
        mime="text/plain"
    )
