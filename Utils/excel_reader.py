import pandas as pd


def leer_excel_seguro(archivo, **kwargs):
    """
    Lee archivos Excel .xlsx o .xls detectando automáticamente el engine.

    Parámetros:
        archivo: archivo cargado desde Streamlit o ruta al archivo
        **kwargs: argumentos extra para pd.read_excel (sheet_name, header, etc.)

    Retorna:
        DataFrame o diccionario de DataFrames según kwargs
    """
    nombre_archivo = ""

    # Si viene de Streamlit, normalmente tiene atributo .name
    if hasattr(archivo, "name"):
        nombre_archivo = archivo.name.lower()
    else:
        nombre_archivo = str(archivo).lower()

    if nombre_archivo.endswith(".xlsx"):
        return pd.read_excel(archivo, engine="openpyxl", **kwargs)

    elif nombre_archivo.endswith(".xls"):
        return pd.read_excel(archivo, engine="xlrd", **kwargs)

    else:
        raise ValueError(
            f"Formato de archivo no soportado: {nombre_archivo}. "
            "Solo se permiten archivos .xlsx o .xls"
        )