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
    """
    Busca una columna dentro de una lista de columnas usando un conjunto
    de alias configurados para un formato DIAN.
    """
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
    columnas_esperadas = obtener_columnas_minimas_formato(formato, vigencia)

    if not columnas_esperadas:
        return {
            "valido": True,
            "faltantes": [],
            "presentes": []
        }

    columnas_df = [normalizar_texto_columna(c) for c in df.columns]
    presentes = []
    faltantes = []

    for col_esperada in columnas_esperadas:
        col_norm = normalizar_texto_columna(col_esperada)
        encontrada = any(col_norm in c or c in col_norm for c in columnas_df)

        if encontrada:
            presentes.append(col_esperada)
        else:
            faltantes.append(col_esperada)

    return {
        "valido": len(presentes) > 0,
        "presentes": presentes,
        "faltantes": faltantes
    }