from Service.normative_service import (
    obtener_columnas_minimas_formato,
    obtener_regla_formato
)


def normalizar_texto_columna(texto):
    return (
        str(texto)
        .strip()
        .upper()
        .replace("Ó", "O")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ú", "U")
    )


def buscar_columna_por_alias(columnas, aliases):
    for col in columnas:
        col_norm = normalizar_texto_columna(col)
        for alias in aliases:
            alias_norm = normalizar_texto_columna(alias)
            if alias_norm in col_norm or col_norm in alias_norm:
                return col
    return None


def validar_formato_configurado(formato, vigencia=2025):
    obtener_regla_formato(formato, vigencia)
    return True


def validar_columnas_minimas(df, formato, vigencia=2025):
    columnas_minimas = obtener_columnas_minimas_formato(formato, vigencia)
    columnas_df = list(df.columns)

    presentes = []
    faltantes = []

    for col in columnas_minimas:
        col_norm = normalizar_texto_columna(col)
        encontrada = any(
            col_norm in normalizar_texto_columna(c) or
            normalizar_texto_columna(c) in col_norm
            for c in columnas_df
        )

        if encontrada:
            presentes.append(col)
        else:
            faltantes.append(col)

    return {
        "valido": len(faltantes) == 0,
        "presentes": presentes,
        "faltantes": faltantes
    }


def contar_vacios_columna(df, columna):
    if not columna or columna not in df.columns:
        return 0

    serie = df[columna].fillna("").astype(str).str.strip()
    return int((serie == "").sum())


def detectar_filas_total(df):
    filas_total = []

    for idx, fila in df.iterrows():
        valores = (
            fila.fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
            .tolist()
        )

        if any(
            valor in ["TOTAL", "TOTALES", "SUMA TOTAL"]
            or valor.startswith("TOTAL ")
            for valor in valores
        ):
            filas_total.append(int(idx) + 1)

    return filas_total