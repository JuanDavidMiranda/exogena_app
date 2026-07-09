import pandas as pd


def _obtener_engine_excel(archivo):
    nombre_archivo = ""

    if hasattr(archivo, "name"):
        nombre_archivo = archivo.name.lower()
    else:
        nombre_archivo = str(archivo).lower()

    if nombre_archivo.endswith(".xlsx"):
        return "openpyxl"
    elif nombre_archivo.endswith(".xls"):
        return "xlrd"
    else:
        raise ValueError(
            f"Formato de archivo no soportado: {nombre_archivo}. "
            "Solo se permiten archivos .xlsx o .xls"
        )


def leer_excel_seguro(archivo, **kwargs):
    engine = _obtener_engine_excel(archivo)
    return pd.read_excel(archivo, engine=engine, **kwargs)


def abrir_excel_seguro(archivo):
    engine = _obtener_engine_excel(archivo)
    return pd.ExcelFile(archivo, engine=engine)