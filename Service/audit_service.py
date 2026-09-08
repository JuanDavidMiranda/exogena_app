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
    "cliente",
]

MONTOS_NOVASOFT = [
    "ven_net",
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
    "mon_cre",
]

# Columnas candidatas para identificar una factura/documento.
FACTURA_NOVASOFT = [
    "numero factura",
    "número factura",
    "numero de factura",
    "número de factura",
    "factura",
    "documento",
    "numero documento",
    "número documento",
    "no factura",
    "no. factura",
    "nro factura",
    "nro. factura",
    "consecutivo",
]

# ----------------------------
# DIAN / compras / facturación
# ----------------------------
CLAVES_DIAN = [
    "nit emisor",
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
    "razón social",
]

MONTOS_DIAN = [
    "total",
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
    "rete ica",
]

FACTURA_DIAN = [
    "numero factura",
    "número factura",
    "numero de factura",
    "número de factura",
    "factura",
    "numero documento",
    "número documento",
    "documento",
    "no factura",
    "no. factura",
    "nro factura",
    "nro. factura",
    "consecutivo",
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
    if hasattr(archivo, "seek"):
        try:
            archivo.seek(0)
        except Exception:
            pass

    nombre = getattr(archivo, "name", "").lower()

    if nombre.endswith(".csv"):
        try:
            return pd.read_csv(archivo)
        except UnicodeDecodeError:
            if hasattr(archivo, "seek"):
                try:
                    archivo.seek(0)
                except Exception:
                    pass
            return pd.read_csv(archivo, encoding="latin-1")

    return leer_excel_seguro(archivo)


def obtener_columnas_disponibles(archivo):
    """
    Devuelve la lista de columnas detectadas en un archivo cargado.
    """
    df = leer_archivo_tabular(archivo)

    if df is None or df.empty:
        return []

    return [str(col).strip() for col in df.columns if str(col).strip() != ""]


def encontrar_columna_por_nombre(df: pd.DataFrame, nombre) -> str | None:
    """
    Busca una columna exacta o tolerando diferencias de formato.
    """
    if nombre is None:
        return None

    nombre_str = str(nombre).strip()

    if nombre_str == "":
        return None

    columnas_originales = list(df.columns)
    columnas_map = {str(col).strip(): col for col in columnas_originales}

    if nombre_str in columnas_map:
        return columnas_map[nombre_str]

    for col in columnas_originales:
        if normalizar_texto(col) == normalizar_texto(nombre_str):
            return col

    return None


def sugerir_columnas_por_origen(df: pd.DataFrame, origen: str):
    """
    Sugiere:
    - columna clave/tercero
    - columna monto
    - columna identificadora de factura
    """
    origen_norm = normalizar_texto(origen)

    if origen_norm == "novasoft":
        col_clave = buscar_columna_prioritaria(df, CLAVES_NOVASOFT)
        col_monto = buscar_columna_prioritaria(df, MONTOS_NOVASOFT)
        col_factura = buscar_columna_prioritaria(df, FACTURA_NOVASOFT)
    else:
        col_clave = buscar_columna_prioritaria(df, CLAVES_DIAN)
        col_monto = buscar_columna_prioritaria(df, MONTOS_DIAN)
        col_factura = buscar_columna_prioritaria(df, FACTURA_DIAN)

    return {
        "col_clave": col_clave,
        "col_monto": col_monto,
        "col_factura": col_factura,
    }


def analizar_archivos_para_auditoria(archivo_dian, archivo_novasoft):
    """
    Devuelve las columnas disponibles y las sugerencias de mapeo
    para ambos archivos.
    """
    df_dian = leer_archivo_tabular(archivo_dian)
    df_novasoft = leer_archivo_tabular(archivo_novasoft)

    columnas_dian = obtener_columnas_disponibles(archivo_dian)
    columnas_novasoft = obtener_columnas_disponibles(archivo_novasoft)

    sugerencia_dian = sugerir_columnas_por_origen(df_dian, "DIAN")
    sugerencia_novasoft = sugerir_columnas_por_origen(df_novasoft, "Novasoft")

    return {
        "columnas_dian": columnas_dian,
        "columnas_novasoft": columnas_novasoft,
        "sugerencia_dian": sugerencia_dian,
        "sugerencia_novasoft": sugerencia_novasoft,
    }


def limpiar_clave(valor):
    """
    Limpia una clave de conciliación.
    """
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def normalizar_identificador_factura(valor):
    """
    Normaliza el identificador de factura para permitir comparar
    valores provenientes de Excel con pequeñas diferencias de formato.

    Ejemplos:
        12345      -> 12345
        "12345 "   -> 12345
        "12345.0"  -> 12345
    """
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto == "":
        return ""

    # Evita que Excel convierta identificadores numéricos a "12345.0".
    try:
        numero = float(texto)
        if numero.is_integer():
            return str(int(numero))
    except (ValueError, TypeError):
        pass

    return texto


def construir_clave_factura(valor_clave, valor_factura):
    """
    Construye la clave única utilizada para comparar una factura.

    Se usa NIT + número de factura para evitar que facturas diferentes
    del mismo tercero sean agrupadas.
    """
    clave = limpiar_clave(valor_clave)
    factura = normalizar_identificador_factura(valor_factura)

    if clave == "" and factura == "":
        return ""

    return f"{clave}|||{factura}"


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

def preparar_df_para_auditoria(
    df: pd.DataFrame,
    origen: str,
    col_clave: str | None = None,
    col_monto: str | None = None,
    col_factura: str | None = None,
    columnas_info: list[str] | None = None,
) -> pd.DataFrame:
    """
    Estandariza un dataframe para conciliación factura por factura.

    Crea:
    - __clave__: tercero/NIT
    - __factura__: identificador de factura
    - __clave_factura__: NIT + factura
    - __monto__: monto numérico
    """
    df = normalizar_columnas(df)

    origen_norm = normalizar_texto(origen)

    # Si no se especifican las columnas, se detectan automáticamente.
    if col_clave is None:
        if origen_norm == "novasoft":
            col_clave = buscar_columna_prioritaria(df, CLAVES_NOVASOFT)
        else:
            col_clave = buscar_columna_prioritaria(df, CLAVES_DIAN)
    else:
        col_clave = encontrar_columna_por_nombre(df, col_clave)

    if col_monto is None:
        if origen_norm == "novasoft":
            col_monto = buscar_columna_prioritaria(df, MONTOS_NOVASOFT)
        else:
            col_monto = buscar_columna_prioritaria(df, MONTOS_DIAN)
    else:
        col_monto = encontrar_columna_por_nombre(df, col_monto)

    if col_factura is None:
        if origen_norm == "novasoft":
            col_factura = buscar_columna_prioritaria(df, FACTURA_NOVASOFT)
        else:
            col_factura = buscar_columna_prioritaria(df, FACTURA_DIAN)
    else:
        col_factura = encontrar_columna_por_nombre(df, col_factura)

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

    if not col_factura:
        raise ValueError(
            f"No se encontró una columna identificadora de factura válida "
            f"en el archivo {origen}. "
            f"Columnas detectadas: {', '.join(df.columns.astype(str))}"
        )

    df = df.copy()

    # Conservar las columnas seleccionadas en nombres internos estándar.
    df["__clave__"] = df[col_clave].apply(limpiar_clave)
    df["__factura__"] = df[col_factura].apply(normalizar_identificador_factura)
    df["__monto__"] = convertir_monto_a_numero(df[col_monto])

    # La comparación se hará por NIT + factura.
    df["__clave_factura__"] = df.apply(
        lambda fila: construir_clave_factura(
            fila["__clave__"],
            fila["__factura__"],
        ),
        axis=1,
    )

    # Eliminar filas sin una clave suficiente.
    df = df[
        (df["__clave__"].astype(str).str.strip() != "") &
        (df["__factura__"].astype(str).str.strip() != "")
    ].copy()

    # Columnas adicionales: solo informativas, no forman parte de la comparación.
    for i, nombre_columna in enumerate(columnas_info or []):
        columna_real = encontrar_columna_por_nombre(df, nombre_columna)
        if columna_real:
            df[f"__info_{normalizar_texto(origen)}_{i}"] = df[columna_real]

    return df


# ============================================================
# CONSOLIDACIÓN POR FACTURA
# ============================================================

def _primer_valor_util(serie: pd.Series):
    """Devuelve el primer valor no vacío de una serie."""
    for valor in serie:
        if pd.notna(valor) and str(valor).strip() != "":
            return valor
    return ""


def consolidar_por_factura(
    df: pd.DataFrame,
    nombre_origen: str,
    columnas_info: list[str] | None = None,
) -> pd.DataFrame:
    """
    Consolida por NIT + factura.
    El monto se suma y las columnas informativas conservan el primer valor no vacío.
    """
    columna_valor = f"valor_{nombre_origen.lower()}"

    if df.empty:
        return pd.DataFrame(columns=[
            "__clave_factura__", "__clave__", "__factura__", columna_valor
        ])

    origen_norm = normalizar_texto(nombre_origen)
    agregaciones = {"__monto__": "sum"}

    for i, _ in enumerate(columnas_info or []):
        col_info = f"__info_{origen_norm}_{i}"
        if col_info in df.columns:
            agregaciones[col_info] = _primer_valor_util

    consolidado = df.groupby(
        ["__clave_factura__", "__clave__", "__factura__"],
        as_index=False,
    ).agg(agregaciones)

    return consolidado.rename(columns={"__monto__": columna_valor})


# Mantener compatibilidad si otra parte del proyecto todavía llama
# a consolidar_por_clave().
def consolidar_por_clave(
    df: pd.DataFrame,
    nombre_origen: str,
    columnas_info: list[str] | None = None,
) -> pd.DataFrame:
    """
    Compatibilidad con versiones anteriores.

    IMPORTANTE:
    La conciliación principal ya NO utiliza esta función.
    """
    return consolidar_por_factura(df, nombre_origen, columnas_info=columnas_info)


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
# FORMATO
# ============================================================

def aplicar_formato_monedas(
    df: pd.DataFrame,
    columnas: list[str],
) -> pd.DataFrame:
    """
    Convierte columnas numéricas a texto con formato de moneda
    para facilitar la lectura.
    """
    resultado = df.copy()

    for columna in columnas:
        if columna in resultado.columns:
            resultado[columna] = pd.to_numeric(
                resultado[columna],
                errors="coerce",
            ).fillna(0)

            resultado[columna] = resultado[columna].apply(
                lambda valor: (
                    f"-${abs(valor):,.2f}"
                    if pd.notna(valor) and valor < 0
                    else f"${valor:,.2f}"
                )
                if pd.notna(valor)
                else "$0.00"
            )

    return resultado


# ============================================================
# SERVICIO PRINCIPAL DE CONCILIACIÓN
# ============================================================

def ejecutar_auditoria_service(
    archivo_dian,
    archivo_novasoft,
    col_clave_dian=None,
    col_monto_dian=None,
    col_factura_dian=None,
    col_clave_novasoft=None,
    col_monto_novasoft=None,
    col_factura_novasoft=None,
    columnas_info_dian=None,
    columnas_info_novasoft=None,
):
    """
    Realiza conciliación de compras FACTURA POR FACTURA.

    Parámetros:
    - col_clave_dian: columna de NIT/tercero en DIAN.
    - col_monto_dian: columna de valor en DIAN.
    - col_factura_dian: columna que identifica la factura en DIAN.
    - col_clave_novasoft: columna de NIT/tercero en Novasoft.
    - col_monto_novasoft: columna de valor en Novasoft.
    - col_factura_novasoft: columna que identifica la factura en Novasoft.

    La clave real de comparación es:
        NIT + número de factura

    Retorna:
    - resumen general
    - detalle por factura
    - dif_montos
    - solo_dian
    - solo_novasoft
    - conciliados_df
    """
    try:
        if archivo_dian is None or archivo_novasoft is None:
            raise ValueError(
                "Debes cargar ambos archivos: DIAN y Novasoft."
            )

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
            raise ValueError(
                "El archivo DIAN no contiene información válida."
            )

        if df_novasoft_raw is None or df_novasoft_raw.empty:
            raise ValueError(
                "El archivo Novasoft no contiene información válida."
            )

        # ====================================================
        # 2) Preparar dataframes
        # ====================================================
        df_dian = preparar_df_para_auditoria(
            df_dian_raw,
            "DIAN",
            col_clave=col_clave_dian,
            col_monto=col_monto_dian,
            col_factura=col_factura_dian,
            columnas_info=columnas_info_dian,
        )

        df_novasoft = preparar_df_para_auditoria(
            df_novasoft_raw,
            "Novasoft",
            col_clave=col_clave_novasoft,
            col_monto=col_monto_novasoft,
            col_factura=col_factura_novasoft,
            columnas_info=columnas_info_novasoft,
        )

        # ====================================================
        # 3) Consolidar POR FACTURA
        # ====================================================
        dian_cons = consolidar_por_factura(df_dian, "dian", columnas_info=columnas_info_dian)
        novasoft_cons = consolidar_por_factura(df_novasoft, "novasoft", columnas_info=columnas_info_novasoft)

        # ====================================================
        # 4) Cruce POR FACTURA
        # ====================================================
        comparativo = pd.merge(
            dian_cons,
            novasoft_cons,
            on="__clave_factura__",
            how="outer",
            suffixes=("_dian", "_novasoft"),
        )

        # Recuperar NIT y factura de cualquiera de los dos archivos.
        comparativo["__clave__"] = (
            comparativo["__clave___dian"]
            if "__clave___dian" in comparativo.columns
            else pd.Series(index=comparativo.index, dtype=object)
        )

        if "__clave___novasoft" in comparativo.columns:
            comparativo["__clave__"] = (
                comparativo["__clave__"]
                .replace("", pd.NA)
                .fillna(comparativo["__clave___novasoft"])
            )

        comparativo["__factura__"] = (
            comparativo["__factura___dian"]
            if "__factura___dian" in comparativo.columns
            else pd.Series(index=comparativo.index, dtype=object)
        )

        if "__factura___novasoft" in comparativo.columns:
            comparativo["__factura__"] = (
                comparativo["__factura__"]
                .replace("", pd.NA)
                .fillna(comparativo["__factura___novasoft"])
            )

        # Agregar columnas informativas seleccionadas por el usuario.
        # Estas columnas NO participan en la clave de comparación.
        columnas_info_salida = []

        for i, nombre_columna in enumerate(columnas_info_dian or []):
            internal = f"__info_dian_{i}"
            if internal in comparativo.columns:
                salida = f"DIAN - {nombre_columna}"
                comparativo[salida] = comparativo[internal]
                columnas_info_salida.append(salida)

        for i, nombre_columna in enumerate(columnas_info_novasoft or []):
            internal = f"__info_novasoft_{i}"
            if internal in comparativo.columns:
                salida = f"Novasoft - {nombre_columna}"
                comparativo[salida] = comparativo[internal]
                columnas_info_salida.append(salida)

        # Normalizar montos.
        comparativo["valor_dian"] = pd.to_numeric(
            comparativo.get("valor_dian", 0),
            errors="coerce",
        ).fillna(0)

        comparativo["valor_novasoft"] = pd.to_numeric(
            comparativo.get("valor_novasoft", 0),
            errors="coerce",
        ).fillna(0)

        # ====================================================
        # 5) Diferencia y estado
        # ====================================================
        comparativo["diferencia"] = (
            comparativo["valor_dian"] -
            comparativo["valor_novasoft"]
        ).round(2)

        comparativo["observacion"] = comparativo.apply(
            construir_observacion,
            axis=1,
        )

        comparativo["estado"] = comparativo["observacion"].apply(
            lambda obs: (
                "Conciliado"
                if obs == "Conciliado"
                else "Diferencia"
            )
        )

        # Ordenar por mayor diferencia absoluta.
        comparativo = comparativo.sort_values(
            by="diferencia",
            key=lambda s: s.abs(),
            ascending=False,
        ).reset_index(drop=True)

        # ====================================================
        # 6) Subconjuntos funcionales
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
        # 7) KPIs / resumen
        # ====================================================
        total_dian = round(comparativo["valor_dian"].sum(), 2)
        total_novasoft = round(comparativo["valor_novasoft"].sum(), 2)
        diferencia_total = round(total_dian - total_novasoft, 2)

        terceros_dian = int(df_dian["__clave__"].nunique())
        terceros_novasoft = int(df_novasoft["__clave__"].nunique())

        registros_dian = int(len(df_dian))
        registros_novasoft = int(len(df_novasoft))

        facturas_dian = int(dian_cons["__clave_factura__"].nunique())
        facturas_novasoft = int(
            novasoft_cons["__clave_factura__"].nunique()
        )

        facturas_comparadas = int(len(comparativo))

        conciliados = int(
            (comparativo["estado"] == "Conciliado").sum()
        )

        con_diferencia = int(
            (comparativo["estado"] == "Diferencia").sum()
        )

        # ====================================================
        # 8) DataFrame principal de salida
        # ====================================================
        detalle = comparativo.rename(
            columns={
                "__clave__": "Tercero / NIT",
                "__factura__": "Factura",
                "valor_dian": "Valor DIAN",
                "valor_novasoft": "Valor Novasoft",
                "diferencia": "Diferencia",
                "estado": "Estado",
                "observacion": "Observación",
            }
        ).copy()

        # Mantener solamente columnas útiles y en orden.
        columnas_detalle = (
            ["Factura", "Tercero / NIT"]
            + columnas_info_salida
            + ["Valor DIAN", "Valor Novasoft", "Diferencia", "Estado", "Observación"]
        )

        columnas_detalle = [
            columna
            for columna in columnas_detalle
            if columna in detalle.columns
        ]

        detalle = detalle[columnas_detalle]

        detalle["Estado"] = detalle["Estado"].replace(
            {
                "Conciliado": "🟢 Conciliado",
                "Diferencia": "🟠 Diferencia",
            }
        )

        detalle = aplicar_formato_monedas(
            detalle,
            [
                "Valor DIAN",
                "Valor Novasoft",
                "Diferencia",
            ],
        )

        # ====================================================
        # 9) Subtablas
        # ====================================================
        def formatear_subtabla(
            df_sub: pd.DataFrame,
        ) -> pd.DataFrame:
            if df_sub.empty:
                return pd.DataFrame(
                    columns=[
                        "Factura",
                        "Tercero / NIT",
                        "Valor DIAN",
                        "Valor Novasoft",
                        "Diferencia",
                        "Observación",
                    ]
                )

            out = df_sub.rename(
                columns={
                    "__clave__": "Tercero / NIT",
                    "__factura__": "Factura",
                    "valor_dian": "Valor DIAN",
                    "valor_novasoft": "Valor Novasoft",
                    "diferencia": "Diferencia",
                    "observacion": "Observación",
                }
            ).copy()

            columnas = (
                ["Factura", "Tercero / NIT"]
                + columnas_info_salida
                + ["Valor DIAN", "Valor Novasoft", "Diferencia", "Observación"]
            )

            columnas = [
                columna
                for columna in columnas
                if columna in out.columns
            ]

            out = aplicar_formato_monedas(
                out,
                [
                    "Valor DIAN",
                    "Valor Novasoft",
                    "Diferencia",
                ],
            )

            return out[columnas]

        solo_dian_out = formatear_subtabla(solo_dian)
        solo_novasoft_out = formatear_subtabla(solo_novasoft)
        dif_montos_out = formatear_subtabla(dif_montos)
        conciliados_out = formatear_subtabla(conciliados_df)

        # ====================================================
        # 10) Respuesta del service
        # ====================================================
        return {
            "ok": True,
            "mensaje": "Conciliación factura por factura procesada correctamente.",

            "resumen": {
                "total_dian": total_dian,
                "total_novasoft": total_novasoft,
                "diferencia_total": diferencia_total,

                "terceros_dian": terceros_dian,
                "terceros_novasoft": terceros_novasoft,

                "registros_dian": registros_dian,
                "registros_novasoft": registros_novasoft,

                "facturas_dian": facturas_dian,
                "facturas_novasoft": facturas_novasoft,
                "facturas_comparadas": facturas_comparadas,

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
            "mensaje": f"Error al procesar la conciliación: {e}",
        }
