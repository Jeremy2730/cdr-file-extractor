import os
import zipfile
import shutil
import rarfile
import py7zr

from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import messagebox


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")


def limpiar_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)


def es_paquete_corel(carpeta):

    elementos = os.listdir(carpeta)

    return "content" in elementos and "mimetype" in elementos


def reconstruir_cdr(carpeta):

    nombre = os.path.basename(carpeta)

    salida = os.path.join(BASE_DIR, nombre + "_FIX.cdr")

    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as zipf:

        for raiz, subcarpetas, archivos in os.walk(carpeta):

            for archivo in archivos:

                ruta = os.path.join(raiz, archivo)

                relativa = os.path.relpath(ruta, carpeta)

                zipf.write(ruta, relativa)

    return salida


def extraer_archivo(archivo):

    limpiar_temp()

    if archivo.endswith(".zip"):

        with zipfile.ZipFile(archivo, 'r') as z:
            z.extractall(TEMP_DIR)

    elif archivo.endswith(".rar"):

        with rarfile.RarFile(archivo) as r:
            r.extractall(TEMP_DIR)

    elif archivo.endswith(".7z"):

        with py7zr.SevenZipFile(archivo, 'r') as z:
            z.extractall(TEMP_DIR)


def buscar_paquete():

    for raiz, dirs, files in os.walk(TEMP_DIR):

        if "content" in dirs and "mimetype" in files:

            return raiz

    return None


def procesar_archivo(ruta):

    if os.path.isdir(ruta):

        if es_paquete_corel(ruta):

            salida = reconstruir_cdr(ruta)

            messagebox.showinfo("Listo", f"CDR creado:\n{salida}")

        else:

            messagebox.showerror("Error", "No es un paquete Corel válido")

    else:

        extraer_archivo(ruta)

        carpeta = buscar_paquete()

        if carpeta:

            salida = reconstruir_cdr(carpeta)

            messagebox.showinfo("Listo", f"CDR creado:\n{salida}")

        else:

            messagebox.showerror("Error", "No se encontró paquete Corel")


def drop(event):

    archivo = event.data.strip("{}")

    procesar_archivo(archivo)


app = TkinterDnD.Tk()
app.title("CDR Reconstructor")
app.geometry("400x250")

label = tk.Label(
    app,
    text="Arrastra aquí tu archivo\nZIP / RAR / 7Z / Carpeta",
    font=("Arial", 14),
    width=30,
    height=8,
    relief="ridge"
)

label.pack(pady=40)

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", drop)

app.mainloop()