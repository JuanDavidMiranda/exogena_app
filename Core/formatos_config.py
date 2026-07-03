def obtener_aliases_formato(formato: str, anio: int = 2025):
    """
    Retorna aliases esperados para identificar columnas del formato DIAN.
    La idea es tolerar diferencias de nombres entre plantillas.
    """
    formato = str(formato).strip()

    # Base común reutilizable
    base = {
        "nit": [
            "NUMERO DE IDENTIFICACION",
            "NIT",
            "IDENTIFICACION",
            "NID",
            "NUMERO DOCUMENTO",
            "DOCUMENTO"
        ],
        "tdoc": [
            "TIPO DE DOCUMENTO",
            "TIPO DOC",
            "TDOC",
            "TIPO IDENTIFICACION"
        ],
        "concepto": [
            "CONCEPTO",
            "CPT"
        ],
        "dv": [
            "DV",
            "D.V.",
            "DIGITO DE VERIFICACION"
        ],
        "razon_social": [
            "RAZON SOCIAL",
            "APELLIDOS Y NOMBRES O RAZON SOCIAL",
            "NOMBRE O RAZON SOCIAL",
            "RAZON"
        ],
        "primer_apellido": [
            "PRIMER APELLIDO",
            "APELLIDO 1",
            "1 APELLIDO"
        ],
        "segundo_apellido": [
            "SEGUNDO APELLIDO",
            "APELLIDO 2",
            "2 APELLIDO"
        ],
        "primer_nombre": [
            "PRIMER NOMBRE",
            "NOMBRE 1",
            "1 NOMBRE"
        ],
        "otros_nombres": [
            "OTROS NOMBRES",
            "SEGUNDO NOMBRE",
            "NOMBRE 2"
        ]
    }

    # Si luego quieres personalizar por formato, lo hacemos aquí
    configuracion_por_formato = {
        "1001": {},
        "1003": {},
        "1004": {},
        "1005": {},
        "1006": {},
        "1007": {},
        "1008": {},
        "1009": {}
    }

    config_especifica = configuracion_por_formato.get(formato, {})

    # Mezcla base + específica
    resultado = {}
    for clave, aliases_base in base.items():
        aliases_extra = config_especifica.get(clave, [])
        resultado[clave] = aliases_base + aliases_extra

    return resultado


def obtener_tag_xml_formato(formato: str, anio: int = 2025):
    """
    Retorna el nombre del tag XML que corresponde al registro del formato.
    """
    formato = str(formato).strip()

    tags = {
        "1001": "pagoAbonoCuenta",
        "1003": "retencionFuente",
        "1004": "descuentoTributario",
        "1005": "ivaDescontable",
        "1006": "ivaGenerado",
        "1007": "ingresoRecibido",
        "1008": "cuentasPorCobrar",
        "1009": "cuentasPorPagar"
    }

    return tags.get(formato, "registro")