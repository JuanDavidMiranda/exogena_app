import pandas as pd

from Core.validators import (
    buscar_columna_por_alias,
    validar_columnas_minimas,
    contar_vacios_columna,
    detectar_filas_total
)
from Service.normative_service import obtener_aliases_formato

def analizar_obligatoriedad(archivo_maestro):
    excel_m = pd.ExcelFile(archivo_maestro)
    pestanas = excel_m.sheet_names
    formatos_analizados = []
    formatos_clave = ["1001", "1003", "1004", "1005", "1006", "1007", "1008", "1009"]
    
    for p in pestanas:
        formato_detectado = None
        for f in formatos_clave:
            if f in p:
                formato_detectado = f
                break
        
        if formato_detectado:
            df_raw = pd.read_excel(excel_m, sheet_name=p, header=None)
            fila_header = 0
            for idx, row in df_raw.iterrows():
                row_str = row.astype(str).str.lower().str.strip().str.replace('ó', 'o').str.replace('á', 'a').tolist()
                if any(kw in row_str for kw in ["concepto", "tipo de documento", "numero de identificacion", "razon social"]):
                    fila_header = idx
                    break
            
            df_datos = pd.read_excel(excel_m, sheet_name=p, skiprows=fila_header)
            df_datos.columns = df_datos.columns.str.strip()
            
            col_identificacion = [
                c for c in df_datos.columns 
                if "identific" in c.lower() or "nid" in c.lower() or "documento" in c.lower()
            ]
            
            if col_identificacion:
                col_id = col_identificacion[0]
                df_filtrado = df_datos[df_datos[col_id].notna()]
                df_filtrado = df_filtrado[df_filtrado[col_id].astype(str).str.strip() != ""]
                df_filtrado = df_filtrado[~df_filtrado[col_id].astype(str).str.lower().str.contains("total|resumen|concepto|nota", na=False)]
                cant_registros = len(df_filtrado)
            else:
                cant_registros = len(df_datos.dropna(how='all'))
            
            estado = "🟢 SÍ SE DEBE PRESENTAR" if cant_registros > 0 else "🔴 NO SE DEBE PRESENTAR (Vacío)"
                
            formatos_analizados.append({
                "Nombre de la Pestaña": p,
                "Formato DIAN": f"Formato {formato_detectado}",
                "Terceros Detectados": cant_registros,
                "Dictamen": estado
            })
    return formatos_analizados

def diagnosticar_dataframe_exogena(df, formato, vigencia=2025):
    aliases_formato = obtener_aliases_formato(formato, vigencia)
    columnas = list(df.columns)

    # Detectar columnas principales por aliases normativos
    col_nit = buscar_columna_por_alias(columnas, aliases_formato.get("nit", []))
    col_tdoc = buscar_columna_por_alias(columnas, aliases_formato.get("tdoc", []))
    col_cpt = buscar_columna_por_alias(columnas, aliases_formato.get("concepto", []))
    col_dv = buscar_columna_por_alias(columnas, aliases_formato.get("dv", []))
    col_raz = buscar_columna_por_alias(columnas, aliases_formato.get("razon_social", []))
    col_apl1 = buscar_columna_por_alias(columnas, aliases_formato.get("primer_apellido", []))
    col_apl2 = buscar_columna_por_alias(columnas, aliases_formato.get("segundo_apellido", []))
    col_nom1 = buscar_columna_por_alias(columnas, aliases_formato.get("primer_nombre", []))
    col_nom2 = buscar_columna_por_alias(columnas, aliases_formato.get("otros_nombres", []))

    columnas_detectadas = {
        "nit": col_nit,
        "tdoc": col_tdoc,
        "concepto": col_cpt,
        "dv": col_dv,
        "razon_social": col_raz,
        "primer_apellido": col_apl1,
        "segundo_apellido": col_apl2,
        "primer_nombre": col_nom1,
        "otros_nombres": col_nom2
    }

    validacion_estructura = validar_columnas_minimas(df, formato, vigencia)

    errores = []
    advertencias = []

    # Validaciones de columnas críticas
    if col_nit:
        vacios_nit = contar_vacios_columna(df, col_nit)
        if vacios_nit > 0:
            errores.append(f"Se encontraron {vacios_nit} registros con NIT/identificación vacío.")
    else:
        errores.append("No se detectó columna de NIT/identificación.")

    if col_tdoc:
        vacios_tdoc = contar_vacios_columna(df, col_tdoc)
        if vacios_tdoc > 0:
            errores.append(f"Se encontraron {vacios_tdoc} registros con tipo de documento vacío.")
    else:
        advertencias.append("No se detectó columna de tipo de documento.")

    if col_cpt:
        vacios_cpt = contar_vacios_columna(df, col_cpt)
        if vacios_cpt > 0:
            advertencias.append(f"Se encontraron {vacios_cpt} registros con concepto vacío.")
    else:
        advertencias.append("No se detectó columna de concepto.")

    # Validación de estructura mínima del formato
    if not validacion_estructura["valido"]:
        faltantes = ", ".join(validacion_estructura["faltantes"])
        errores.append(
            f"Faltan columnas mínimas requeridas para el formato {formato}: {faltantes}"
        )

    # Detectar filas tipo TOTAL / resumen
    filas_total = detectar_filas_total(df)
    if filas_total:
        advertencias.append(
            f"Se detectaron posibles filas de total o resumen en las filas: "
            f"{', '.join(map(str, filas_total[:10]))}"
            + ("..." if len(filas_total) > 10 else "")
        )

    estado_general = "OK"
    if errores:
        estado_general = "CON ERRORES"
    elif advertencias:
        estado_general = "CON ADVERTENCIAS"

    return {
        "formato": formato,
        "vigencia": vigencia,
        "estado_general": estado_general,
        "columnas_detectadas": columnas_detectadas,
        "validacion_estructura": validacion_estructura,
        "errores": errores,
        "advertencias": advertencias,
        "resumen": {
            "total_registros": len(df),
            "columnas_encontradas": len(df.columns),
            "filas_total_detectadas": len(filas_total)
        }
    }