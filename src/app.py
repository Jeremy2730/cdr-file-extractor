import os
import zipfile
import shutil
import threading

import rarfile
import py7zr

import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES


# ---------- Config UI ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------- Rutas ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


# ---------- Utilidades ----------
def limpiar_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)


def es_paquete_corel(carpeta):
    try:
        elementos = os.listdir(carpeta)
        return "content" in elementos and "mimetype" in elementos
    except Exception:
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

    archivo = archivo.lower()

    if archivo.endswith(".zip"):
        with zipfile.ZipFile(archivo, "r") as z:
            z.extractall(TEMP_DIR)

    elif archivo.endswith(".rar"):
        with rarfile.RarFile(archivo) as r:
            r.extractall(TEMP_DIR)

    elif archivo.endswith(".7z"):
        with py7zr.SevenZipFile(archivo, "r") as z:
            z.extractall(TEMP_DIR)


def buscar_paquete():
    for raiz, dirs, files in os.walk(TEMP_DIR):
        if "content" in dirs and "mimetype" in files:
            return raiz
    return None


# ---------- Lógica principal ----------
def procesar(ruta):

    progress.set(0.1)
    estado.configure(text="Procesando...")

    if os.path.isdir(ruta):

        progress.set(0.4)

        if es_paquete_corel(ruta):
            salida = reconstruir_cdr(ruta)

            progress.set(1)
            estado.configure(text="✔ CDR creado")
            resultado.configure(text=f"Guardado en:\n{salida}")

        else:
            estado.configure(text="No es paquete Corel")

    else:

        progress.set(0.3)
        extraer_archivo(ruta)

        progress.set(0.6)

        carpeta = buscar_paquete()

        if carpeta:
            salida = reconstruir_cdr(carpeta)

            progress.set(1)
            estado.configure(text="✔ CDR creado")
            resultado.configure(text=f"Guardado en:\n{salida}")

        else:
            estado.configure(text="No se encontró paquete Corel")


def iniciar_proceso(ruta):
    threading.Thread(target=procesar, args=(ruta,), daemon=True).start()


# ---------- Eventos ----------
def seleccionar_archivo():
    ruta = filedialog.askopenfilename(
        filetypes=[
            ("Archivos compatibles", "*.zip *.rar *.7z"),
            ("Todos", "*.*")
        ]
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


# ---------- Ventana ----------
app = TkinterDnD.Tk()
app.title("CDR Reconstructor")
app.geometry("500x420")


titulo = ctk.CTkLabel(app, text="CDR Reconstructor", font=("Arial", 24))
titulo.pack(pady=20)


info = ctk.CTkLabel(
    app,
    text="Arrastra aquí ZIP / RAR / 7Z\n o selecciona archivo o carpeta",
    font=("Arial", 14)
)
info.pack(pady=10)


frame_botones = ctk.CTkFrame(app)
frame_botones.pack(pady=10)


btn_archivo = ctk.CTkButton(
    frame_botones,
    text="Seleccionar archivo",
    command=seleccionar_archivo
)
btn_archivo.grid(row=0, column=0, padx=10, pady=10)


btn_carpeta = ctk.CTkButton(
    frame_botones,
    text="Seleccionar carpeta",
    command=seleccionar_carpeta
)
btn_carpeta.grid(row=0, column=1, padx=10, pady=10)


zona_drop = ctk.CTkLabel(
    app,
    text="⬇ Arrastra aquí ⬇",
    height=100,
    width=350,
    corner_radius=10
)
zona_drop.pack(pady=20)

zona_drop.drop_target_register(DND_FILES)
zona_drop.dnd_bind("<<Drop>>", drop)


progress = ctk.CTkProgressBar(app, width=350)
progress.pack(pady=10)
progress.set(0)


estado = ctk.CTkLabel(app, text="Esperando archivo...")
estado.pack(pady=5)


resultado = ctk.CTkLabel(app, text="")
resultado.pack(pady=5)


app.mainloop()