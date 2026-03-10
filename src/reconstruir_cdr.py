import os
import zipfile

ruta_base = os.path.dirname(os.path.abspath(__file__))

def crear_cdr(carpeta, salida):

    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as zipf:

        for raiz, subcarpetas, archivos in os.walk(carpeta):

            for archivo in archivos:

                ruta_completa = os.path.join(raiz, archivo)

                ruta_relativa = os.path.relpath(ruta_completa, carpeta)

                zipf.write(ruta_completa, ruta_relativa)

    print("CDR creado:", salida)


for elemento in os.listdir(ruta_base):

    ruta_elemento = os.path.join(ruta_base, elemento)

    if os.path.isdir(ruta_elemento):

        nombre = os.path.basename(ruta_elemento)

        salida = os.path.join(ruta_base, nombre + "_FIX.cdr")

        crear_cdr(ruta_elemento, salida)