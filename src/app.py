import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox


def reconstruir_cdr(carpeta, salida):

    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as zipf:

        for raiz, subcarpetas, archivos in os.walk(carpeta):

            for archivo in archivos:

                ruta = os.path.join(raiz, archivo)

                relativa = os.path.relpath(ruta, carpeta)

                zipf.write(ruta, relativa)


def seleccionar_carpeta():

    carpeta = filedialog.askdirectory()

    if not carpeta:
        return

    nombre = os.path.basename(carpeta)

    salida = os.path.join(os.path.dirname(carpeta), nombre + "_FIX.cdr")

    reconstruir_cdr(carpeta, salida)

    messagebox.showinfo("Listo", f"CDR reconstruido:\n{salida}")


ventana = tk.Tk()
ventana.title("CDR Reconstructor")
ventana.geometry("350x200")

titulo = tk.Label(ventana, text="CDR Reconstructor", font=("Arial", 16))
titulo.pack(pady=20)

boton = tk.Button(
    ventana,
    text="Seleccionar carpeta Corel",
    command=seleccionar_carpeta,
    height=2,
    width=25
)

boton.pack(pady=20)

ventana.mainloop()