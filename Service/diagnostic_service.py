import pandas as pd

from Core.diagnostics import (
    analizar_obligatoriedad,
    diagnosticar_dataframe_exogena
)


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

def diagnosticar_formato_excel_service(
    archivo_excel,
    pestana_seleccionada,
    formato_detectado,
    vigencia=2025
):
    if archivo_excel is None:
        raise ValueError("Debes cargar un archivo Excel para ejecutar el diagnóstico del formato.")

    # Leer hoja cruda para detectar encabezado real
    df_crudo = pd.read_excel(
        archivo_excel,
        sheet_name=pestana_seleccionada,
        header=None
    )

    fila_inicio_datos = 18

    for idx in range(15, min(30, len(df_crudo))):
        valores_fila = (
            df_crudo.iloc[idx]
            .fillna("")
            .astype(str)
            .str.strip()
            .tolist()
        )

        if any(
            "DOCUMENTO" in f.upper() or
            "IDENTIFICA" in f.upper() or
            "RAZON SOCIAL" in f.upper()
            for f in valores_fila
        ):
            fila_inicio_datos = idx + 1
            break

    df_datos = pd.read_excel(
        archivo_excel,
        sheet_name=pestana_seleccionada,
        skiprows=fila_inicio_datos - 1
    )

    df_datos.columns = (
        df_datos.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace('Ó', 'O')
        .str.replace('Á', 'A')
        .str.replace('É', 'E')
        .str.replace('Í', 'I')
        .str.replace('Ú', 'U')
    )

    df_datos = df_datos.dropna(how="all").copy()

    return diagnosticar_dataframe_exogena(
        df=df_datos,
        formato=str(formato_detectado).strip(),
        vigencia=vigencia
    )