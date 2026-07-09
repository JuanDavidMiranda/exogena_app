import pandas as pd
import streamlit as st

from Utils.excel_reader import leer_excel_seguro


# ============================================================
# CONFIGURACIÓN DE ALIASES / PRIORIDADES DE COLUMNAS
# ============================================================

# ----------------------------
# NOVASOFT / auxiliares compras
# ----------------------------
CLAVES_NOVASOFT = [
    "provee",
    "proveedor",
    "nit proveedor",
    "nit tercero",
    "nit",
    "tercero",
    "documento",
    "identificacion",
    "identificación",
    "cliente"
]

MONTOS_NOVASOFT = [
    "ven_net",       # prioridad alta para compras
    "valor",
    "valor total",
    "monto",
    "cos_tot",
    "saldo",
    "base",
    "debito",
    "débito",
    "credito",
    "crédito",
    "mon_iva",
    "mon_ret",
    "mon_cre"
]


# ----------------------------
# DIAN / compras / facturación
# ----------------------------
CLAVES_DIAN = [
    "nit emisor",     # prioridad alta para compras
    "nit receptor",
    "nit",
    "numero documento",
    "número documento",
    "documento",
    "identificacion",
    "identificación",
    "nombre emisor",
    "nombre receptor",
    "tercero",
    "razon social",
    "razón social"
]

MONTOS_DIAN = [
    "total",          # prioridad alta para compras
    "valor",
    "valor total",
    "monto",
    "cuantia",
    "cuantía",
    "base",
    "pago o abono",
    "pago o abono en cuenta",
    "retencion",
    "retención",
    "saldo",
    "iva",
    "rete iva",
    "rete renta",
    "rete ica"
]


# ============================================================
# HELPERS
# ============================================================

def normalizar_texto(texto):
    """
    Normaliza un texto para facilitar comparación de columnas.
    """
    return str(texto).strip().lower()


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia nombres de columnas sin perder el nombre visible original.
    """
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df


def buscar_columna_prioritaria(df: pd.DataFrame, candidatos: list[str]):
    """
    Busca una columna por prioridad:
    1) coincidencia exacta
    2) coincidencia parcial
    """
    columnas_originales = list(df.columns)
    columnas_normalizadas = {
        normalizar_texto(col): col for col in columnas_originales
    }

    # 1. match exacto por prioridad
    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)
        if candidato_norm in columnas_normalizadas:
            return columnas_normalizadas[candidato_norm]

    # 2. match parcial por prioridad
    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)
        for col in columnas_originales:
            col_norm = normalizar_texto(col)
            if candidato_norm in col_norm:
                return col

    return None


def leer_archivo_tabular(archivo):
    """
    Lee un archivo Excel/CSV de forma segura.
    Usa tu lector robusto para soportar xls/xlsx/csv.
    """
    nombre = getattr(archivo, "name", "").lower()

    if nombre.endswith(".csv"):
        try:
            return pd.read_csv(archivo)
        except UnicodeDecodeError:
            archivo.seek(0)
            return pd.read_csv(archivo, encoding="latin-1")

    return leer_excel_seguro(archivo)


def limpiar_clave(valor):
    """
    Limpia la clave de conciliación.
    Convierte NaN a vacío, quita espacios y homogeneiza.
    """
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def convertir_monto_a_numero(serie: pd.Series) -> pd.Series:
    """
    Convierte una serie a numérico tolerando formatos mixtos.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie.fillna(0)

    # Limpieza básica de símbolos / separadores
    serie = (
        serie.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(serie, errors="coerce").fillna(0)


# ============================================================
# PREPARACIÓN DE DATAFRAMES
# ============================================================

def preparar_df_para_auditoria(df: pd.DataFrame, origen: str) -> pd.DataFrame:
    """
    Estandariza un dataframe para conciliación:
    - detecta columna clave
    - detecta columna monto
    - crea __clave__ y __monto__
    - devuelve columnas originales + columnas técnicas
    """
    df = normalizar_columnas(df)

    origen_norm = normalizar_texto(origen)

    if origen_norm == "novasoft":
        col_clave = buscar_columna_prioritaria(df, CLAVES_NOVASOFT)
        col_monto = buscar_columna_prioritaria(df, MONTOS_NOVASOFT)
    else:
        col_clave = buscar_columna_prioritaria(df, CLAVES_DIAN)
        col_monto = buscar_columna_prioritaria(df, MONTOS_DIAN)

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
    df["__clave__"] = df[col_clave].apply(limpiar_clave)
    df["__monto__"] = convertir_monto_a_numero(df[col_monto])

    # Eliminar filas sin clave útil
    df = df[df["__clave__"].astype(str).str.strip() != ""].copy()

    return df


def consolidar_por_clave(df: pd.DataFrame, nombre_origen: str) -> pd.DataFrame:
    """
    Consolida un dataframe por clave:
    suma el monto por cada tercero / proveedor.
    """
    if df.empty:
        return pd.DataFrame(columns=["__clave__", f"valor_{nombre_origen.lower()}"])

    consolidado = (
        df.groupby("__clave__", as_index=False)["__monto__"]
        .sum()
        .rename(columns={"__monto__": f"valor_{nombre_origen.lower()}"})
    )

    return consolidado


# ============================================================
# SERVICIO PRINCIPAL DE CONCILIACIÓN
# ============================================================

def ejecutar_auditoria_service(archivo_dian, archivo_novasoft):
    """
    Realiza conciliación de compras entre archivo DIAN y archivo Novasoft.

    Retorna un dict con:
    - resumen general
    - detalle consolidado por tercero
    - totales
    """
    try:
        if archivo_dian is None or archivo_novasoft is None:
            raise ValueError("Debes cargar ambos archivos: DIAN y Novasoft.")

        # ----------------------------------------------------
        # 1) Leer archivos
        # ----------------------------------------------------
        df_dian_raw = leer_archivo_tabular(archivo_dian)
        df_novasoft_raw = leer_archivo_tabular(archivo_novasoft)

        if df_dian_raw is None or df_dian_raw.empty:
            raise ValueError("El archivo DIAN no contiene información válida.")

        if df_novasoft_raw is None or df_novasoft_raw.empty:
            raise ValueError("El archivo Novasoft no contiene información válida.")

        # ----------------------------------------------------
        # 2) Preparar dataframes
        # ----------------------------------------------------
        df_dian = preparar_df_para_auditoria(df_dian_raw, "DIAN")
        df_novasoft = preparar_df_para_auditoria(df_novasoft_raw, "Novasoft")

        # ----------------------------------------------------
        # 3) Consolidar por tercero / clave
        # ----------------------------------------------------
        dian_cons = consolidar_por_clave(df_dian, "dian")
        novasoft_cons = consolidar_por_clave(df_novasoft, "novasoft")

        # ----------------------------------------------------
        # 4) Cruce consolidado
        # ----------------------------------------------------
        comparativo = pd.merge(
            dian_cons,
            novasoft_cons,
            on="__clave__",
            how="outer"
        ).fillna(0)

        comparativo["diferencia"] = (
            comparativo["valor_dian"] - comparativo["valor_novasoft"]
        ).round(2)

        # estado
        comparativo["estado"] = comparativo["diferencia"].apply(
            lambda x: "Conciliado" if abs(x) < 0.01 else "Diferencia"
        )

        # ordenar por mayor diferencia
        comparativo = comparativo.sort_values(
            by="diferencia",
            key=lambda s: s.abs(),
            ascending=False
        ).reset_index(drop=True)

        # ----------------------------------------------------
        # 5) KPIs / resumen
        # ----------------------------------------------------
        total_dian = round(comparativo["valor_dian"].sum(), 2)
        total_novasoft = round(comparativo["valor_novasoft"].sum(), 2)
        diferencia_total = round(total_dian - total_novasoft, 2)

        terceros_dian = int(df_dian["__clave__"].nunique())
        terceros_novasoft = int(df_novasoft["__clave__"].nunique())

        registros_dian = int(len(df_dian))
        registros_novasoft = int(len(df_novasoft))

        conciliados = int((comparativo["estado"] == "Conciliado").sum())
        con_diferencia = int((comparativo["estado"] == "Diferencia").sum())

        # ----------------------------------------------------
        # 6) DataFrame de salida bonito
        # ----------------------------------------------------
        detalle = comparativo.rename(columns={
            "__clave__": "Tercero / NIT",
            "valor_dian": "Valor DIAN",
            "valor_novasoft": "Valor Novasoft",
            "diferencia": "Diferencia",
            "estado": "Estado"
        })

        # formato visual del estado
        detalle["Estado"] = detalle["Estado"].replace({
            "Conciliado": "🟢 Conciliado",
            "Diferencia": "🟠 Diferencia"
        })

        # ----------------------------------------------------
        # 7) Respuesta del service
        # ----------------------------------------------------
        return {
            "ok": True,
            "mensaje": "Conciliación procesada correctamente.",
            "resumen": {
                "total_dian": total_dian,
                "total_novasoft": total_novasoft,
                "diferencia_total": diferencia_total,
                "terceros_dian": terceros_dian,
                "terceros_novasoft": terceros_novasoft,
                "registros_dian": registros_dian,
                "registros_novasoft": registros_novasoft,
                "conciliados": conciliados,
                "con_diferencia": con_diferencia,
            },
            "detalle": detalle,
            "detalle_raw": comparativo,
        }

    except Exception as e:
        return {
            "ok": False,
            "mensaje": f"Error al procesar la conciliación: {e}"
        }