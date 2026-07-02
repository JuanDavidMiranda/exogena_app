EXOGENA_RULES = {
    2025: {
        "supported_formats": ["1001", "1003", "1004", "1005", "1006", "1007", "1008", "1009"],

        "defaults": {
            "direccion": "ZONA URBANA",
            "departamento": "73",
            "municipio": "001",
            "pais": "169"
        },

        "formats": {
            "1001": {
                "nombre": "Pagos o abonos en cuenta y retenciones practicadas",
                "version": 10,
                "xml_tag": "pagos",
                "columnas_minimas": [
                    "CONCEPTO",
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [
                    "PAGO",
                    "PNDED",
                    "IDED",
                    "INDED",
                    "RETP",
                    "RETA"
                ],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC", "TIPO DOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"],
                    "primer_apellido": ["PRIMER APELLIDO", "APELLIDO 1"],
                    "segundo_apellido": ["SEGUNDO APELLIDO", "APELLIDO 2"],
                    "primer_nombre": ["PRIMER NOMBRE", "NOMBRE 1"],
                    "otros_nombres": ["OTROS NOMBRES", "SEGUNDO NOMBRE", "NOMBRE 2"]
                }
            },

            "1003": {
                "nombre": "Retenciones en la fuente que le practicaron",
                "version": 7,
                "xml_tag": "retenc",
                "columnas_minimas": [
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [
                    "SUJETO",
                    "VALOR ACUMULADO",
                    "RETENCION",
                    "PRACTICARON"
                ],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"]
                }
            },

            "1004": {
                "nombre": "Descuentos tributarios solicitados",
                "version": 8,
                "xml_tag": "descto",
                "columnas_minimas": [
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"]
                }
            },

            "1005": {
                "nombre": "IVA descontable",
                "version": 9,
                "xml_tag": "ivades",
                "columnas_minimas": [
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [
                    "IMPUESTO",
                    "DESCONTABLE",
                    "CORRECCIONES",
                    "DEVOLUCIONES"
                ],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"]
                }
            },

            "1006": {
                "nombre": "IVA generado",
                "version": 8,
                "xml_tag": "ivagen",
                "columnas_minimas": [
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [
                    "GENERADO",
                    "RECUPERADO",
                    "DEVOLUCIONES",
                    "CONSUMO"
                ],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"]
                }
            },

            "1007": {
                "nombre": "Ingresos recibidos",
                "version": 9,
                "xml_tag": "ingresos",
                "columnas_minimas": [
                    "TIPO DE DOCUMENTO",
                    "NUMERO DE IDENTIFICACION"
                ],
                "columnas_monto": [
                    "BRUTOS",
                    "INGREC",
                    "ING_REC",
                    "DEVOLUCIONES",
                    "ING_DEV"
                ],
                "aliases": {
                    "nit": ["NUMERO DE IDENTIFICACION", "IDENTIFICACION", "NIT", "NID"],
                    "tdoc": ["TIPO DE DOCUMENTO", "TDOC"],
                    "concepto": ["CONCEPTO", "CPT"],
                    "dv": ["DV", "D.V."],
                    "razon_social": ["RAZON SOCIAL", "SOCIAL"]
                }
            },

            "1008": {
                "nombre": "Cuentas por cobrar",
                "version": 1,
                "xml_tag": "cxc",
                "columnas_minimas": [],
                "columnas_monto": [],
                "aliases": {}
            },

            "1009": {
                "nombre": "Cuentas por pagar",
                "version": 1,
                "xml_tag": "cxp",
                "columnas_minimas": [],
                "columnas_monto": [],
                "aliases": {}
            }
        }
    }
}