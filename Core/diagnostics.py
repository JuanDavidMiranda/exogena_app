import pandas as pd

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