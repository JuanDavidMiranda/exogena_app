import pandas as pd

from Utils.excel_reader import leer_excel_seguro


COLUMNAS_CLAVE_POSIBLES = [
    "concepto",
    "cuenta",
    "codigo cuenta",
    "código cuenta",
    "cuenta contable",
    "nit",
    "nit tercero",
    "nit proveedor",
    "documento",
    "numero documento",
    "número documento",
    "identificacion",
    "identificación",
    "tercero",
    "nombre tercero",
    "proveedor",
    "provee",
    "cod provee",
    "codigo proveedor",
    "código proveedor",
    "razon social",
    "razón social",
    "razon social tercero",
    "razón social tercero"
]

COLUMNAS_MONTO_POSIBLES = [
    "valor",
    "valor total",
    "monto",
    "cuantia",
    "cuantía",
    "saldo",
    "saldo final",
    "base",
    "debito",
    "débito",
    "credito",
    "crédito",
    "pago o abono",
    "pago o abono en cuenta",
    "retencion",
    "retención"
]


def normalizar_texto(texto):
    return str(texto).strip().lower()


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def leer_archivo_tabular(archivo):
    nombre = archivo.name.lower()

    if nombre.endswith(".csv"):
        try:
            return pd.read_csv(archivo)
        except UnicodeDecodeError:
            archivo.seek(0)
            return pd.read_csv(archivo, encoding="latin-1")

    return leer_excel_seguro(archivo)


def encontrar_columna(df: pd.DataFrame, candidatos: list[str]):
    """
    Busca una columna por coincidencia exacta o parcial.
    Primero intenta match exacto.
    Si no encuentra, busca si el candidato está contenido en el nombre de la columna.
    """
    columnas_originales = list(df.columns)
    columnas_normalizadas = {
        normalizar_texto(col): col for col in columnas_originales
    }

    # 1) Coincidencia exacta
    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)
        if candidato_norm in columnas_normalizadas:
            return columnas_normalizadas[candidato_norm]

    # 2) Coincidencia parcial: "nit" dentro de "nit tercero", etc.
    for col in columnas_originales:
        col_norm = normalizar_texto(col)
        for candidato in candidatos:
            candidato_norm = normalizar_texto(candidato)
            if candidato_norm in col_norm:
                return col

    return None


def preparar_df_para_auditoria(df: pd.DataFrame, origen: str) -> pd.DataFrame:
    df = normalizar_columnas(df)

    col_clave = encontrar_columna(df, COLUMNAS_CLAVE_POSIBLES)
    col_monto = encontrar_columna(df, COLUMNAS_MONTO_POSIBLES)

    if not col_clave:
        raise ValueError(
        f"No se encontró una columna clave válida en el archivo {origen}. "
        f"Columnas detectadas: {', '.join(df.columns.astype(str))}"
        )

    if not col_monto:
        raise ValueError(
        f"No se encontró una columna de monto válida en el archivo {origen}. "
        f"Columnas detectadas: {', '.join(df.columns.astype(str))}"
        )

    df = df.copy()

    df["__clave__"] = df[col_clave].astype(str).str.strip()
    df["__monto__"] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0)

    return df


def ejecutar_auditoria_service(archivo_novasoft, archivo_dian):
    # ==========================
    # Lectura de archivos
    # ==========================
    df_novasoft = leer_archivo_tabular(archivo_novasoft)
    df_dian = leer_archivo_tabular(archivo_dian)

    if df_novasoft.empty:
        raise ValueError("El archivo de Novasoft no contiene registros.")
    if df_dian.empty:
        raise ValueError("El archivo DIAN no contiene registros.")

    # ==========================
    # Preparación
    # ==========================
    df_novasoft = preparar_df_para_auditoria(df_novasoft, "Novasoft")
    df_dian = preparar_df_para_auditoria(df_dian, "DIAN")

    # Nos quedamos con clave + monto + columnas originales
    novasoft_base = df_novasoft.copy()
    dian_base = df_dian.copy()

    # ==========================
    # Cruce principal
    # ==========================
    merge_df = dian_base.merge(
        novasoft_base,
        on="__clave__",
        how="outer",
        suffixes=("_dian", "_novasoft"),
        indicator=True
    )

    # ==========================
    # Solo en DIAN
    # ==========================
    solo_dian = merge_df[merge_df["_merge"] == "left_only"].copy()

    # ==========================
    # Solo en Novasoft
    # ==========================
    solo_novasoft = merge_df[merge_df["_merge"] == "right_only"].copy()

    # ==========================
    # Diferencias de montos
    # ==========================
    comunes = merge_df[merge_df["_merge"] == "both"].copy()

    if "__monto___dian" in comunes.columns and "__monto___novasoft" in comunes.columns:
        dif_montos = comunes[
            comunes["__monto___dian"].fillna(0) != comunes["__monto___novasoft"].fillna(0)
        ].copy()
    else:
        dif_montos = pd.DataFrame()

    # ==========================
    # Limpieza de columnas técnicas
    # ==========================
    columnas_ocultar = ["_merge"]

    def limpiar_resultado(df):
        if df.empty:
            return df

        df = df.copy()
        columnas_finales = [c for c in df.columns if c not in columnas_ocultar]
        return df[columnas_finales]

    dif_montos = limpiar_resultado(dif_montos)
    solo_dian = limpiar_resultado(solo_dian)
    solo_novasoft = limpiar_resultado(solo_novasoft)

    # ==========================
    # Resumen
    # ==========================
    resumen = {
        "diferencias_montos": len(dif_montos),
        "solo_dian": len(solo_dian),
        "solo_novasoft": len(solo_novasoft),
    }

    return {
        "resumen": resumen,
        "dif_montos": dif_montos,
        "solo_dian": solo_dian,
        "solo_novasoft": solo_novasoft,
    }