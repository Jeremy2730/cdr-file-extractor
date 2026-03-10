import os
import zipfile
import shutil
import threading

import rarfile
import py7zr

import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES


# -------- CONFIGURACION UI --------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -------- RUTAS --------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


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


def detectar_formatos():

    formatos_detectados = []

    for raiz, dirs, files in os.walk(TEMP_DIR):

        for archivo in files:

            ext = os.path.splitext(archivo)[1].lower()

            if ext == ".ai":
                formatos_detectados.append("Illustrator (.ai)")

            elif ext == ".psd":
                formatos_detectados.append("Photoshop (.psd)")

            elif ext == ".svg":
                formatos_detectados.append("SVG")

            elif ext == ".eps":
                formatos_detectados.append("EPS")

    return list(set(formatos_detectados))



# -------- LOGICA --------

def procesar(ruta):

    try:

        progress.set(0.1)

        estado.configure(text="Analizando archivo...")

        # ----- SI ES CARPETA -----

        if os.path.isdir(ruta):

            progress.set(0.4)

            if es_paquete_corel(ruta):

                salida = reconstruir_cdr(ruta)

                progress.set(1)

                estado.configure(text="✔ CDR reconstruido")

                resultado.configure(
                    text=f"Guardado en:\n{salida}"
                )

            else:

                progress.set(0)

                formatos = detectar_formatos()

                if formatos:

                    lista = ", ".join(formatos)

                    estado.configure(text="⚠ Archivo no compatible")

                    resultado.configure(
                        text=f"Se detectaron archivos:\n{lista}\n\nEste programa solo reconstruye CorelDRAW"
                    )

                else:

                    estado.configure(text="Archivo no compatible")

                    resultado.configure(
                        text="No se encontró ningún archivo CorelDRAW\npara reconstruir"
                    )

        # ----- SI ES ARCHIVO -----

        else:

            progress.set(0.3)

            extraer_archivo(ruta)

            progress.set(0.6)

            carpeta = buscar_paquete()

            if carpeta:

                salida = reconstruir_cdr(carpeta)

                progress.set(1)

                estado.configure(text="✔ CDR reconstruido")

                resultado.configure(
                    text=f"Guardado en:\n{salida}"
                )

            else:

                progress.set(0)

                estado.configure(text="Archivo no compatible")

                resultado.configure(
                    text="No se encontró ningún archivo Corel\npara reconstruir"
                )

    except Exception as e:

        progress.set(0)

        estado.configure(text="Error al procesar archivo")

        resultado.configure(
            text="El archivo no es compatible\n o está dañado"
        )

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

app.geometry("520x460")

app.configure(bg="#0f172a")


# -------- TITULO --------

titulo = ctk.CTkLabel(
    app,
    text="CDR RECONSTRUCTOR",
    font=("Segoe UI", 28, "bold"),
    text_color="white"
)

titulo.pack(pady=(25,5))


subtitulo = ctk.CTkLabel(
    app,
    text="Reconstruye archivos CorelDRAW desde ZIP / RAR / 7Z",
    font=("Segoe UI", 13),
    text_color="#9ca3af"
)

subtitulo.pack(pady=(0,20))


# -------- PANEL CENTRAL --------

panel = ctk.CTkFrame(
    app,
    width=420,
    height=220,
    corner_radius=15
)

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

progress = ctk.CTkProgressBar(
    app,
    width=400,
    height=18
)

progress.pack(pady=25)

progress.set(0)


# -------- ESTADO --------

estado = ctk.CTkLabel(
    app,
    text="Esperando archivo...",
    font=("Segoe UI", 12)
)

estado.pack()


resultado = ctk.CTkLabel(
    app,
    text="",
    font=("Segoe UI", 11),
    text_color="#9ca3af"
)

resultado.pack(pady=5)


app.mainloop()