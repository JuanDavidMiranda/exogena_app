import pandas as pd

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
    return str(texto).strip().lower()


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
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

    # 1. Match exacto por prioridad
    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)
        if candidato_norm in columnas_normalizadas:
            return columnas_normalizadas[candidato_norm]

    # 2. Match parcial por prioridad
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


def construir_observacion(row) -> str:
    """
    Etiqueta funcional para entender el resultado de la conciliación.
    """
    valor_dian = float(row.get("valor_dian", 0) or 0)
    valor_novasoft = float(row.get("valor_novasoft", 0) or 0)
    diferencia = float(row.get("diferencia", 0) or 0)

    if valor_dian > 0 and valor_novasoft == 0:
        return "Solo en DIAN"

    if valor_novasoft > 0 and valor_dian == 0:
        return "Solo en Novasoft"

    if abs(diferencia) < 0.01:
        return "Conciliado"

    if diferencia > 0:
        return "Monto DIAN mayor"

    return "Monto Novasoft mayor"


# ============================================================
# SERVICIO PRINCIPAL DE CONCILIACIÓN
# ============================================================

def ejecutar_auditoria_service(archivo_dian, archivo_novasoft):
    """
    Realiza conciliación de compras entre archivo DIAN y archivo Novasoft.

    Retorna:
    - resumen general
    - detalle consolidado por tercero
    - dif_montos
    - solo_dian
    - solo_novasoft
    - conciliados_df
    """
    try:
        if archivo_dian is None or archivo_novasoft is None:
            raise ValueError("Debes cargar ambos archivos: DIAN y Novasoft.")

        # ====================================================
        # 1) Leer archivos
        # ====================================================
        df_dian_raw = leer_archivo_tabular(archivo_dian)
        df_novasoft_raw = leer_archivo_tabular(archivo_novasoft)
        print("\n========== DEBUG DIAN RAW ==========")
        print("Columnas DIAN RAW:", list(df_dian_raw.columns))
        print("Shape DIAN RAW:", df_dian_raw.shape)
        print(df_dian_raw.head(15).to_string())
        print("====================================\n")
        print("\n========== DEBUG NOVASOFT RAW ==========")
        print("Columnas NOVASOFT RAW:", list(df_novasoft_raw.columns))
        print("Shape NOVASOFT RAW:", df_novasoft_raw.shape)
        print(df_novasoft_raw.head(10).to_string())
        print("========================================\n")

        if df_dian_raw is None or df_dian_raw.empty:
            raise ValueError("El archivo DIAN no contiene información válida.")

        if df_novasoft_raw is None or df_novasoft_raw.empty:
            raise ValueError("El archivo Novasoft no contiene información válida.")

        # ====================================================
        # 2) Preparar dataframes
        # ====================================================
        df_dian = preparar_df_para_auditoria(df_dian_raw, "DIAN")
        df_novasoft = preparar_df_para_auditoria(df_novasoft_raw, "Novasoft")

        # ====================================================
        # 3) Consolidar por clave
        # ====================================================
        dian_cons = consolidar_por_clave(df_dian, "dian")
        novasoft_cons = consolidar_por_clave(df_novasoft, "novasoft")

        # ====================================================
        # 4) Cruce consolidado
        # ====================================================
        comparativo = pd.merge(
            dian_cons,
            novasoft_cons,
            on="__clave__",
            how="outer"
        ).fillna(0)

        comparativo["valor_dian"] = pd.to_numeric(
            comparativo["valor_dian"], errors="coerce"
        ).fillna(0)

        comparativo["valor_novasoft"] = pd.to_numeric(
            comparativo["valor_novasoft"], errors="coerce"
        ).fillna(0)

        comparativo["diferencia"] = (
            comparativo["valor_dian"] - comparativo["valor_novasoft"]
        ).round(2)

        comparativo["observacion"] = comparativo.apply(construir_observacion, axis=1)

        comparativo["estado"] = comparativo["observacion"].apply(
            lambda obs: "Conciliado" if obs == "Conciliado" else "Diferencia"
        )

        # Ordenar por mayor diferencia
        comparativo = comparativo.sort_values(
            by="diferencia",
            key=lambda s: s.abs(),
            ascending=False
        ).reset_index(drop=True)

        # ====================================================
        # 5) Subconjuntos funcionales
        # ====================================================
        solo_dian = comparativo[
            (comparativo["valor_dian"] > 0) &
            (comparativo["valor_novasoft"] == 0)
        ].copy()

        solo_novasoft = comparativo[
            (comparativo["valor_novasoft"] > 0) &
            (comparativo["valor_dian"] == 0)
        ].copy()

        dif_montos = comparativo[
            (comparativo["valor_dian"] > 0) &
            (comparativo["valor_novasoft"] > 0) &
            (comparativo["diferencia"].abs() >= 0.01)
        ].copy()

        conciliados_df = comparativo[
            comparativo["diferencia"].abs() < 0.01
        ].copy()

        # ====================================================
        # 6) KPIs / resumen
        # ====================================================
        total_dian = round(comparativo["valor_dian"].sum(), 2)
        total_novasoft = round(comparativo["valor_novasoft"].sum(), 2)
        diferencia_total = round(total_dian - total_novasoft, 2)

        terceros_dian = int(df_dian["__clave__"].nunique())
        terceros_novasoft = int(df_novasoft["__clave__"].nunique())

        registros_dian = int(len(df_dian))
        registros_novasoft = int(len(df_novasoft))

        conciliados = int((comparativo["estado"] == "Conciliado").sum())
        con_diferencia = int((comparativo["estado"] == "Diferencia").sum())

        # ====================================================
        # 7) DataFrames bonitos de salida
        # ====================================================
        detalle = comparativo.rename(columns={
            "__clave__": "Tercero / NIT",
            "valor_dian": "Valor DIAN",
            "valor_novasoft": "Valor Novasoft",
            "diferencia": "Diferencia",
            "estado": "Estado",
            "observacion": "Observación"
        }).copy()

        detalle["Estado"] = detalle["Estado"].replace({
            "Conciliado": "🟢 Conciliado",
            "Diferencia": "🟠 Diferencia"
        })

        def formatear_subtabla(df_sub: pd.DataFrame) -> pd.DataFrame:
            if df_sub.empty:
                return pd.DataFrame(columns=[
                    "Tercero / NIT",
                    "Valor DIAN",
                    "Valor Novasoft",
                    "Diferencia",
                    "Observación"
                ])

            out = df_sub.rename(columns={
                "__clave__": "Tercero / NIT",
                "valor_dian": "Valor DIAN",
                "valor_novasoft": "Valor Novasoft",
                "diferencia": "Diferencia",
                "observacion": "Observación"
            }).copy()

            columnas = [
                "Tercero / NIT",
                "Valor DIAN",
                "Valor Novasoft",
                "Diferencia",
                "Observación"
            ]
            return out[columnas]

        solo_dian_out = formatear_subtabla(solo_dian)
        solo_novasoft_out = formatear_subtabla(solo_novasoft)
        dif_montos_out = formatear_subtabla(dif_montos)
        conciliados_out = formatear_subtabla(conciliados_df)

        # ====================================================
        # 8) Respuesta del service
        # ====================================================
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
                "solo_dian": len(solo_dian_out),
                "solo_novasoft": len(solo_novasoft_out),
                "dif_montos": len(dif_montos_out),
            },
            "detalle": detalle,
            "detalle_raw": comparativo,
            "solo_dian": solo_dian_out,
            "solo_novasoft": solo_novasoft_out,
            "dif_montos": dif_montos_out,
            "conciliados_df": conciliados_out,
        }

    except Exception as e:
        return {
            "ok": False,
            "mensaje": f"Error al procesar la conciliación: {e}"
        }