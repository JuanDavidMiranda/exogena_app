import pandas as pd

def ejecutar_conciliacion_posicional(archivo_novasoft, archivo_dian):
    # 1. LEER NOVASOFT
    nombre_novasoft = archivo_novasoft.name.lower()
    if nombre_novasoft.endswith('.csv'):
        df_novasoft = pd.read_csv(archivo_novasoft, sep=None, engine='python', header=None)
    elif nombre_novasoft.endswith('.xls'):
        df_novasoft = pd.read_excel(archivo_novasoft, engine='xlrd', header=None)
    else:
        df_novasoft = pd.read_excel(archivo_novasoft, header=None)

    fila_inicio_nova = 0
    for i in range(min(20, len(df_novasoft))):
        val = str(df_novasoft.iloc[i, 11]).strip() if len(df_novasoft.columns) > 11 else ""
        if val.isdigit() and len(val) > 4:
            fila_inicio_nova = i
            break
        elif "provee" in val.lower():
            fila_inicio_nova = i + 1
            break
    
    df_novasoft = df_novasoft.iloc[fila_inicio_nova:].reset_index(drop=True)
    df_nova_clean = pd.DataFrame()
    df_nova_clean['NIT'] = df_novasoft.iloc[:, 11].astype(str).str.split('.').str[0].str.split('-').str[0].str.strip()
    df_nova_clean['Nombre'] = df_novasoft.iloc[:, 17].astype(str).str.strip()
    df_nova_clean['Base'] = pd.to_numeric(df_novasoft.iloc[:, 12], errors='coerce').fillna(0)
    df_nova_clean['IVA'] = pd.to_numeric(df_novasoft.iloc[:, 13], errors='coerce').fillna(0)
    df_nova_clean = df_nova_clean[df_nova_clean['NIT'].str.len() > 3]

    # 2. LEER DIAN
    nombre_dian = archivo_dian.name.lower()
    if nombre_dian.endswith('.csv'):
        df_dian = pd.read_csv(archivo_dian, sep=None, engine='python', header=None)
    else:
        df_dian = pd.read_excel(archivo_dian, header=None)

    fila_inicio_dian = 0
    for i in range(min(20, len(df_dian))):
        val = str(df_dian.iloc[i, 9]).strip() if len(df_dian.columns) > 9 else ""
        if val.isdigit() and len(val) > 4:
            fila_inicio_dian = i
            break
        elif "emisor" in val.lower() or "nit" in val.lower():
            fila_inicio_dian = i + 1
            break
            
    df_dian = df_dian.iloc[fila_inicio_dian:].reset_index(drop=True)
    df_dian_clean = pd.DataFrame()
    df_dian_clean['NIT'] = df_dian.iloc[:, 9].astype(str).str.split('.').str[0].str.split('-').str[0].str.strip()
    df_dian_clean['Nombre'] = df_dian.iloc[:, 10].astype(str).str.strip()
    df_dian_clean['Base'] = pd.to_numeric(df_dian.iloc[:, 13], errors='coerce').fillna(0)
    df_dian_clean['IVA'] = pd.to_numeric(df_dian.iloc[:, 14], errors='coerce').fillna(0)
    df_dian_clean = df_dian_clean[df_dian_clean['NIT'].str.len() > 3]

    # 3. ACUMULAR Y CONCILIAR
    nova_grouped = df_nova_clean.groupby('NIT').agg({'Nombre': 'first', 'Base': 'sum', 'IVA': 'sum'}).reset_index()
    dian_grouped = df_dian_clean.groupby('NIT').agg({'Nombre': 'first', 'Base': 'sum', 'IVA': 'sum'}).reset_index()

    cruce_internos = pd.merge(dian_grouped, nova_grouped, on='NIT', how='inner', suffixes=('_DIAN', '_Novasoft'))
    
    dif_montos = pd.DataFrame({
        'NIT': cruce_internos['NIT'],
        'Razon_Social': cruce_internos['Nombre_DIAN'],
        'Base_DIAN': cruce_internos['Base_DIAN'],
        'Base_Novasoft': cruce_internos['Base_Novasoft'],
        'Diferencia_Base': cruce_internos['Base_DIAN'] - cruce_internos['Base_Novasoft'],
        'IVA_DIAN': cruce_internos['IVA_DIAN'],
        'IVA_Novasoft': cruce_internos['IVA_Novasoft'],
        'Diferencia_IVA': cruce_internos['IVA_DIAN'] - cruce_internos['IVA_Novasoft']
    })

    solo_dian = dian_grouped[~dian_grouped['NIT'].isin(nova_grouped['NIT'])].copy()[['NIT', 'IVA', 'Nombre']]
    solo_dian.columns = ['index', 'IVA', 'Nombre Emisor']
    
    solo_novasoft = nova_grouped[~nova_grouped['NIT'].isin(dian_grouped['NIT'])].copy()[['NIT', 'Base', 'IVA', 'Nombre']]
    solo_novasoft.columns = ['index', 'ven_net', 'mon_iva', 'NOMBRE PROVEEDOR']

    return dif_montos, solo_dian, solo_novasoft