import os
import zipfile
import shutil

ruta_base = os.path.dirname(os.path.abspath(__file__))


def es_paquete_corel(carpeta):
    elementos = os.listdir(carpeta)

    return (
        "content" in elementos
        and "mimetype" in elementos
    )


def crear_cdr(carpeta, salida):

    with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as zipf:

        for raiz, subcarpetas, archivos in os.walk(carpeta):

            for archivo in archivos:

                ruta_completa = os.path.join(raiz, archivo)

                ruta_relativa = os.path.relpath(ruta_completa, carpeta)

                zipf.write(ruta_completa, ruta_relativa)

    print("✔ CDR creado:", salida)


def extraer_zip(archivo, destino):

    with zipfile.ZipFile(archivo, 'r') as zip_ref:
        zip_ref.extractall(destino)

    print("📦 ZIP extraído:", archivo)


for elemento in os.listdir(ruta_base):

    ruta_elemento = os.path.join(ruta_base, elemento)

    # Detectar carpeta
    if os.path.isdir(ruta_elemento):

        if es_paquete_corel(ruta_elemento):

            salida = os.path.join(ruta_base, elemento + "_FIX.cdr")

            crear_cdr(ruta_elemento, salida)

    # Detectar ZIP
    elif elemento.lower().endswith(".zip"):

        carpeta_temp = os.path.join(ruta_base, "temp_extract")

        if os.path.exists(carpeta_temp):
            shutil.rmtree(carpeta_temp)

        os.makedirs(carpeta_temp)

        extraer_zip(ruta_elemento, carpeta_temp)

        for sub in os.listdir(carpeta_temp):

            posible = os.path.join(carpeta_temp, sub)

            if os.path.isdir(posible) and es_paquete_corel(posible):

                salida = os.path.join(ruta_base, sub + "_FIX.cdr")

                crear_cdr(posible, salida)