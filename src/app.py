import os
import zipfile
import shutil
import threading

import rarfile
import py7zr

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tkinterdnd2 import TkinterDnD, DND_FILES


# -------- CONFIGURACION UI --------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -------- RUTAS --------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")


# -------- FUNCIONES --------

def limpiar_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)


def es_paquete_corel(carpeta):
    try:
        elementos = os.listdir(carpeta)
        return "content" in elementos and "mimetype" in elementos
    except:
        return False


def reconstruir_cdr(carpeta):
    nombre = os.path.basename(carpeta)
    salida = os.path.join(DOWNLOADS, f"{nombre}_FIX.cdr")
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as zipf:
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                ruta = os.path.join(raiz, archivo)
                relativa = os.path.relpath(ruta, carpeta)
                zipf.write(ruta, relativa)
    return salida


def extraer_archivo(archivo):
    limpiar_temp()
    ext = os.path.splitext(archivo)[1].lower()
    if ext == ".zip":
        with zipfile.ZipFile(archivo, "r") as z:
            z.extractall(TEMP_DIR)
    elif ext == ".rar":
        with rarfile.RarFile(archivo) as r:
            r.extractall(TEMP_DIR)
    elif ext == ".7z":
        with py7zr.SevenZipFile(archivo, "r") as z:
            z.extractall(TEMP_DIR)
    else:
        raise ValueError("Formato no soportado")


def buscar_paquete():
    for raiz, dirs, files in os.walk(TEMP_DIR):
        if "content" in dirs and "mimetype" in files:
            return raiz
    return None


def detectar_formatos(carpeta_raiz=None):
    if carpeta_raiz is None:
        carpeta_raiz = TEMP_DIR

    formatos_detectados = []

    EXTENSIONES = {
        ".ai":       "Adobe Illustrator (.ai)",
        ".psd":      "Photoshop (.psd)",
        ".svg":      "SVG (.svg)",
        ".eps":      "EPS (.eps)",
        ".pdf":      "PDF (.pdf)",
        ".indd":     "InDesign (.indd)",
        ".xd":       "Adobe XD (.xd)",
        ".fig":      "Figma (.fig)",
        ".afdesign": "Affinity Designer (.afdesign)",
        ".cdr":      "CorelDRAW (.cdr) — sin estructura de paquete",
    }

    for raiz, dirs, files in os.walk(carpeta_raiz):
        for archivo in files:
            ext = os.path.splitext(archivo)[1].lower()
            if ext in EXTENSIONES:
                formatos_detectados.append(EXTENSIONES[ext])

    return list(set(formatos_detectados))


# -------- LOGICA --------

def procesar(ruta):
    try:
        progress.set(0.1)
        estado.configure(text="Analizando archivo...")

        if os.path.isdir(ruta):
            progress.set(0.4)
            if es_paquete_corel(ruta):
                salida = reconstruir_cdr(ruta)
                progress.set(1)
                estado.configure(text="✔ CDR reconstruido")
                resultado.configure(text=f"Guardado en:\n{salida}")
            else:
                progress.set(0)
                formatos = detectar_formatos(ruta)
                if formatos:
                    lista = "\n".join(f"  • {f}" for f in formatos)
                    estado.configure(text="⚠ Formato no compatible")
                    resultado.configure(
                        text=f"Se detectaron estos archivos:\n{lista}\n\nEste programa solo reconstruye CorelDRAW"
                    )
                else:
                    estado.configure(text="Archivo no compatible")
                    resultado.configure(
                        text="No se encontró ningún archivo CorelDRAW\npara reconstruir"
                    )
        else:
            progress.set(0.3)
            extraer_archivo(ruta)
            progress.set(0.6)
            carpeta = buscar_paquete()
            if carpeta:
                salida = reconstruir_cdr(carpeta)
                progress.set(1)
                estado.configure(text="✔ CDR reconstruido")
                resultado.configure(text=f"Guardado en:\n{salida}")
            else:
                progress.set(0)
                formatos = detectar_formatos()
                if formatos:
                    lista = "\n".join(f"  • {f}" for f in formatos)
                    estado.configure(text="⚠ Formato no compatible")
                    resultado.configure(
                        text=f"Se detectaron estos archivos:\n{lista}\n\nEste programa solo reconstruye CorelDRAW"
                    )
                else:
                    estado.configure(text="Archivo no compatible")
                    resultado.configure(
                        text="No se encontró ningún archivo reconocido\npara reconstruir"
                    )

    except Exception as e:
        progress.set(0)
        estado.configure(text="Error al procesar archivo")
        resultado.configure(text=f"El archivo no es compatible o está dañado.\n{str(e)}")


def iniciar_proceso(ruta):
    estado.configure(text="Procesando...")
    resultado.configure(text="")
    progress.set(0)
    hilo = threading.Thread(target=procesar, args=(ruta,), daemon=True)
    hilo.start()


# -------- EVENTOS --------

def seleccionar_archivo():
    ruta = filedialog.askopenfilename(
        filetypes=[("Archivos compatibles", "*.zip *.rar *.7z"), ("Todos", "*.*")]
    )
    if ruta:
        iniciar_proceso(ruta)


def seleccionar_carpeta():
    ruta = filedialog.askdirectory()
    if ruta:
        iniciar_proceso(ruta)


def drop(event):
    ruta = event.data.strip("{}")
    iniciar_proceso(ruta)


# -------- VENTANA --------

app = TkinterDnD.Tk()
app.title("CDR Reconstructor")
app.geometry("520x540")
app.configure(bg="#0f172a")


# -------- ICONO DE VENTANA --------
try:
    icon_path = os.path.join(ASSETS_DIR, "cdr_reconstructor.ico")
    app.iconbitmap(icon_path)
except:
    pass


# -------- LOGO --------
try:
    logo_path = os.path.join(ASSETS_DIR, "cdr_reconstructor_logo.png")
    logo_img = ctk.CTkImage(
        light_image=Image.open(logo_path),
        dark_image=Image.open(logo_path),
        size=(380, 100)
    )
    logo_label = ctk.CTkLabel(app, image=logo_img, text="")
    logo_label.pack(pady=(20, 5))
except:
    titulo = ctk.CTkLabel(
        app,
        text="CDR RECONSTRUCTOR",
        font=("Segoe UI", 28, "bold"),
        text_color="white"
    )
    titulo.pack(pady=(25, 5))


subtitulo = ctk.CTkLabel(
    app,
    text="Reconstruye archivos CorelDRAW desde ZIP / RAR / 7Z",
    font=("Segoe UI", 13),
    text_color="#9ca3af"
)
subtitulo.pack(pady=(0, 15))


# -------- PANEL CENTRAL --------

panel = ctk.CTkFrame(app, width=420, height=220, corner_radius=15)
panel.pack()
panel.pack_propagate(False)


# -------- BOTONES --------

frame_botones = ctk.CTkFrame(panel, fg_color="transparent")
frame_botones.pack(pady=15)

btn_archivo = ctk.CTkButton(
    frame_botones,
    text="Seleccionar archivo",
    width=180,
    height=40,
    command=seleccionar_archivo
)
btn_archivo.grid(row=0, column=0, padx=10)

btn_carpeta = ctk.CTkButton(
    frame_botones,
    text="Seleccionar carpeta",
    width=180,
    height=40,
    command=seleccionar_carpeta
)
btn_carpeta.grid(row=0, column=1, padx=10)


# -------- ZONA DRAG DROP --------

zona_drop = ctk.CTkLabel(
    panel,
    text="⬇ Arrastra tu archivo aquí ⬇\nZIP  RAR  7Z",
    width=350,
    height=90,
    corner_radius=10,
    fg_color="#1e293b",
    font=("Segoe UI", 14)
)
zona_drop.pack(pady=10)
zona_drop.drop_target_register(DND_FILES)
zona_drop.dnd_bind("<<Drop>>", drop)


# -------- PROGRESS --------

progress = ctk.CTkProgressBar(app, width=400, height=18)
progress.pack(pady=25)
progress.set(0)


# -------- ESTADO --------

estado = ctk.CTkLabel(app, text="Esperando archivo...", font=("Segoe UI", 12))
estado.pack()

resultado = ctk.CTkLabel(app, text="", font=("Segoe UI", 11), text_color="#9ca3af")
resultado.pack(pady=5)


app.mainloop()
