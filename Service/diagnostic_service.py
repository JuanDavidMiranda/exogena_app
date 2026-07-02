from Core.diagnostics import analizar_obligatoriedad


def ejecutar_diagnostico_service(archivo_maestro):
    """
    Orquesta el diagnóstico preliminar de formatos DIAN.
    Retorna un diccionario con el detalle y un pequeño resumen.
    """
    if archivo_maestro is None:
        raise ValueError("Debes cargar un archivo Excel para ejecutar el diagnóstico.")

    resultados = analizar_obligatoriedad(archivo_maestro)

    if not resultados:
        return {
            "resultados": [],
            "total_formatos": 0,
            "formatos_con_datos": 0,
            "formatos_vacios": 0
        }

    formatos_con_datos = sum(1 for r in resultados if "🟢" in r["Dictamen"])
    formatos_vacios = sum(1 for r in resultados if "🔴" in r["Dictamen"])

    return {
        "resultados": resultados,
        "total_formatos": len(resultados),
        "formatos_con_datos": formatos_con_datos,
        "formatos_vacios": formatos_vacios
    }