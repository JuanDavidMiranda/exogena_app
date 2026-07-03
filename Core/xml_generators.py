import sys
import os
# Asegurar compatibilidad de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from Utils.helpers import inicializar_encabezado, generar_xml_bytes
from Core.validators import buscar_columna_por_alias
from Core.formatos_config import obtener_aliases_formato, obtener_tag_xml_formato
from Core.validators import buscar_columna_por_alias
from Service.normative_service import (
    obtener_tag_xml_formato,
    obtener_defaults_ubicacion,
    obtener_aliases_formato
)

def entero_seguro(valor):
    """
    Convierte cualquier valor a entero.
    Si el valor está vacío, es NaN o no es numérico, devuelve 0.
    """
    numero = pd.to_numeric(valor, errors="coerce")

    if pd.isna(numero):
        return 0

    return round(float(numero))

def procesar_dinamico_xml(
    archivo_xml_insumo,
    pestana_seleccionada,
    año_gravable,
    version_xml,
    num_envio,
    formato_detectado
):

    # 1. Leer la pestaña completa sin procesar headers para detectar la estructura real
    df_crudo = pd.read_excel(
        archivo_xml_insumo,
        sheet_name=pestana_seleccionada,
        header=None
    )

    # Buscar dinámicamente la fila donde empiezan los datos
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

    # Re-leer definiendo la fila de títulos encontrada
    df_datos = pd.read_excel(archivo_xml_insumo, sheet_name=pestana_seleccionada, skiprows=fila_inicio_datos - 1)
    
    # Normalizar los encabezados a mayúsculas limpias sin tildes ni espacios raros
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
    
    columnas = list(df_datos.columns)
    fmt_str = str(formato_detectado).strip()

    # Traer configuración normativa del formato
    tag_registro = obtener_tag_xml_formato(fmt_str, 2025)
    defaults_ubicacion = obtener_defaults_ubicacion(2025)
    aliases_formato = obtener_aliases_formato(fmt_str, 2025)

    # 2. Identificación de columnas usando aliases normativos
    col_nit = buscar_columna_por_alias(columnas, aliases_formato.get("nit", []))
    if not col_nit and len(columnas) > 2:
        col_nit = columnas[2]  # fallback posicional

    col_tdoc = buscar_columna_por_alias(columnas, aliases_formato.get("tdoc", []))
    if not col_tdoc and len(columnas) > 1:
        col_tdoc = columnas[1]  # fallback posicional

    col_cpt = buscar_columna_por_alias(columnas, aliases_formato.get("concepto", []))
    if not col_cpt and len(columnas) > 0:
        col_cpt = columnas[0]  # fallback posicional

    fmt_str = str(formato_detectado).strip()

    aliases_formato = obtener_aliases_formato(fmt_str, 2025)

    col_nit = buscar_columna_por_alias(columnas, aliases_formato.get("nit", []))
    col_tdoc = buscar_columna_por_alias(columnas, aliases_formato.get("tdoc", []))
    col_cpt = buscar_columna_por_alias(columnas, aliases_formato.get("concepto", []))
    col_dv = buscar_columna_por_alias(columnas, aliases_formato.get("dv", []))
    col_raz = buscar_columna_por_alias(columnas, aliases_formato.get("razon_social", []))
    col_apl1 = buscar_columna_por_alias(columnas, aliases_formato.get("primer_apellido", []))
    col_apl2 = buscar_columna_por_alias(columnas, aliases_formato.get("segundo_apellido", []))
    col_nom1 = buscar_columna_por_alias(columnas, aliases_formato.get("primer_nombre", []))
    col_nom2 = buscar_columna_por_alias(columnas, aliases_formato.get("otros_nombres", []))

    tag_registro = obtener_tag_xml_formato(fmt_str, 2025)

    # 3. Configuración de Etiquetas XML oficiales de la DIAN por número de formato
    from Service.normative_service import (
        obtener_tag_xml_formato,
        obtener_defaults_ubicacion,
        obtener_aliases_formato
    )

    fmt_str = str(formato_detectado).strip()
    tag_registro = obtener_tag_xml_formato(fmt_str, 2025)
    defaults_ubicacion = obtener_defaults_ubicacion(2025)
    aliases_formato = obtener_aliases_formato(fmt_str, 2025)

    # Crear Nodo Principal <mas>
    mas = ET.Element('mas', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': f'../xsd/{fmt_str}.xsd'
    })
    
    # Inicializar el nodo <Cab> temporalmente
    inicializar_encabezado(mas, año_gravable, fmt_str, version_xml, num_envio, 0, 0)
    
    suma_totales_general = 0
    conteo_registros = 0

    # 4. Procesamiento de registros
    for _, fila in df_datos.iterrows():
        if col_nit not in fila or pd.isna(fila[col_nit]):
            continue
            
        nit_raw = str(fila[col_nit]).strip().split('.')[0].split('-')[0]
        
        # Filtrar si la fila es un subtotal, está vacía, o es un texto acumulador
        if not nit_raw or nit_raw.lower() in ['nan', 'none', '', 'null', 'total', 'totales'] or not nit_raw.isdigit():
            continue

        atributos_montos = {}
        valores_fila_suma = 0

        # --- EXTRACCIÓN FLEXIBLE DE VALORES POR CONTENIDO DE TEXTO ---
        if fmt_str == "1001":
            columnas_valores = [c for c in columnas if any(x in c for x in ['PAGO', 'PNDED', 'IDED', 'INDED', 'RETP', 'RETA'])]
            for col in columnas_valores:
                val = entero_seguro(fila[col])      if col      else 0
                # Tomar los primeros 5 caracteres del nombre de la columna para el atributo XML (ej. pago, retp)
                nombre_attr = col.lower().split(' ')[0][:5]
                atributos_montos[nombre_attr] = str(val)
                valores_fila_suma += val

        elif fmt_str == "1003":
            col_vcom = next((c for c in columnas if 'SUJETO' in c or 'VALOR ACUMULADO' in c), None)
            col_ret = next((c for c in columnas if 'PRACTICARON' in c or 'RETENCION' in c if c != col_vcom), None)
            
            valor = pd.to_numeric(fila[col_vcom], errors="coerce") if col_vcom else 0
            vcom_val = entero_seguro(fila[col_vcom])
            ret_val = entero_seguro(fila[col_ret]) if col_ret else 0
            
            atributos_montos = {"vcom": str(vcom_val), "ret": str(ret_val)}
            valores_fila_suma = vcom_val + ret_val

        elif fmt_str == "1005":
            col_imp = next((c for c in columnas if 'IMPUESTO' in c or 'DESCONTABLE' in c), None)
            col_tov = next((c for c in columnas if 'CORRECCIONES' in c or 'DEVOLUCIONES' in c), None)
            
            imp_val = entero_seguro(fila[col_imp]) if col_imp else 0
            tov_val = entero_seguro(fila[col_tov])  if col_tov  else 0
            
            atributos_montos = {"imp": str(imp_val), "tov": str(tov_val)}
            valores_fila_suma = imp_val + tov_val

        elif fmt_str == "1006":
            col_imp = next((c for c in columnas if 'GENERADO' in c), None)
            col_tov = next((c for c in columnas if 'RECUPERADO' in c or 'DEVOLUCIONES' in c), None)
            col_inc = next((c for c in columnas if 'CONSUMO' in c), None)
            
            imp_val = entero_seguro(fila[col_imp]) if col_imp else 0
            tov_val = entero_seguro(fila[col_tov]) if col_tov else 0
            inc_val = entero_seguro(fila[col_inc]) if col_inc else 0
            
            atributos_montos = {"imp": str(imp_val), "tov": str(tov_val), "inc": str(inc_val)}
            valores_fila_suma = imp_val + tov_val + inc_val

        elif fmt_str == "1007":
            # Si los nombres vienen recortados o como ING_REC / INGBRT
            col_ingbrt = next((c for c in columnas if 'BRUTOS' in c or 'INGREC' in c or 'ING_REC' in c or 'VALOR ACUMULADO DE LOS INGRESOS' in c), None)
            col_ingdev = next((c for c in columnas if 'DEVOLUCIONES' in c or 'ING_DEV' in c or 'DEV' in c if c != col_ingbrt), None)
            
            ingbrt_val =  entero_seguro(fila[col_ingbrt]) if col_ingbrt else 0
            ingdev_val = entero_seguro(fila[col_ingdev]) if col_ingdev else 0
            
            atributos_montos = {"ingbrt": str(ingbrt_val), "ingdev": str(ingdev_val)}
            valores_fila_suma = ingbrt_val + ingdev_val
            
        else:
            # Si es cualquier otro formato, acumula todas las columnas numéricas finales
            for col in columnas[5:]:
                if df_datos[col].dtype in [np.float64, np.int64]:
                    val = entero_seguro(fila[col])
                    if val > 0:
                        atributos_montos[col.lower()[:5]] = str(val)
                        valores_fila_suma += val

        # Si toda la fila de este tercero está en ceros, la DIAN no pide reportarla
        if valores_fila_suma == 0:
            continue

        conteo_registros += 1
        suma_totales_general += valores_fila_suma

        # 5. Inyección al Árbol XML
        reg = ET.SubElement(mas, tag_registro)
        
        # Atributos Obligatorios base
        cpt_val = str(fila[col_cpt]).split('.')[0].strip() if col_cpt and pd.notna(fila[col_cpt]) else "5001"
        tdoc_val = str(fila[col_tdoc]).split('.')[0].strip() if col_tdoc and pd.notna(fila[col_tdoc]) else "13"
        
        reg.set('cpt', cpt_val if cpt_val.isdigit() else "5001")
        reg.set('tdoc', tdoc_val if tdoc_val.isdigit() else "13")
        reg.set('nid', str(nit_raw))
        
        if col_dv and pd.notna(fila[col_dv]) and str(fila[col_dv]).strip() != "" and str(fila[col_dv]).strip().lower() != 'nan':
            reg.set('dv', str(fila[col_dv]).strip().split('.')[0])

        # Determinar Razón Social o Nombres Naturales
        razon_social = str(fila[col_raz]).strip() if col_raz and pd.notna(fila[col_raz]) else ""
        if razon_social and razon_social.lower() != 'nan':
            reg.set('raz', razon_social.replace("&", "&amp;").replace('"', '')[:450])
        else:
            reg.set('apl1', str(fila[col_apl1]).strip() if col_apl1 and pd.notna(fila[col_apl1]) and str(fila[col_apl1]).lower() != 'nan' else "")
            reg.set('apl2', str(fila[col_apl2]).strip() if col_apl2 and pd.notna(fila[col_apl2]) and str(fila[col_apl2]).lower() != 'nan' else "")
            reg.set('nom1', str(fila[col_nom1]).strip() if col_nom1 and pd.notna(fila[col_nom1]) and str(fila[col_nom1]).lower() != 'nan' else "")
            reg.set('nom2', str(fila[col_nom2]).strip() if col_nom2 and pd.notna(fila[col_nom2]) and str(fila[col_nom2]).lower() != 'nan' else "")

        # Atributos de ubicación estándar para evitar rechazos en el validador Muisca
        reg.set('dir', defaults_ubicacion.get("direccion", "ZONA URBANA"))
        reg.set('dpto', defaults_ubicacion.get("departamento", "73"))
        reg.set('mun', defaults_ubicacion.get("municipio", "001"))
        reg.set('pais', defaults_ubicacion.get("pais", "169"))

        # Inyectar dinámicamente los importes calculados
        for k, v in atributos_montos.items():
            reg.set(k, v)

    # 6. Estampar sumatorias definitivas en la cabecera <Cab>
    cab_node = mas.find('Cab')
    if cab_node is not None:
        cab_node.find('ValorTotal').text = str(int(suma_totales_general))
        cab_node.find('CantReg').text = str(int(conteo_registros))

    if conteo_registros == 0:
        raise ValueError(f"La hoja '{pestana_seleccionada}' fue procesada, pero todos los terceros sumaban $0 en sus columnas de montos principales.")

    return generar_xml_bytes(mas), conteo_registros, suma_totales_general