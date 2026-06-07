#import tkinter as tk
#from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random
import os
from tkcalendar import DateEntry
# Recuerda tener instalado Pillow: pip install Pillow
import streamlit as st

st.title("¡Mi Primera Aplicación Web con Python!")
st.write("Esta aplicación se creó en VS Code y ahora está en internet.")

# Aquí va la lógica de tu programa
nombre = st.text_input("¿Cómo te llamas?")
if nombre:
    st.write(f"¡Hola, {nombre}! Bienvenido a mi programa.")
from PIL import Image, ImageTk

# Importaciones para gráficos de Matplotlib integrados con Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =====================================================================
# CONFIGURACIÓN DE PALETA DE COLORES (Estilo Oscuro / Neón)
# =====================================================================
BG_GRIS = "#7E8B8A"        
INPUT_BLANCO = "#FFFFFF"   
TEXT_NEGRO = "#000000"     
NEON_MORADO = "#E22BD9"    
TEXT_BLANCO = "#F2F3F5"

def inicializar_base_datos():
    """Crea y estructura las tablas necesarias en SQLite."""
    conn = sqlite3.connect("asistencia_fe_y_alegria.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY, 
            contrasena TEXT, 
            rol TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            cedula TEXT PRIMARY KEY, 
            nombre TEXT, 
            apellido TEXT, 
            genero TEXT,
            fecha_nacimiento TEXT,
            telefono TEXT,
            correo TEXT,
            ano TEXT, 
            seccion TEXT,
            turno TEXT,
            codigo_estudiante TEXT,
            nombre_rep TEXT,
            cedula_rep TEXT,
            telefono_rep TEXT
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE estudiantes ADD COLUMN genero TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula_estudiante TEXT,
            fecha TEXT,
            estado TEXT,
            FOREIGN KEY(cedula_estudiante) REFERENCES estudiantes(cedula)
        )
    """)
    
    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios VALUES ('admin', 'admin123', 'Administrador')")
        
    conn.commit()
    conn.close()


class AsistenciaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Asistencia - Fe y Alegría Prisco Villasmil")
        self.root.geometry("1366x768")
        self.root.configure(bg=BG_GRIS)
        self.root.state('zoomed') 
        
        self.usuario_actual = None
        self.rol_actual = None
        
        inicializar_base_datos()
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TCombobox", 
                             fieldbackground=INPUT_BLANCO, 
                             background=INPUT_BLANCO, 
                             foreground=TEXT_NEGRO,
                             darkcolor=INPUT_BLANCO,
                             lightcolor=INPUT_BLANCO)
        
        self.pantalla_bienvenida()

    def limpiar_pantalla(self):
        """Elimina los widgets de la ventana para renderizar una nueva sección."""
        for widget in self.root.winfo_children(): 
            widget.destroy()

    def obtener_logo_procesado(self, width=340, height=340):
        """Busca el archivo de imagen local y lo devuelve procesado en alta resolución."""
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        posibles_archivos = ["logo.png", "logo.png.png", "logo.jpg", "logo.jpeg"]
        
        for archivo in posibles_archivos:
            ruta_completa = os.path.join(carpeta_actual, archivo)
            if os.path.exists(ruta_completa):
                try:
                    imagen_original = Image.open(ruta_completa).convert("RGBA")
                    pixeles = imagen_original.load()
                    for y in range(imagen_original.size[1]):
                        for x in range(imagen_original.size[0]):
                            r, g, b, a = pixeles[x, y]
                            if (120 <= r <= 255) and (120 <= g <= 255) and (120 <= b <= 255):
                                if abs(r - g) < 10 and abs(g - b) < 10:
                                    if not (r > 200 and g < 120 and b > 180): 
                                        pixeles[x, y] = (0, 0, 0, 0)
                    
                    return imagen_original.resize((width, height), Image.Resampling.LANCZOS)
                except Exception as e:
                    print(f"Error al procesar {archivo}: {e}")
        return None

    # =====================================================================
    # PANTALLA DE BIENVENIDA CON LOGO COMO TITULO Y DISEÑO CENTRADO
    # =====================================================================
    def pantalla_bienvenida(self):
        self.limpiar_pantalla()
        self.usuario_actual = None
        self.rol_actual = None
        
        # Contenedor principal centrado
        f_main = tk.Frame(self.root, bg=BG_GRIS)
        f_main.pack(expand=True)
        
        # 1. Identidad de la Institución
        st.subheader("Fe y Alegría Prisco Villasmil", font=("Helvetica", 24, "bold"), fg=TEXT_BLANCO, bg=BG_GRIS).pack(pady=(10, 20))
        
        # 2. El Logo actúa como Título Visual
        img_logo = self.obtener_logo_procesado(340, 340)
        if img_logo:
            self.logo_bienvenida = ImageTk.PhotoImage(img_logo)
            lbl_logo = st.Label(f_main, image=self.logo_bienvenida, bg=BG_GRIS)
            lbl_logo.pack(pady=(0, 25))
        else:
            st.Label(f_main, text="[ LOGOTIPO INSTITUCIONAL ]", fg=NEON_MORADO, bg=BG_GRIS, font=("Helvetica", 16, "bold")).pack(pady=(0, 25))
        
        # Contenedor dinámico inferior para alternar botón / credenciales
        f_interactivo = st.Frame(f_main, bg=BG_GRIS)
        f_interactivo.pack(fill="x", pady=10)
        
        def desplegar_formulario_login():
            # Remueve el botón inicial para revelar el acceso de manera fluida
            for widget in f_interactivo.winfo_children():
                widget.destroy()
                
            st.Label(f_interactivo, text="Usuario:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11, "bold")).pack(anchor="center", pady=(0, 4))
            self.txt_user = st.Entry(f_interactivo, bg=INPUT_BLANCO, fg=TEXT_NEGRO, insertbackground=TEXT_NEGRO, relief="flat", width=30, font=("Helvetica", 12), justify="center")
            self.txt_user.pack(pady=(0, 12))
            self.txt_user.focus_set()
            
            st.Label(f_interactivo, text="Contraseña:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11, "bold")).pack(anchor="center", pady=(0, 4))
            self.txt_pass = st.Entry(f_interactivo, show="*", bg=INPUT_BLANCO, fg=TEXT_NEGRO, insertbackground=TEXT_NEGRO, relief="flat", width=30, font=("Helvetica", 12), justify="center")
            self.txt_pass.pack(pady=(0, 20))
            
            st.Button(f_interactivo, text="Confirmar Ingreso", command=self.procesar_login, bg=NEON_MORADO, fg=TEXT_BLANCO, width=22, font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2").pack(pady=(0, 10))
            st.Button(f_interactivo, text="Registrar Personal", command=self.pantalla_registrar_usuario, bg=BG_GRIS, fg=TEXT_BLANCO, relief="flat", font=("Helvetica", 10, "underline"), cursor="hand2").pack(pady=(0, 10))
            st.Button(f_interactivo, text="Volver", command=self.pantalla_bienvenida, bg="#2B2D31", fg=TEXT_BLANCO, relief="flat", font=("Helvetica", 9), width=10, cursor="hand2").pack()

        # 3. Botón de Ingresar Único Solicitado
        btn_ingresar = st.Button(f_interactivo, text="INGRESAR", command=desplegar_formulario_login, bg=NEON_MORADO, fg=TEXT_BLANCO, width=20, height=2, font=("Helvetica", 14, "bold"), relief="flat", cursor="hand2")
        btn_ingresar.pack(pady=10)
        
        st.Button(f_main, text="Salir de la Aplicación", command=self.root.quit, bg="#4E1414", fg=TEXT_BLANCO, relief="flat", font=("Helvetica", 9), width=18, cursor="hand2").pack(pady=(15, 0))

    def procesar_login(self):
        u, p = self.txt_user.get().strip(), self.txt_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Campos Vacíos", "Por favor ingrese su usuario y contraseña.")
            return

        conn = sqlite3.connect("asistencia_fe_y_alegria.db")
        c = conn.cursor()
        c.execute("SELECT usuario, rol FROM usuarios WHERE usuario=? AND contrasena=?", (u, p))
        resultado = c.fetchone()
        
        if resultado: 
            self.usuario_actual = resultado[0]
            self.rol_actual = resultado[1]
            conn.close()
            self.pantalla_menu_principal()
        else: 
            messagebox.showerror("Error", "Credenciales incorrectas. Verifique e intente de nuevo.")
            conn.close()

    def pantalla_registrar_usuario(self):
        self.limpiar_pantalla()
        
        f_main = tk.Frame(self.root, bg=BG_GRIS)
        f_main.pack(expand=True)
        
        f_izq = tk.Frame(f_main, bg=BG_GRIS, padx=40)
        f_izq.pack(side="left", fill="y", expand=True)
        
        img_logo = self.obtener_logo_procesado(320, 320)
        if img_logo:
            self.logo_registro = ImageTk.PhotoImage(img_logo)
            lbl_logo = st(f_izq, image=self.logo_registro, bg=BG_GRIS)
            lbl_logo.pack(expand=True)
        else:
            st.Label(f_izq, text="[ Logo no encontrado ]", fg="gray", bg=BG_GRIS, font=("Helvetica", 11, "italic")).pack(expand=True)
            
        sep = st.Frame(f_main, bg=NEON_MORADO, width=2)
        sep.pack(side="left", fill="y", padx=20)

        f_der = st.Frame(f_main, bg=BG_GRIS, padx=40)
        f_der.pack(side="left", fill="y", expand=True)
        
        st.Label(f_der, text="Registro de Personal Escolar", font=("Helvetica", 20, "bold"), fg=NEON_MORADO, bg=BG_GRIS).pack(pady=(10, 25))
        
        st.Label(f_der, text="Usuario asignado:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        u_e = st.Entry(f_der, bg=INPUT_BLANCO, fg=TEXT_NEGRO, insertbackground=TEXT_NEGRO, font=("Helvetica", 12), width=32, relief="flat")
        u_e.pack(pady=(0, 15))
        
        st.Label(f_der, text="Contraseña:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        p_e = st.Entry(f_der, show="*", bg=INPUT_BLANCO, fg=TEXT_NEGRO, insertbackground=TEXT_NEGRO, font=("Helvetica", 12), width=32, relief="flat")
        p_e.pack(pady=(0, 15))
        
        st.Label(f_der, text="Rol del Usuario:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        cb_rol = ttk.Combobox(f_der, values=["Docente", "Administrador"], state="readonly", font=("Helvetica", 11), width=30)
        cb_rol.pack(pady=(0, 25))
        cb_rol.current(0)
        
        def save():
            if not u_e.get().strip() or not p_e.get().strip():
                messagebox.showwarning("Campos vacíos", "Por favor rellene todos los campos.")
                return
            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios VALUES (?, ?, ?)", (u_e.get().strip(), p_e.get().strip(), cb_rol.get()))
                conn.commit()
                messagebox.showinfo("Éxito", f"Personal registrado como [{cb_rol.get()}] correctamente.")
                self.pantalla_bienvenida()
            except sqlite3.IntegrityError: 
                messagebox.showerror("Error", "El nombre de usuario ya se encuentra registrado.")
            finally:
                conn.close()
            
        st.Button(f_der, text="Registrar y Volver", command=save, bg=NEON_MORADO, fg=TEXT_BLANCO, font=("Helvetica", 12, "bold"), relief="flat", width=24, cursor="hand2").pack(pady=(0, 15))
        st.Button(f_der, text="Cancelar", command=self.pantalla_bienvenida, bg="#4E1414", fg=TEXT_BLANCO, font=("Helvetica", 10), relief="flat", width=16, cursor="hand2").pack()

    def pantalla_menu_principal(self):
        self.limpiar_pantalla()
        
        bar = st.Frame(self.root, bg=NEON_MORADO, height=55)
        bar.pack(fill="x")
        
        informacion_tag = f"PANEL DE CONTROL  |  Usuario: {self.usuario_actual} ({self.rol_actual})"
        st.Label(bar, text=informacion_tag, fg=TEXT_BLANCO, bg=NEON_MORADO, font=("Helvetica", 12, "bold")).pack(side="left", padx=25)
        st.Button(bar, text="Cerrar Sesión", command=self.pantalla_bienvenida, bg=BG_GRIS, fg=TEXT_BLANCO, relief="flat", font=("Helvetica", 10, "bold"), cursor="hand2").pack(side="right", padx=15)
        
        m_container = st.Frame(self.root, bg=BG_GRIS)
        m_container.pack(expand=True, fill="none", padx=20, pady=20)
        
        f_logo_panel = st.Frame(m_container, bg=BG_GRIS, padx=10)
        f_logo_panel.pack(side="left", fill="y")
        
        img_logo = self.obtener_logo_procesado(260, 260)
        if img_logo:
            self.logo_panel = ImageTk.PhotoImage(img_logo)
            lbl_logo = st.Label(f_logo_panel, image=self.logo_panel, bg=BG_GRIS)
            lbl_logo.pack(expand=True, anchor="e")
        else:
            st.Label(f_logo_panel, text="[ Logo ]", fg="gray", bg=BG_GRIS, font=("Helvetica", 11, "italic")).pack(expand=True)

        m = st.Frame(m_container, bg=BG_GRIS, padx=10)
        m.pack(side="left", fill="y")
        
        st.Button(m, text="Registrar Nuevo Estudiante", command=self.pantalla_registrar_estudiante, font=("Helvetica", 13, "bold"), bg="#2B2D31", fg=TEXT_BLANCO, width=35, height=2, relief="flat", cursor="hand2").pack(pady=10)
        st.Button(m, text="Control Matrícula (Pasar Asistencia)", command=self.pantalla_tomar_asistencia, font=("Helvetica", 13, "bold"), bg="#2B2D31", fg=TEXT_BLANCO, width=35, height=2, relief="flat", cursor="hand2").pack(pady=10)
        st.Button(m, text="Módulo Estadístico y Reportes", command=self.pantalla_reportes, font=("Helvetica", 13, "bold"), bg="#2B2D31", fg=TEXT_BLANCO, width=35, height=2, relief="flat", cursor="hand2").pack(pady=10)

    def pantalla_registrar_estudiante(self):
        self.limpiar_pantalla()
        
        f_principal = st.Frame(self.root, bg=BG_GRIS)
        f_principal.pack(expand=True, fill="both", padx=40, pady=20)
        
        st.Label(f_principal, text="SISTEMA DE CONTROL DE ASISTENCIA - REGISTRO DE MATRÍCULA", font=("Helvetica", 18, "bold"), fg=NEON_MORADO, bg=BG_GRIS).pack(pady=10)
        
        panel_columnas = st.Frame(f_principal, bg=BG_GRIS)
        panel_columnas.pack(expand=True, fill="both", pady=10)
        
        estilo_lbl_frame = {"bg": BG_GRIS, "fg": TEXT_BLANCO, "font": ("Helvetica", 12, "bold"), "bd": 1, "relief": "groove"}
        estilo_entrada = {"bg": INPUT_BLANCO, "fg": TEXT_NEGRO, "insertbackground": TEXT_NEGRO, "font": ("Helvetica", 11), "relief": "sunken", "bd": 1}
        
        col1 = st.LabelFrame(panel_columnas, text=" Datos Personales ", **estilo_lbl_frame)
        col1.pack(side="left", fill="both", expand=True, padx=15, pady=5)
        col1.grid_columnconfigure(1, weight=1)
        
        tk.Label(col1, text="Cédula de Identidad:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        frame_cedula = tk.Frame(col1, bg=BG_GRIS)
        frame_cedula.grid(row=0, column=1, sticky="ew", padx=10)
        
        cb_nac = ttk.Combobox(frame_cedula, values=["V-", "E-"], width=3, state="readonly", font=("Helvetica", 10))
        cb_nac.pack(side="left")
        cb_nac.current(0)
        
        ent_cedula = tk.Entry(frame_cedula, **estilo_entrada)
        ent_cedula.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Label(col1, text="Apellidos:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        ent_apellidos = tk.Entry(col1, **estilo_entrada)
        ent_apellidos.grid(row=1, column=1, sticky="ew", padx=10)
        
        tk.Label(col1, text="Nombres:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=2, column=0, sticky="w", padx=10, pady=8)
        ent_nombres = tk.Entry(col1, **estilo_entrada)
        ent_nombres.grid(row=2, column=1, sticky="ew", padx=10)
        
        tk.Label(col1, text="Género / Sexo:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=3, column=0, sticky="w", padx=10, pady=8)
        cb_ge = ttk.Combobox(col1, values=["Masculino", "Femenino"], state="readonly", font=("Helvetica", 10))
        cb_ge.grid(row=3, column=1, sticky="ew", padx=10)
        cb_ge.current(0)
        
        tk.Label(col1, text="Fecha de Nacimiento:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=4, column=0, sticky="w", padx=10, pady=8)
        cal_nacimiento = DateEntry(col1, background=NEON_MORADO, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', font=10)
        cal_nacimiento.grid(row=4, column=1, sticky="ew", padx=10)
        
        tk.Label(col1, text="Teléfono Celular:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=5, column=0, sticky="w", padx=10, pady=8)
        ent_telefono = tk.Entry(col1, **estilo_entrada)
        ent_telefono.grid(row=5, column=1, sticky="ew", padx=10)
        
        tk.Label(col1, text="Correo Electrónico:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=6, column=0, sticky="w", padx=10, pady=8)
        ent_correo = tk.Entry(col1, **estilo_entrada)
        ent_correo.grid(row=6, column=1, sticky="ew", padx=10)

        col2 = tk.LabelFrame(panel_columnas, text=" Distribución Escolar ", **estilo_lbl_frame)
        col2.pack(side="left", fill="both", expand=True, padx=15, pady=5)
        col2.grid_columnconfigure(1, weight=1)
        
        tk.Label(col2, text="Año de Curso:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        cb_ano = ttk.Combobox(col2, values=["1er Ano", "2do Ano", "3er Ano", "4to Ano", "5to Ano"], state="readonly", font=("Helvetica", 10))
        cb_ano.grid(row=0, column=1, sticky="ew", padx=10)
        cb_ano.current(3)
        
        tk.Label(col2, text="Sección Asignada:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        cb_seccion = ttk.Combobox(col2, values=["A", "B"], state="readonly", font=("Helvetica", 10))
        cb_seccion.grid(row=1, column=1, sticky="ew", padx=10)
        cb_seccion.current(0)
        
        tk.Label(col2, text="Turno Escolar:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=2, column=0, sticky="w", padx=10, pady=8)
        cb_turno = ttk.Combobox(col2, values=["Manana", "Tarde"], state="readonly", font=("Helvetica", 10))
        cb_turno.grid(row=2, column=1, sticky="ew", padx=10)
        cb_turno.current(0)
        
        tk.Label(col2, text="Código Alumno Interno:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=3, column=0, sticky="w", padx=10, pady=8)
        ent_codigo = tk.Entry(col2, bg="#2B2D31", fg="#00FFFF", font=("Helvetica", 11, "bold"), relief="flat")
        ent_codigo.grid(row=3, column=1, sticky="ew", padx=10)
        ent_codigo.insert(0, f"SB-{datetime.now().year}-04A-{random.randint(100,999)}")
        
        def actualizar_codigo_evento(e):
            ent_codigo.delete(0, tk.END)
            digito_ano = cb_ano.get()[0]
            secc_sel = cb_seccion.get()
            ent_codigo.insert(0, f"SB-{datetime.now().year}-0{digito_ano}{secc_sel}-{random.randint(100,999)}")
            
        cb_ano.bind("<<ComboboxSelected>>", actualizar_codigo_evento)
        cb_seccion.bind("<<ComboboxSelected>>", actualizar_codigo_evento)

        col3 = tk.LabelFrame(panel_columnas, text=" Ficha del Representante Legal ", **estilo_lbl_frame)
        col3.pack(side="left", fill="both", expand=True, padx=15, pady=5)
        col3.grid_columnconfigure(1, weight=1)
        
        tk.Label(col3, text="Nombre Completo:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        ent_rep_nombre = tk.Entry(col3, **estilo_entrada)
        ent_rep_nombre.grid(row=0, column=1, sticky="ew", padx=10)
        
        tk.Label(col3, text="Cédula de Identidad:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        frame_rep_ced = tk.Frame(col3, bg=BG_GRIS)
        frame_rep_ced.grid(row=1, column=1, sticky="ew", padx=10)
        cb_rep_nac = ttk.Combobox(frame_rep_ced, values=["V-", "E-"], width=3, state="readonly", font=("Helvetica", 10))
        cb_rep_nac.pack(side="left")
        cb_rep_nac.current(0)
        ent_rep_cedula = tk.Entry(frame_rep_ced, **estilo_entrada)
        ent_rep_cedula.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Label(col3, text="Teléfono de Contacto:", fg=TEXT_BLANCO, bg=BG_GRIS).grid(row=2, column=0, sticky="w", padx=10, pady=8)
        ent_rep_telf = tk.Entry(col3, **estilo_entrada)
        ent_rep_telf.grid(row=2, column=1, sticky="ew", padx=10)

        frame_botones = tk.Frame(f_principal, bg=BG_GRIS)
        frame_botones.pack(fill="x", pady=25)
        
        def limpiar_todo():
            for entry in [ent_cedula, ent_apellidos, ent_nombres, ent_telefono, ent_correo, ent_rep_nombre, ent_rep_cedula, ent_rep_telf]:
                entry.delete(0, tk.END)
            actualizar_codigo_evento(None)
            
        def ejecutar_guardado():
            ced_completa = cb_nac.get() + ent_cedula.get().strip()
            rep_ced_completa = cb_rep_nac.get() + ent_rep_cedula.get().strip()
            
            if not ent_cedula.get().strip() or not ent_apellidos.get().strip() or not ent_nombres.get().strip():
                messagebox.showwarning("Atención", "Campos del Alumno obligatorios (Cédula, Apellidos y Nombres)")
                return
                
            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO estudiantes (
                        cedula, nombre, apellido, genero, fecha_nacimiento, 
                        telefono, correo, ano, seccion, turno, 
                        codigo_estudiante, nombre_rep, cedula_rep, telefono_rep
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    ced_completa, ent_nombres.get().strip(), ent_apellidos.get().strip(), cb_ge.get(),
                    cal_nacimiento.get_date().strftime("%Y-%m-%d"), ent_telefono.get().strip(), ent_correo.get().strip(),
                    cb_ano.get(), cb_seccion.get(), cb_turno.get(), ent_codigo.get().strip(),
                    ent_rep_nombre.get().strip(), rep_ced_completa, ent_rep_telf.get().strip()
                ))
                conn.commit()
                messagebox.showinfo("Éxito", "Estudiante registrado e incorporado a la matrícula escolar.")
                self.pantalla_menu_principal()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Esta cédula escolar ya existe registrada.")
            except Exception as e:
                messagebox.showerror("Error Inesperado", f"No se pudo completar el guardado: {e}")
            finally:
                conn.close()

        tk.Button(frame_botones, text="Limpiar Formulario", command=limpiar_todo, bg="#4E1414", fg=TEXT_BLANCO, font=("Helvetica", 11, "bold"), width=18, relief="flat").pack(side="left", padx=20)
        tk.Button(frame_botones, text="Guardar Registro", command=ejecutar_guardado, bg="#00CC00", fg="#000000", font=("Helvetica", 11, "bold"), width=22, relief="flat").pack(side="right", padx=20)
        tk.Button(frame_botones, text="Volver al Menú", command=self.pantalla_menu_principal, bg="#2B2D31", fg=TEXT_BLANCO, font=("Helvetica", 11), width=18, relief="flat").pack(side="right", padx=10)

    def mostrar_ficha_estudiante(self, cedula_alumno):
        conn = sqlite3.connect("asistencia_fe_y_alegria.db")
        c = conn.cursor()
        c.execute("SELECT * FROM estudiantes WHERE cedula=?", (cedula_alumno,))
        alumno = c.fetchone()
        conn.close()

        if not alumno:
            messagebox.showerror("Error", "No se encontraron los datos de este estudiante.")
            return

        nombre_completo_estudiante = f"{alumno[2]}, {alumno[1]}".upper()

        modal = tk.Toplevel(self.root)
        modal.title(f"Expediente Escolar - {nombre_completo_estudiante}")
        modal.geometry("620x520")
        modal.configure(bg=BG_GRIS)
        modal.grab_set()
        modal.resizable(False, False)

        es_admin = (self.rol_actual == "Administrador")
        color_titulo = NEON_MORADO if es_admin else "#FFD700"

        tk.Label(modal, text=nombre_completo_estudiante, font=("Helvetica", 13, "bold"), fg=color_titulo, bg=BG_GRIS).pack(pady=10)
        
        contenedor_scroll = tk.Frame(modal, bg=BG_GRIS)
        contenedor_scroll.pack(fill="both", expand=True, padx=20, pady=5)
        
        canvas_ficha = tk.Canvas(contenedor_scroll, bg="#2B2D31", highlightthickness=0)
        scrollbar_vertical = ttk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas_ficha.yview)
        
        f_datos = tk.Frame(canvas_ficha, bg="#2B2D31", padx=15, pady=15)
        f_datos.bind("<Configure>", lambda e: canvas_ficha.configure(scrollregion=canvas_ficha.bbox("all")))
        
        canvas_ficha.create_window((0, 0), window=f_datos, anchor="nw", width=560)
        canvas_ficha.configure(yscrollcommand=scrollbar_vertical.set)
        
        canvas_ficha.pack(side="left", fill="both", expand=True)
        scrollbar_vertical.pack(side="right", fill="y")
        
        self.entradas_edicion = {}

        def agregar_linea_interactiva(label, valor, db_column_index, row):
            tk.Label(f_datos, text=label, fg="#00FFFF", bg="#2B2D31", font=("Helvetica", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
            
            if es_admin:
                ent = tk.Entry(f_datos, bg=INPUT_BLANCO, fg=TEXT_NEGRO, insertbackground=TEXT_NEGRO, font=("Helvetica", 10), width=32, relief="flat")
                ent.grid(row=row, column=1, sticky="w", padx=15, pady=5)
                ent.insert(0, valor if valor else "")
                self.entradas_edicion[db_column_index] = ent
            else:
                tk.Label(f_datos, text=valor if valor else "No registrado", fg=TEXT_BLANCO, bg="#2B2D31", font=("Helvetica", 10)).grid(row=row, column=1, sticky="w", padx=15, pady=5)

        if not es_admin:
            agregar_linea_interactiva("Cédula Estudiante:", alumno[0], 0, 0)
            agregar_linea_interactiva("Fecha Nacimiento:", alumno[4], 4, 1)
            agregar_linea_interactiva("Teléfono Estudiante:", alumno[5], 5, 2)
            
            tk.Frame(f_datos, bg=color_titulo, height=1).grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)
            
            agregar_linea_interactiva("Cédula Representante:", alumno[12], 12, 4)
            agregar_linea_interactiva("Teléfono Representante:", alumno[13], 13, 5)
        else:
            agregar_linea_interactiva("Cédula de Identidad *:", alumno[0], 0, 0)
            agregar_linea_interactiva("Nombres del Alumno:", alumno[1], 1, 1)
            agregar_linea_interactiva("Apellidos del Alumno:", alumno[2], 2, 2)
            agregar_linea_interactiva("Género / Sexo:", alumno[3], 3, 3)
            agregar_linea_interactiva("Fecha de Nacimiento (AAAA-MM-DD):", alumno[4], 4, 4)
            agregar_linea_interactiva("Teléfono Celular:", alumno[5], 5, 5)
            agregar_linea_interactiva("Correo Electrónico:", alumno[6], 6, 6)
            agregar_linea_interactiva("Año / Curso:", alumno[7], 7, 7)
            agregar_linea_interactiva("Sección Asignada:", alumno[8], 8, 8)
            agregar_linea_interactiva("Turno Horario:", alumno[9], 9, 9)
            agregar_linea_interactiva("Código de Alumno Interno:", alumno[10], 10, 10)
            
            tk.Frame(f_datos, bg=NEON_MORADO, height=1).grid(row=11, column=0, columnspan=2, sticky="ew", pady=12)
            
            agregar_linea_interactiva("Nombre del Representante:", alumno[11], 11, 12)
            agregar_linea_interactiva("Cédula del Representante:", alumno[12], 12, 13)
            agregar_linea_interactiva("Teléfono del Representante:", alumno[13], 13, 14)

        panel_acciones = tk.Frame(modal, bg=BG_GRIS)
        panel_acciones.pack(fill="x", side="bottom", pady=15)

        def guardar_modificaciones_admin():
            nueva_cedula = self.entradas_edicion[0].get().strip()
            if not nueva_cedula:
                messagebox.showerror("Error", "La cédula del estudiante no puede quedar vacía.")
                return

            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()
            try:
                c.execute("""
                    UPDATE estudiantes SET
                        nombre=?, apellido=?, genero=?, fecha_nacimiento=?, telefono=?,
                        correo=?, ano=?, seccion=?, turno=?, codigo_estudiante=?,
                        nombre_rep=?, cedula_rep=?, telefono_rep=?, cedula=?
                    WHERE cedula=?
                """, (
                    self.entradas_edicion[1].get().strip(), self.entradas_edicion[2].get().strip(),
                    self.entradas_edicion[3].get().strip(), self.entradas_edicion[4].get().strip(),
                    self.entradas_edicion[5].get().strip(), self.entradas_edicion[6].get().strip(),
                    self.entradas_edicion[7].get().strip(), self.entradas_edicion[8].get().strip(),
                    self.entradas_edicion[9].get().strip(), self.entradas_edicion[10].get().strip(),
                    self.entradas_edicion[11].get().strip(), self.entradas_edicion[12].get().strip(),
                    self.entradas_edicion[13].get().strip(), nueva_cedula,
                    cedula_alumno
                ))
                conn.commit()
                messagebox.showinfo("Éxito", "Expediente escolar actualizado correctamente.")
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar los cambios: {e}")
            finally:
                conn.close()

        if es_admin:
            tk.Button(panel_acciones, text="Actualizar Datos", command=guardar_modificaciones_admin, bg="#00CC00", fg="#000000", font=("Helvetica", 10, "bold"), relief="flat", width=18).pack(side="left", padx=35)
            tk.Button(panel_acciones, text="Cancelar", command=modal.destroy, bg="#2B2D31", fg=TEXT_BLANCO, font=("Helvetica", 10), relief="flat", width=12).pack(side="right", padx=35)
        else:
            tk.Button(panel_acciones, text="Cerrar Ficha", command=modal.destroy, bg="#2B2D31", fg=TEXT_BLANCO, font=("Helvetica", 11, "bold"), relief="flat", width=16).pack()

    def pantalla_tomar_asistencia(self):
        self.limpiar_pantalla()
        f_top = tk.Frame(self.root, bg=BG_GRIS)
        f_top.pack(pady=15)
        
        cb_a = ttk.Combobox(f_top, values=["1er Ano", "2do Ano", "3er Ano", "4to Ano", "5to Ano"], width=12, state="readonly", font=10)
        cb_a.grid(row=0, column=0, padx=8)
        cb_a.current(3)
        cb_s = ttk.Combobox(f_top, values=["A", "B"], width=6, state="readonly", font=10)
        cb_s.grid(row=0, column=1, padx=8)
        cb_s.current(0)
        
        tk.Label(self.root, text="Nota: Los nombres tienen hipervínculo. Haga clic sobre ellos para auditar la ficha.", fg="#00FFFF", bg=BG_GRIS, font=("Helvetica", 10, "italic")).pack()
        
        f_list = tk.LabelFrame(self.root, text=" Cuadrícula de Asistencia por Salón ", bg=BG_GRIS, fg=TEXT_BLANCO, font=("bold", 11))
        f_list.pack(fill="both", expand=True, padx=35, pady=10)
        
        canv = tk.Canvas(f_list, bg=BG_GRIS, highlightthickness=0)
        scr = ttk.Scrollbar(f_list, orient="vertical", command=canv.yview)
        scroll_f = tk.Frame(canv, bg=BG_GRIS)
        
        scroll_f.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
        canv.create_window((0,0), window=scroll_f, anchor="nw")
        canv.configure(yscrollcommand=scr.set)
        
        canv.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scr.pack(side="right", fill="y") 
        votos = {}
        
        def cargar():
            for w in scroll_f.winfo_children(): 
                w.destroy()
            votos.clear()
            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()
            c.execute("SELECT cedula, nombre, apellido FROM estudiantes WHERE ano=? AND seccion=? ORDER BY apellido ASC", (cb_a.get(), cb_s.get()))
            filas = c.fetchall()
            if not filas:
                tk.Label(scroll_f, text="No hay alumnos inscritos en este salón.", fg="#FF5555", bg=BG_GRIS, font=("bold", 12)).pack(pady=20)
            
            for i, (ced, nom, ape) in enumerate(filas):
                tk.Frame(scroll_f, bg="#2B2D31", height=1, width=1200).grid(row=i*2, column=0, columnspan=2, sticky="ew", pady=4)
                
                lbl_estudiante = tk.Label(scroll_f, text=f"{ced}  -  {ape}, {nom}", fg="#8A2BE2", bg=BG_GRIS, font=("Helvetica", 11, "bold", "underline"), width=45, anchor="w", cursor="hand2")
                lbl_estudiante.grid(row=i*2+1, column=0, padx=15, pady=6)
                
                lbl_estudiante.bind("<Button-1>", lambda event, c_id=ced: self.mostrar_ficha_estudiante(c_id))
                
                f_btn = tk.Frame(scroll_f, bg=BG_GRIS)
                f_btn.grid(row=i*2+1, column=1)
                votos[ced] = tk.StringVar(value="None")
                
                opts = [("Asistente","#00FF00"), ("Ausente","#FF0000"), ("Jubilado","#FFD700"), ("Reposo","#00FFFF")]
                for txt, col in opts:
                    tk.Radiobutton(f_btn, text=txt, variable=votos[ced], value=txt, fg=col, bg=BG_GRIS, selectcolor=BG_GRIS, activebackground=BG_GRIS, font=("Helvetica", 10, "bold")).pack(side="left", padx=10)
            conn.close()

        tk.Button(f_top, text="Cargar Alumnos", command=cargar, bg=NEON_MORADO, fg=TEXT_BLANCO, font=("bold", 10), relief="flat", width=15).grid(row=0, column=2, padx=15)
        
        def enviar():
            if not votos: 
                return
            hoy = datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()
            for _ced, var in votos.items():
                if var.get() == "None":
                    messagebox.showwarning("Incompleto", "Asigne un estado de asistencia a todos los estudiantes listados.")
                    conn.close()
                    return
            for ced, var in votos.items():
                c.execute("INSERT INTO asistencia (cedula_estudiante, fecha, estado) VALUES (?,?,?)", (ced, hoy, var.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Matriz de asistencia guardada con éxito.")
            self.pantalla_menu_principal()
        
        tk.Button(self.root, text="GUARDAR ASISTENCIA COMPLETA DEL DIA", command=enviar, bg="#00CC00", fg="#000000", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=20, ipady=5)
        tk.Button(self.root, text="Volver al Menú", command=self.pantalla_menu_principal, bg="#2B2D31", fg=TEXT_BLANCO, relief="flat").pack(pady=5)

    def pantalla_reportes(self):
        self.limpiar_pantalla()

        f_filtros = tk.Frame(self.root, bg=BG_GRIS)
        f_filtros.pack(fill="x", padx=30, pady=15)

        tk.Label(f_filtros, text="Fecha Consulta:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11)).grid(row=0, column=0, padx=5, sticky="w")
        cal_reporte = DateEntry(f_filtros, background=NEON_MORADO, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd', font=10, width=12)
        cal_reporte.grid(row=0, column=1, padx=10)

        tk.Label(f_filtros, text="Cobertura Escolar:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11)).grid(row=0, column=2, padx=5, sticky="w")
        cb_cobertura = ttk.Combobox(f_filtros, values=["Todos los Anos (Global)", "Aula Especifica"], state="readonly", font=("Helvetica", 10), width=22)
        cb_cobertura.grid(row=0, column=3, padx=10)
        cb_cobertura.current(0)

        lbl_ano = tk.Label(f_filtros, text="Año:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11))
        cb_ano = ttk.Combobox(f_filtros, values=["1er Ano", "2do Ano", "3er Ano", "4to Ano", "5to Ano"], state="readonly", font=("Helvetica", 10), width=10)
        lbl_secc = tk.Label(f_filtros, text="Secc:", fg=TEXT_BLANCO, bg=BG_GRIS, font=("Helvetica", 11))
        cb_seccion = ttk.Combobox(f_filtros, values=["A", "B"], state="readonly", font=("Helvetica", 10), width=5)

        def cambiar_visibilidad_filtros(e):
            if cb_cobertura.get() == "Aula Especifica":
                lbl_ano.grid(row=0, column=4, padx=5)
                cb_ano.grid(row=0, column=5, padx=5)
                cb_ano.current(3)
                lbl_secc.grid(row=0, column=6, padx=5)
                cb_seccion.grid(row=0, column=7, padx=5)
                cb_seccion.current(0)
            else:
                lbl_ano.grid_forget()
                cb_ano.grid_forget()
                lbl_secc.grid_forget()
                cb_seccion.grid_forget()

        cb_cobertura.bind("<<ComboboxSelected>>", cambiar_visibilidad_filtros)

        frame_graficos = tk.Frame(self.root, bg=BG_GRIS)
        frame_graficos.pack(fill="both", expand=True, padx=30, pady=10)

        def generar_graficos():
            for widget in frame_graficos.winfo_children():
                widget.destroy()

            fecha_sel = cal_reporte.get_date().strftime("%Y-%m-%d")
            cobertura = cb_cobertura.get()
            ano_sel = cb_ano.get()
            secc_sel = cb_seccion.get()

            conn = sqlite3.connect("asistencia_fe_y_alegria.db")
            c = conn.cursor()

            if cobertura == "Todos los Anos (Global)":
                c.execute("""
                    SELECT asis.estado, COUNT(asis.estado) 
                    FROM asistencia asis
                    WHERE asis.fecha = ?
                    GROUP BY asis.estado
                """, (fecha_sel,))
            else:
                c.execute("""
                    SELECT asis.estado, COUNT(asis.estado) 
                    FROM asistencia asis
                    JOIN estudiantes est ON asis.cedula_estudiante = est.cedula
                    WHERE est.ano = ? AND est.seccion = ? AND asis.fecha = ?
                    GROUP BY asis.estado
                """, (ano_sel, secc_sel, fecha_sel))

            datos = c.fetchall()
            conn.close()

            estados_dict = {"Asistente": 0, "Ausente": 0, "Jubilado": 0, "Reposo": 0}
            for est, cant in datos:
                if est in estados_dict:
                    estados_dict[est] = cant

            categorias = list(estados_dict.keys())
            valores = list(estados_dict.values())
            colores = ["#00FF00", "#FF0000", "#FFD700", "#00FFFF"] 

            if sum(valores) == 0:
                tk.Label(frame_graficos, text=f"No se encontraron registros cargados\npara la fecha: {fecha_sel}", 
                         fg="#FF5555", bg=BG_GRIS, font=("Helvetica", 16, "bold")).pack(expand=True)
                return

            plt.rcParams['text.color'] = 'white'
            plt.rcParams['axes.labelcolor'] = 'white'
            plt.rcParams['xtick.color'] = 'white'
            plt.rcParams['ytick.color'] = 'white'

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), facecolor=BG_GRIS)

            ax1.set_facecolor("#2B2D31")
            barras = ax1.bar(categorias, valores, color=colores, edgecolor="white", width=0.5)
            ax1.set_title("Frecuencia Métrica Global", fontsize=12, fontweight="bold")
            ax1.set_ylabel("Cantidad Alumnos")
            ax1.grid(axis='y', linestyle='--', alpha=0.3)

            for bar in barras:
                yval = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontweight='bold')

            ax2.set_facecolor(BG_GRIS)
            indices_validos = [i for i, v in enumerate(valores) if v > 0]
            cat_pie = [categorias[i] for i in indices_validos]
            val_pie = [valores[i] for i in indices_validos]
            col_pie = [colores[i] for i in indices_validos]

            ax2.pie(val_pie, labels=cat_pie, colors=col_pie, autopct='%1.1f%%', startangle=90, 
                    textprops={'fontsize': 10, 'weight': 'bold'}, wedgeprops={'edgecolor': 'white', 'linewidth': 1})
            ax2.set_title("Distribución Porcentual %", fontsize=12, fontweight="bold")

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            f_drill_btns = tk.Frame(frame_graficos, bg=BG_GRIS)
            f_drill_btns.pack(pady=10)

            tk.Label(f_drill_btns, text="Auditar Alumnos por Estado:", fg="#00FFFF", bg=BG_GRIS, font=("Helvetica", 10, "bold")).pack(side="left", padx=10)
            for cat, col in zip(categorias, colores):
                estado_btn = "normal" if estados_dict[cat] > 0 else "disabled"
                tk.Button(f_drill_btns, text=f"Ver {cat}", command=lambda c=cat: self.mostrar_desglose_estudiantes(c, fecha_sel, cobertura, ano_sel, secc_sel),
                          bg="#2B2D31", fg=col, state=estado_btn, font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)

        tk.Button(f_filtros, text="Procesar Métricas", command=generar_graficos, bg=NEON_MORADO, fg=TEXT_BLANCO, font=("Helvetica", 10, "bold"), relief="flat", width=18, cursor="hand2").grid(row=0, column=8, padx=20)

        generar_graficos()

        f_bottom = tk.Frame(self.root, bg=BG_GRIS)
        f_bottom.pack(fill="x", side="bottom", pady=15)
        tk.Button(f_bottom, text="Volver al Panel de Control principal", command=self.pantalla_menu_principal, bg="#2B2D31", fg=TEXT_BLANCO, font=("Helvetica", 11), relief="flat", width=30).pack()

    def mostrar_desglose_estudiantes(self, estado_seleccionado, fecha, cobertura, ano, seccion):
        ventana_drill = tk.Toplevel(self.root)
        ventana_drill.title(f"Detalle: Alumnos con Estado {estado_seleccionado} ({fecha})")
        ventana_drill.geometry("650x450")
        ventana_drill.configure(bg=BG_GRIS)
        ventana_drill.grab_set() 
        
        titulo_txt = f"Alumnos en estado '{estado_seleccionado}'"
        sub_txt = f"Fecha: {fecha} | Alcance: {cobertura if cobertura != 'Aula Especifica' else f'{ano} Secc {seccion}'}"
        
        tk.Label(ventana_drill, text=titulo_txt, font=("Helvetica", 14, "bold"), fg=NEON_MORADO, bg=BG_GRIS).pack(pady=10)
        tk.Label(ventana_drill, text=sub_txt, font=("Helvetica", 10), fg=TEXT_BLANCO, bg=BG_GRIS).pack(pady=2)
        
        tabla_frame = tk.Frame(ventana_drill, bg=BG_GRIS)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        columnas = ("cedula", "apellido", "nombre", "aula")
        tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=12)
        tree.heading("cedula", text="Cédula Escolar")
        tree.heading("apellido", text="Apellidos")
        tree.heading("nombre", text="Nombres")
        tree.heading("aula", text="Aula Asignada")
        
        tree.column("cedula", width=110, anchor="center")
        tree.column("apellido", width=150, anchor="w")
        tree.column("nombre", width=150, anchor="w")
        tree.column("aula", width=100, anchor="center")
        
        conn = sqlite3.connect("asistencia_fe_y_alegria.db")
        c = conn.cursor()
        
        if cobertura == "Todos los Anos (Global)":
            q = """SELECT est.cedula, est.apellido, est.nombre, est.ano || ' ' || est.seccion
                   FROM asistencia asis
                   JOIN estudiantes est ON asis.cedula_estudiante = est.cedula
                   WHERE asis.fecha = ? AND asis.estado = ?
                   ORDER BY est.apellido ASC"""
            p = (fecha, estado_seleccionado)
        else:
            q = """SELECT est.cedula, est.apellido, est.nombre, est.ano || ' ' || est.seccion
                   FROM asistencia asis
                   JOIN estudiantes est ON asis.cedula_estudiante = est.cedula
                   WHERE est.ano = ? AND est.seccion = ? AND asis.fecha = ? AND asis.estado = ?
                   ORDER BY est.apellido ASC"""
            p = (ano, seccion, fecha, estado_seleccionado)

        c.execute(q, p)
        filas = c.fetchall()
        conn.close()

        for f in filas:
            tree.insert("", "end", values=f)

        sb_tree = ttk.Scrollbar(tabla_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb_tree.set)
        tree.pack(side="left", fill="both", expand=True)
        sb_tree.pack(side="right", fill="y")

        tk.Button(ventana_drill, text="Cerrar Detalle", command=ventana_drill.destroy, bg=NEON_MORADO, fg=TEXT_BLANCO, font=("Helvetica", 10, "bold"), relief="flat", width=15).pack(pady=10)
  # --- CÓDIGO PARA TU PÁGINA WEB DE DESCARGA ---
st.write("---")
st.subheader("Descargar Sistema de Asistencia")

st.write("Haz clic en el botón de abajo para obtener el archivo de la aplicación:")

# Apuntamos al archivo de Descargas que tienes abierto
with open("c:/Users/Milano Rivera/Downloads/Sistema_Asistencia.py", "rb") as file:
    st.download_button(
        label="📥 Descargar Programa de Asistencia",
        data=file,
        file_name="Sistema_Asistencia.py",
        mime="text/plain"
    )
