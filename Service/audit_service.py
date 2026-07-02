from Core.auditors import ejecutar_conciliacion_posicional


def ejecutar_auditoria_service(archivo_novasoft, archivo_dian):
    """
    Ejecuta la conciliación Novasoft vs DIAN y devuelve
    un resultado estructurado para la interfaz.
    """
    if archivo_novasoft is None:
        raise ValueError("Debes cargar el archivo de Novasoft.")
    if archivo_dian is None:
        raise ValueError("Debes cargar el archivo DIAN.")

    dif_montos, solo_dian, solo_novasoft = ejecutar_conciliacion_posicional(
        archivo_novasoft,
        archivo_dian
    )

    # Filtrar solo diferencias reales
    if not dif_montos.empty:
        dif_montos = dif_montos[
            (dif_montos["Diferencia_Base"] != 0) |
            (dif_montos["Diferencia_IVA"] != 0)
        ].copy()

    return {
        "dif_montos": dif_montos,
        "solo_dian": solo_dian,
        "solo_novasoft": solo_novasoft,
        "resumen": {
            "diferencias_montos": len(dif_montos),
            "solo_dian": len(solo_dian),
            "solo_novasoft": len(solo_novasoft)
        }
    }