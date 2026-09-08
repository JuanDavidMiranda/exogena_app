import pandas as pd

from Utils.excel_reader import leer_excel_seguro


# ============================================================
# CONFIGURACION
# ============================================================
TOLERANCIA_MONTO_DEFAULT = 1.0
TOLERANCIA_DIAS_DEFAULT = 3

ALIASES = {
    "dian_nit": ["NIT Emisor", "NIT emisor", "nit emisor", "NIT"],
    "dian_fecha": ["Fecha Emisión", "Fecha emision", "Fecha emisión", "fecha emisión"],
    "dian_total": ["Total", "total", "Valor Total", "Valor total"],
    "dian_folio": ["Folio", "folio", "Número", "Numero"],
    "dian_prefijo": ["Prefijo", "prefijo"],
    "dian_nombre": ["Nombre Emisor", "Nombre emisor", "Razon Social", "Razón Social"],
    "dian_tipo": ["Tipo de documento", "Tipo Documento", "Tipo de documento"],
    "nova_nit": ["provee", "proveedor", "nit proveedor", "nit tercero", "nit"],
    "nova_numero": ["numero", "número", "numero documento", "documento"],
    "nova_fecha": ["fecha", "Fecha"],
    "nova_ven_net": ["ven_net", "ven net", "valor neto"],
    "nova_iva": ["mon_iva", "mon iva", "iva"],
    "nova_credito": ["mon_cre", "mon cre", "credito", "crédito"],
}


def normalizar_texto(valor):
    return str(valor).strip().lower()


def normalizar_columnas(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def encontrar_columna(df, candidatos):
    columnas = list(df.columns)
    mapa = {normalizar_texto(c): c for c in columnas}

    for candidato in candidatos:
        if normalizar_texto(candidato) in mapa:
            return mapa[normalizar_texto(candidato)]

    for candidato in candidatos:
        candidato_norm = normalizar_texto(candidato)
        for columna in columnas:
            if candidato_norm in normalizar_texto(columna):
                return columna
    return None


def leer_archivo_tabular(archivo):
    if hasattr(archivo, "seek"):
        try:
            archivo.seek(0)
        except Exception:
            pass

    nombre = str(getattr(archivo, "name", "")).lower()
    if nombre.endswith(".csv"):
        try:
            return pd.read_csv(archivo)
        except UnicodeDecodeError:
            if hasattr(archivo, "seek"):
                try:
                    archivo.seek(0)
                except Exception:
                    pass
            return pd.read_csv(archivo, encoding="latin-1")

    return normalizar_columnas(leer_excel_seguro(archivo))


def convertir_monto(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0.0)

    texto = serie.astype(str).str.strip()
    # Soporta formatos como $1,234.56 y tambien 1.234.567,89.
    texto = texto.str.replace("$", "", regex=False).str.replace(" ", "", regex=False)

    # Si contiene coma y punto, se asume que el ultimo separador es decimal.
    def convertir(valor):
        if valor in ("", "nan", "None"):
            return 0.0
        try:
            if "," in valor and "." in valor:
                if valor.rfind(",") > valor.rfind("."):
                    valor = valor.replace(".", "").replace(",", ".")
                else:
                    valor = valor.replace(",", "")
            elif "," in valor:
                # En estos reportes la coma normalmente es separador de miles.
                valor = valor.replace(",", "")
            return float(valor)
        except (ValueError, TypeError):
            return 0.0

    return texto.map(convertir)


def normalizar_nit(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    # El NIT se compara sin separadores ni digito de verificacion separado.
    texto = texto.replace(" ", "").replace("-", "")
    return texto


def normalizar_identificador(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto


def normalizar_fecha(serie):
    return pd.to_datetime(serie, errors="coerce", dayfirst=True).dt.normalize()


def construir_factura_dian(prefijo, folio):
    prefijo = normalizar_identificador(prefijo)
    folio = normalizar_identificador(folio)
    if prefijo and folio:
        return f"{prefijo}-{folio}"
    return folio or prefijo


def _primer_valor(serie):
    for valor in serie:
        if pd.notna(valor) and str(valor).strip() != "":
            return valor
    return ""


def preparar_dian(df):
    df = normalizar_columnas(df)

    col_nit = encontrar_columna(df, ALIASES["dian_nit"])
    col_fecha = encontrar_columna(df, ALIASES["dian_fecha"])
    col_total = encontrar_columna(df, ALIASES["dian_total"])
    col_folio = encontrar_columna(df, ALIASES["dian_folio"])
    col_prefijo = encontrar_columna(df, ALIASES["dian_prefijo"])
    col_nombre = encontrar_columna(df, ALIASES["dian_nombre"])
    col_tipo = encontrar_columna(df, ALIASES["dian_tipo"])

    faltantes = []
    for nombre, columna in [("NIT Emisor", col_nit), ("Fecha Emisión", col_fecha), ("Total", col_total)]:
        if not columna:
            faltantes.append(nombre)
    if faltantes:
        raise ValueError(
            "No se pudieron detectar las columnas obligatorias de DIAN: "
            + ", ".join(faltantes)
            + f". Columnas detectadas: {', '.join(map(str, df.columns))}"
        )

    out = pd.DataFrame(index=df.index)
    out["nit"] = df[col_nit].map(normalizar_nit)
    out["fecha_dian"] = normalizar_fecha(df[col_fecha])
    out["total_dian"] = convertir_monto(df[col_total]).round(2)
    out["factura_dian"] = [
        construir_factura_dian(
            df[col_prefijo].iloc[i] if col_prefijo else "",
            df[col_folio].iloc[i] if col_folio else "",
        )
        for i in range(len(df))
    ]
    out["nombre_emisor"] = df[col_nombre] if col_nombre else ""
    out["tipo_documento"] = df[col_tipo] if col_tipo else ""

    # Para compras, las notas de credito no se cruzan como facturas.
    if col_tipo:
        tipo = out["tipo_documento"].astype(str).str.lower()
        es_factura = tipo.str.contains("factura", na=False) & ~tipo.str.contains("nota", na=False)
        if es_factura.any():
            out = out[es_factura].copy()

    out = out[(out["nit"] != "") & out["fecha_dian"].notna()].copy()
    out["_dian_id"] = range(len(out))
    return out.reset_index(drop=True)


def preparar_novasoft(df):
    df = normalizar_columnas(df)

    col_nit = encontrar_columna(df, ALIASES["nova_nit"])
    col_numero = encontrar_columna(df, ALIASES["nova_numero"])
    col_fecha = encontrar_columna(df, ALIASES["nova_fecha"])
    col_ven_net = encontrar_columna(df, ALIASES["nova_ven_net"])
    col_iva = encontrar_columna(df, ALIASES["nova_iva"])
    col_credito = encontrar_columna(df, ALIASES["nova_credito"])

    faltantes = []
    for nombre, columna in [("provee/NIT", col_nit), ("numero", col_numero), ("fecha", col_fecha), ("ven_net", col_ven_net)]:
        if not columna:
            faltantes.append(nombre)
    if faltantes:
        raise ValueError(
            "No se pudieron detectar las columnas obligatorias de Novasoft: "
            + ", ".join(faltantes)
            + f". Columnas detectadas: {', '.join(map(str, df.columns))}"
        )

    trabajo = pd.DataFrame()
    trabajo["nit"] = df[col_nit].map(normalizar_nit)
    trabajo["numero_novasoft"] = df[col_numero].map(normalizar_identificador)
    trabajo["fecha_novasoft"] = normalizar_fecha(df[col_fecha])
    trabajo["ven_net"] = convertir_monto(df[col_ven_net])
    trabajo["mon_iva"] = convertir_monto(df[col_iva]) if col_iva else 0.0
    trabajo["mon_cre"] = convertir_monto(df[col_credito]) if col_credito else 0.0

    # En el auxiliar analizado, el total que corresponde al valor de la factura
    # es ven_net + IVA - credito.
    trabajo["total_novasoft"] = (
        trabajo["ven_net"] + trabajo["mon_iva"] - trabajo["mon_cre"]
    ).round(2)

    trabajo = trabajo[
        (trabajo["nit"] != "")
        & (trabajo["numero_novasoft"] != "")
        & trabajo["fecha_novasoft"].notna()
    ].copy()

    # Cada factura Novasoft puede tener varias filas por item. Se consolida
    # primero por NIT + documento + fecha para evitar duplicar el valor.
    consolidado = (
        trabajo.groupby(
            ["nit", "numero_novasoft", "fecha_novasoft"],
            as_index=False,
        )[["ven_net", "mon_iva", "mon_cre", "total_novasoft"]]
        .sum()
    )
    consolidado["_nova_id"] = range(len(consolidado))
    return consolidado


def _candidatos_por_nit_monto(novasoft, nit, monto, tolerancia_monto):
    candidatos = novasoft[novasoft["nit"] == nit].copy()
    if candidatos.empty:
        return candidatos
    candidatos["dif_monto_abs"] = (candidatos["total_novasoft"] - monto).abs()
    return candidatos[candidatos["dif_monto_abs"] <= tolerancia_monto].copy()


def conciliar_facturas(dian, novasoft, tolerancia_monto=1.0, tolerancia_dias=3):
    """Cruce uno-a-uno usando NIT + fecha + total, con fallback por fecha."""
    usados = set()
    resultados = []

    for _, factura in dian.iterrows():
        nit = factura["nit"]
        fecha_dian = factura["fecha_dian"]
        total_dian = float(factura["total_dian"])

        candidatos = _candidatos_por_nit_monto(
            novasoft, nit, total_dian, tolerancia_monto
        )
        candidatos = candidatos[~candidatos["_nova_id"].isin(usados)].copy()

        exactos = candidatos[
            candidatos["fecha_novasoft"] == fecha_dian
        ].copy()

        estado = "🔴 No encontrada"
        observacion = "No se encontró un documento Novasoft con NIT, fecha y valor compatibles."
        elegido = None
        nivel = "No encontrada"

        if len(exactos) == 1:
            elegido = exactos.iloc[0]
            estado = "🟢 Exacta"
            nivel = "Exacta"
            observacion = "Coincidencia exacta por NIT + fecha + valor."
        elif len(exactos) > 1:
            estado = "🟠 Ambigua"
            nivel = "Ambigua"
            observacion = f"Se encontraron {len(exactos)} documentos Novasoft con el mismo NIT, fecha y valor."
        else:
            # Fallback: mismo NIT + mismo valor y fecha cercana.
            if not candidatos.empty:
                candidatos["dif_dias"] = (
                    candidatos["fecha_novasoft"] - fecha_dian
                ).abs().dt.days
                cercanos = candidatos[candidatos["dif_dias"] <= tolerancia_dias].copy()
                cercanos = cercanos.sort_values(["dif_dias", "dif_monto_abs"])

                if len(cercanos) == 1:
                    elegido = cercanos.iloc[0]
                    estado = "🟡 Probable"
                    nivel = "Probable"
                    observacion = (
                        "Coincidencia por NIT + valor; revisar fecha. "
                        f"La fecha difiere {int(elegido['dif_dias'])} día(s)."
                    )
                elif len(cercanos) > 1:
                    estado = "🟠 Ambigua"
                    nivel = "Ambigua"
                    observacion = (
                        f"Hay {len(cercanos)} candidatos por NIT + valor dentro de "
                        f"±{tolerancia_dias} días. Requiere revisión manual."
                    )

        fila = {
            "Factura DIAN": factura["factura_dian"],
            "Documento Novasoft": elegido["numero_novasoft"] if elegido is not None else "",
            "NIT": nit,
            "Nombre emisor": factura["nombre_emisor"],
            "Fecha DIAN": fecha_dian,
            "Fecha Novasoft": elegido["fecha_novasoft"] if elegido is not None else pd.NaT,
            "Total DIAN": total_dian,
            "Total Novasoft": float(elegido["total_novasoft"]) if elegido is not None else 0.0,
            "Diferencia": round(total_dian - (float(elegido["total_novasoft"]) if elegido is not None else 0.0), 2),
            "Resultado": estado,
            "Nivel coincidencia": nivel,
            "Observación": observacion,
            "_nova_id": elegido["_nova_id"] if elegido is not None else pd.NA,
        }
        resultados.append(fila)

        if elegido is not None:
            usados.add(int(elegido["_nova_id"]))

    detalle = pd.DataFrame(resultados)

    # Agregar documentos Novasoft que no fueron utilizados.
    no_usados = novasoft[~novasoft["_nova_id"].isin(usados)].copy()
    solo_novasoft = no_usados.rename(
        columns={
            "numero_novasoft": "Documento Novasoft",
            "nit": "NIT",
            "fecha_novasoft": "Fecha Novasoft",
            "total_novasoft": "Total Novasoft",
        }
    )[["Documento Novasoft", "NIT", "Fecha Novasoft", "Total Novasoft"]].copy()
    solo_novasoft["Observación"] = "Documento Novasoft sin factura DIAN asociada."

    return detalle, solo_novasoft


def _formatear_monedas(df, columnas):
    out = df.copy()
    for col in columnas:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).map(
                lambda x: f"-${abs(x):,.2f}" if x < 0 else f"${x:,.2f}"
            )
    return out


def _formatear_fechas(df, columnas):
    out = df.copy()
    for col in columnas:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%d/%m/%Y")
            out[col] = out[col].fillna("")
    return out


def ejecutar_auditoria_service(
    archivo_dian,
    archivo_novasoft,
    tolerancia_monto=TOLERANCIA_MONTO_DEFAULT,
    tolerancia_dias=TOLERANCIA_DIAS_DEFAULT,
    **kwargs,
):
    try:
        if archivo_dian is None or archivo_novasoft is None:
            raise ValueError("Debes cargar ambos archivos: DIAN y Novasoft.")

        df_dian_raw = leer_archivo_tabular(archivo_dian)
        df_nova_raw = leer_archivo_tabular(archivo_novasoft)

        dian = preparar_dian(df_dian_raw)
        novasoft = preparar_novasoft(df_nova_raw)

        detalle, solo_novasoft = conciliar_facturas(
            dian,
            novasoft,
            tolerancia_monto=float(tolerancia_monto),
            tolerancia_dias=int(tolerancia_dias),
        )

        if detalle.empty:
            detalle = pd.DataFrame(columns=[
                "Factura DIAN", "Documento Novasoft", "NIT", "Nombre emisor",
                "Fecha DIAN", "Fecha Novasoft", "Total DIAN", "Total Novasoft",
                "Diferencia", "Resultado", "Nivel coincidencia", "Observación"
            ])

        exactas = detalle[detalle["Nivel coincidencia"] == "Exacta"].copy()
        probables = detalle[detalle["Nivel coincidencia"] == "Probable"].copy()
        ambiguas = detalle[detalle["Nivel coincidencia"] == "Ambigua"].copy()
        no_encontradas = detalle[detalle["Nivel coincidencia"] == "No encontrada"].copy()
        con_diferencia = detalle[detalle["Diferencia"].abs() > tolerancia_monto].copy()

        # Para el total de Novasoft se usa todo el auxiliar consolidado.
        total_dian = round(float(dian["total_dian"].sum()), 2)
        total_novasoft = round(float(novasoft["total_novasoft"].sum()), 2)
        diferencia_total = round(total_dian - total_novasoft, 2)

        detalle_salida = detalle.drop(columns=["_nova_id"], errors="ignore").copy()
        detalle_salida = _formatear_fechas(detalle_salida, ["Fecha DIAN", "Fecha Novasoft"])
        detalle_salida = _formatear_monedas(
            detalle_salida, ["Total DIAN", "Total Novasoft", "Diferencia"]
        )

        solo_dian = no_encontradas.drop(columns=["_nova_id"], errors="ignore").copy()
        solo_dian = _formatear_fechas(solo_dian, ["Fecha DIAN", "Fecha Novasoft"])
        solo_dian = _formatear_monedas(solo_dian, ["Total DIAN", "Total Novasoft", "Diferencia"])

        solo_novasoft_salida = _formatear_fechas(solo_novasoft, ["Fecha Novasoft"])
        solo_novasoft_salida = _formatear_monedas(solo_novasoft_salida, ["Total Novasoft"])

        dif_montos = _formatear_fechas(con_diferencia.drop(columns=["_nova_id"], errors="ignore"), ["Fecha DIAN", "Fecha Novasoft"])
        dif_montos = _formatear_monedas(dif_montos, ["Total DIAN", "Total Novasoft", "Diferencia"])

        conciliados_df = detalle[
            (detalle["Nivel coincidencia"].isin(["Exacta", "Probable"]))
            & (detalle["Diferencia"].abs() <= tolerancia_monto)
        ].drop(columns=["_nova_id"], errors="ignore").copy()
        conciliados_df = _formatear_fechas(conciliados_df, ["Fecha DIAN", "Fecha Novasoft"])
        conciliados_df = _formatear_monedas(conciliados_df, ["Total DIAN", "Total Novasoft", "Diferencia"])

        resumen = {
            "total_dian": total_dian,
            "total_novasoft": total_novasoft,
            "diferencia_total": diferencia_total,
            "terceros_dian": int(dian["nit"].nunique()),
            "terceros_novasoft": int(novasoft["nit"].nunique()),
            "registros_dian": int(len(dian)),
            "registros_novasoft": int(len(df_nova_raw)),
            "facturas_dian": int(len(dian)),
            "facturas_novasoft": int(len(novasoft)),
            "facturas_comparadas": int(len(detalle)),
            "conciliados": int(len(exactas)),
            "probables": int(len(probables)),
            "ambiguas": int(len(ambiguas)),
            "no_encontradas": int(len(no_encontradas)),
            "con_diferencia": int(len(con_diferencia)),
            "solo_dian": int(len(no_encontradas)),
            "solo_novasoft": int(len(solo_novasoft)),
            "dif_montos": int(len(con_diferencia)),
        }

        return {
            "ok": True,
            "mensaje": "Conciliación factura por factura procesada correctamente.",
            "resumen": resumen,
            "detalle": detalle_salida,
            "detalle_raw": detalle,
            "solo_dian": solo_dian,
            "solo_novasoft": solo_novasoft_salida,
            "dif_montos": dif_montos,
            "conciliados_df": conciliados_df,
            "probables_df": _formatear_monedas(_formatear_fechas(probables.drop(columns=["_nova_id"], errors="ignore"), ["Fecha DIAN", "Fecha Novasoft"]), ["Total DIAN", "Total Novasoft", "Diferencia"]),
            "ambiguas_df": _formatear_fechas(ambiguas.drop(columns=["_nova_id"], errors="ignore"), ["Fecha DIAN", "Fecha Novasoft"]),
        }

    except Exception as e:
        return {
            "ok": False,
            "mensaje": f"Error al procesar la conciliación: {e}",
        }


def obtener_columnas_disponibles(archivo):
    df = leer_archivo_tabular(archivo)
    if df is None or df.empty:
        return []
    return [str(c).strip() for c in df.columns if str(c).strip()]


def analizar_archivos_para_auditoria(archivo_dian, archivo_novasoft):
    columnas_dian = obtener_columnas_disponibles(archivo_dian)
    columnas_novasoft = obtener_columnas_disponibles(archivo_novasoft)
    return {
        "columnas_dian": columnas_dian,
        "columnas_novasoft": columnas_novasoft,
        "sugerencia_dian": {
            "col_clave": encontrar_columna(pd.DataFrame(columns=columnas_dian), ALIASES["dian_nit"]),
            "col_monto": encontrar_columna(pd.DataFrame(columns=columnas_dian), ALIASES["dian_total"]),
        },
        "sugerencia_novasoft": {
            "col_clave": encontrar_columna(pd.DataFrame(columns=columnas_novasoft), ALIASES["nova_nit"]),
            "col_monto": encontrar_columna(pd.DataFrame(columns=columnas_novasoft), ALIASES["nova_ven_net"]),
        },
    }
