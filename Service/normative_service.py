from Config.exogena_rules import EXOGENA_RULES


DEFAULT_VIGENCIA = 2025


def obtener_reglas_vigencia(vigencia=DEFAULT_VIGENCIA):
    if vigencia not in EXOGENA_RULES:
        raise ValueError(f"No existe configuración normativa para la vigencia {vigencia}.")
    return EXOGENA_RULES[vigencia]


def obtener_formatos_soportados(vigencia=DEFAULT_VIGENCIA):
    reglas = obtener_reglas_vigencia(vigencia)
    return reglas["supported_formats"]


def obtener_defaults_ubicacion(vigencia=DEFAULT_VIGENCIA):
    reglas = obtener_reglas_vigencia(vigencia)
    return reglas.get("defaults", {})


def obtener_regla_formato(formato, vigencia=DEFAULT_VIGENCIA):
    reglas = obtener_reglas_vigencia(vigencia)
    formatos = reglas["formats"]

    formato = str(formato).strip()
    if formato not in formatos:
        raise ValueError(
            f"El formato {formato} no está configurado para la vigencia {vigencia}."
        )

    return formatos[formato]


def obtener_version_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla["version"]


def obtener_tag_xml_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla["xml_tag"]


def obtener_nombre_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla["nombre"]


def obtener_aliases_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla.get("aliases", {})


def obtener_columnas_minimas_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla.get("columnas_minimas", [])


def obtener_columnas_monto_formato(formato, vigencia=DEFAULT_VIGENCIA):
    regla = obtener_regla_formato(formato, vigencia)
    return regla.get("columnas_monto", [])


def detectar_formato_desde_pestana(pestana, vigencia=DEFAULT_VIGENCIA):
    formatos = obtener_formatos_soportados(vigencia)
    pestana = str(pestana)

    for formato in formatos:
        if formato in pestana:
            return formato

    return None