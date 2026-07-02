import pandas as pd
from Core.xml_generators import procesar_dinamico_xml
from Service.normative_service import (
    detectar_formato_desde_pestana,
    obtener_formatos_soportados,
    obtener_version_formato
)

DEFAULT_VIGENCIA = 2025


def obtener_pestanas_validas_service(archivo_excel, vigencia=DEFAULT_VIGENCIA):
    if archivo_excel is None:
        raise ValueError("Debes cargar un archivo Excel.")

    xls = pd.ExcelFile(archivo_excel)
    pestanas_disponibles = xls.sheet_names
    formatos_validos = obtener_formatos_soportados(vigencia)

    pestanas_formatos = [
        p for p in pestanas_disponibles
        if any(f in p for f in formatos_validos)
    ]

    if not pestanas_formatos:
        pestanas_formatos = pestanas_disponibles

    return pestanas_formatos


def construir_nombre_xml_service(formato_detectado, version_xml, ano, envio):
    return f"Dmuisca_01{str(formato_detectado).zfill(4)}{str(version_xml).zfill(2)}{ano}{str(envio).zfill(8)}.xml"


def generar_xml_service(archivo_excel, pestana_seleccionada, ano, envio, vigencia=DEFAULT_VIGENCIA):
    if archivo_excel is None:
        raise ValueError("Debes cargar el archivo Excel para generar el XML.")

    if not pestana_seleccionada:
        raise ValueError("Debes seleccionar una pestaña para procesar.")

    formato_detectado = detectar_formato_desde_pestana(pestana_seleccionada, vigencia)

    if not formato_detectado:
        raise ValueError(
            f"No fue posible detectar el formato DIAN desde la pestaña '{pestana_seleccionada}'."
        )

    version_xml = obtener_version_formato(formato_detectado, vigencia)

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