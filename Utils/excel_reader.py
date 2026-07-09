import pandas as pd


PATRONES_ENCABEZADO = [
    "nit emisor",
    "nombre emisor",
    "nit receptor",
    "nombre receptor",
    "total",
    "base",
    "iva",
    "provee",
    "proveedor",
    "ven_net",
    "valor",
    "tercero",
]


def normalizar_texto(valor):
    return str(valor).strip().lower()


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


def _limpiar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def _score_fila_como_header(fila) -> int:
    """
    Puntúa una fila según cuántas señales de encabezado útil contiene.
    """
    score = 0
    for celda in fila:
        texto = normalizar_texto(celda)
        if texto in ("", "nan", "none"):
            continue

        for patron in PATRONES_ENCABEZADO:
            if patron in texto:
                score += 1
                break

    return score


def _detectar_mejor_header_en_df(raw_df: pd.DataFrame):
    """
    Revisa las primeras filas de una hoja y detecta cuál parece ser
    el encabezado real. Devuelve un DataFrame reconstruido con esa fila
    como header.
    """
    if raw_df is None or raw_df.empty:
        return None

    mejor_score = -1
    mejor_fila_idx = None

    limite = min(len(raw_df), 25)

    for i in range(limite):
        fila = raw_df.iloc[i].tolist()

        # contar celdas no vacías
        no_vacios = sum(
            1 for x in fila
            if str(x).strip() not in ("", "nan", "None")
        )

        if no_vacios == 0:
            continue

        score = _score_fila_como_header(fila)

        if score > mejor_score:
            mejor_score = score
            mejor_fila_idx = i

    # Si no encontró algo con al menos 2 señales, no confiar
    if mejor_fila_idx is None or mejor_score < 2:
        return None

    header = raw_df.iloc[mejor_fila_idx].tolist()
    data = raw_df.iloc[mejor_fila_idx + 1:].copy()
    data.columns = header
    data = data.reset_index(drop=True)

    # eliminar columnas completamente vacías
    data = data.dropna(axis=1, how="all")

    # eliminar columnas cuyo nombre sea NaN
    data = data.loc[:, ~pd.isna(data.columns)]

    return _limpiar_columnas(data)


def _evaluar_df_util(df: pd.DataFrame) -> int:
    """
    Puntúa un DataFrame según si parece útil para conciliación.
    """
    if df is None or df.empty:
        return -1

    score = 0
    columnas = [normalizar_texto(col) for col in df.columns]

    for col in columnas:
        for patron in PATRONES_ENCABEZADO:
            if patron in col:
                score += 1
                break

    # premio por tener filas
    if len(df) > 0:
        score += 1

    return score


def leer_excel_seguro(archivo, **kwargs):
    """
    Lee un Excel de forma robusta:
    - soporta xls/xlsx
    - revisa todas las hojas
    - detecta automáticamente la fila real del encabezado
    - devuelve la hoja / estructura más útil para conciliación
    """
    engine = _obtener_engine_excel(archivo)

    # Si el usuario manda explícitamente sheet_name o header,
    # respetamos ese comportamiento tradicional.
    if "sheet_name" in kwargs or "header" in kwargs:
        return pd.read_excel(archivo, engine=engine, **kwargs)

    excel_file = pd.ExcelFile(archivo, engine=engine)

    mejor_df = None
    mejor_score = -1

    for hoja in excel_file.sheet_names:
        try:
            # leer la hoja cruda, sin encabezado
            raw_df = pd.read_excel(
                archivo,
                sheet_name=hoja,
                engine=engine,
                header=None
            )

            candidato = _detectar_mejor_header_en_df(raw_df)

            if candidato is None or candidato.empty:
                continue

            score = _evaluar_df_util(candidato)

            if score > mejor_score:
                mejor_score = score
                mejor_df = candidato

        except Exception:
            continue

        finally:
            # importante para UploadedFile de Streamlit
            try:
                archivo.seek(0)
            except Exception:
                pass

    # Fallback: si no se detectó nada inteligente,
    # usar la primera hoja como siempre.
    if mejor_df is None:
        try:
            archivo.seek(0)
        except Exception:
            pass

        return pd.read_excel(archivo, engine=engine, **kwargs)

    return mejor_df


def abrir_excel_seguro(archivo):
    engine = _obtener_engine_excel(archivo)
    return pd.ExcelFile(archivo, engine=engine)