from Core.xml_generators import procesar_dinamico_xml
import pandas as pd


FORMATOS_VALIDOS = ["1001", "1003", "1004", "1005", "1006", "1007"]
VERSIONES_FORMATOS = {
    "1001": 10,
    "1003": 7,
    "1004": 8,
    "1005": 9,
    "1006": 8,
    "1007": 9
}


def obtener_pestanas_validas_service(archivo_excel):
    """
    Retorna las pestañas disponibles del Excel y prioriza aquellas
    que parecen corresponder a formatos DIAN.
    """
    if archivo_excel is None:
        raise ValueError("Debes cargar un archivo Excel.")

    xls = pd.ExcelFile(archivo_excel)
    pestanas_disponibles = xls.sheet_names

    pestanas_formatos = [
        p for p in pestanas_disponibles
        if any(f in p for f in FORMATOS_VALIDOS)
    ]

    if not pestanas_formatos:
        pestanas_formatos = pestanas_disponibles

    return pestanas_formatos


def detectar_formato_desde_pestana_service(pestana_seleccionada):
    """
    Extrae el número de formato a partir del nombre de la pestaña.
    """
    formato_detectado = "".join(filter(str.isdigit, pestana_seleccionada))

    if not formato_detectado:
        raise ValueError(
            f"No fue posible detectar el formato DIAN desde la pestaña '{pestana_seleccionada}'."
        )

    return formato_detectado


def obtener_version_formato_service(formato_detectado):
    """
    Devuelve la versión oficial del XML para el formato.
    """
    return VERSIONES_FORMATOS.get(str(formato_detectado), 9)


def construir_nombre_xml_service(formato_detectado, version_xml, ano, envio):
    """
    Construye el nombre oficial del archivo XML de salida.
    """
    return f"Dmuisca_01{str(formato_detectado).zfill(4)}{str(version_xml).zfill(2)}{ano}{str(envio).zfill(8)}.xml"


def generar_xml_service(archivo_excel, pestana_seleccionada, ano, envio):
    """
    Orquesta el proceso completo de generación del XML.
    """
    if archivo_excel is None:
        raise ValueError("Debes cargar el archivo Excel para generar el XML.")

    if not pestana_seleccionada:
        raise ValueError("Debes seleccionar una pestaña para procesar.")

    formato_detectado = detectar_formato_desde_pestana_service(pestana_seleccionada)
    version_xml = obtener_version_formato_service(formato_detectado)

    xml_bytes, total_registros, total_cuantias = procesar_dinamico_xml(
        archivo_xml_insumo=archivo_excel,
        pestana_seleccionada=pestana_seleccionada,
        año_gravable=ano,
        version_xml=version_xml,
        num_envio=envio,
        formato_detectado=str(formato_detectado)
    )

    nombre_archivo = construir_nombre_xml_service(
        formato_detectado=formato_detectado,
        version_xml=version_xml,
        ano=ano,
        envio=envio
    )

    return {
        "xml_bytes": xml_bytes,
        "nombre_archivo": nombre_archivo,
        "formato_detectado": formato_detectado,
        "version_xml": version_xml,
        "total_registros": total_registros,
        "total_cuantias": total_cuantias
    }