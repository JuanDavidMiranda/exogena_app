import io
import pandas as pd
import streamlit as st

from Service.audit_service import (
    analizar_archivos_para_auditoria,
    ejecutar_auditoria_service,
)
from Ui.components import section_header, kpi_card, status_box, soft_divider
from Service.transacciones_service import registrar_transaccion


def render_auditoria_page():
    section_header(
        "🔄 Auditoría de datos: Novasoft vs formatos DIAN",
        "Cruza el archivo base de Novasoft con el borrador del formato DIAN para identificar diferencias en valores por tercero."
    )

    user_info = st.session_state.get("user_info", {}) or {}
    username = user_info.get("username", "")
    nombre_usuario = user_info.get("nombre", "")
    rol = user_info.get("rol", "usuario")

    st.markdown("### Archivos de entrada")
    col1, col2 = st.columns(2)

    with col1:
        archivo_novasoft = st.file_uploader(
            "Sube el reporte de Novasoft",
            type=["xlsx", "xls", "csv"],
            key="novasoft_file"
        )

    with col2:
        archivo_dian = st.file_uploader(
            "Sube el borrador del formato DIAN",
            type=["xlsx", "xls", "csv"],
            key="dian_file"
        )

    if not archivo_novasoft or not archivo_dian:
        st.info("Carga ambos archivos para ejecutar la auditoría y conciliación.")
        return

    st.markdown("")

    try:
        analisis = analizar_archivos_para_auditoria(archivo_dian, archivo_novasoft)
    except Exception as e:
        st.warning(f"No fue posible analizar automáticamente los archivos: {e}")
        analisis = {"columnas_dian": [], "columnas_novasoft": [], "sugerencia_dian": {}, "sugerencia_novasoft": {}}

    st.markdown("### 🧠 Configuración inteligente de columnas")
    st.info(
        "El sistema lee ambos archivos, detecta sus columnas y te permite elegir qué campo usar como identificador y qué campo usar para comparar montos."
    )

    col_dian_cfg, col_nova_cfg = st.columns(2)

    with col_dian_cfg:
        st.markdown("**Columnas detectadas - DIAN**")
        if analisis["columnas_dian"]:
            st.dataframe(
                pd.DataFrame({"Columnas": analisis["columnas_dian"]}),
                hide_index=True,
                width="stretch",
            )
        else:
            st.caption("No se detectaron columnas útiles en el archivo DIAN.")

        col_clave_dian = st.selectbox(
            "Columna para identificar tercero (DIAN)",
            options=analisis["columnas_dian"] or ["No disponible"],
            index=0 if analisis["columnas_dian"] else 0,
            key="col_clave_dian",
        )
        col_monto_dian = st.selectbox(
            "Columna para comparar montos (DIAN)",
            options=analisis["columnas_dian"] or ["No disponible"],
            index=0 if analisis["columnas_dian"] else 0,
            key="col_monto_dian",
        )

    with col_nova_cfg:
        st.markdown("**Columnas detectadas - Novasoft**")
        if analisis["columnas_novasoft"]:
            st.dataframe(
                pd.DataFrame({"Columnas": analisis["columnas_novasoft"]}),
                hide_index=True,
                width="stretch",
            )
        else:
            st.caption("No se detectaron columnas útiles en el archivo Novasoft.")

        col_clave_novasoft = st.selectbox(
            "Columna para identificar tercero (Novasoft)",
            options=analisis["columnas_novasoft"] or ["No disponible"],
            index=0 if analisis["columnas_novasoft"] else 0,
            key="col_clave_novasoft",
        )
        col_monto_novasoft = st.selectbox(
            "Columna para comparar montos (Novasoft)",
            options=analisis["columnas_novasoft"] or ["No disponible"],
            index=0 if analisis["columnas_novasoft"] else 0,
            key="col_monto_novasoft",
        )

    if not analisis["columnas_dian"] or not analisis["columnas_novasoft"]:
        st.warning("No fue posible leer columnas válidas en uno de los archivos. Revisa el formato o intenta con otro archivo.")
        return

    st.markdown("")

    if st.button("📊 Ejecutar conciliación", width="stretch"):
        try:
            # OJO: tu service recibe primero DIAN y luego Novasoft
            resultado = ejecutar_auditoria_service(
                archivo_dian,
                archivo_novasoft,
                col_clave_dian=col_clave_dian if col_clave_dian != "No disponible" else None,
                col_monto_dian=col_monto_dian if col_monto_dian != "No disponible" else None,
                col_clave_novasoft=col_clave_novasoft if col_clave_novasoft != "No disponible" else None,
                col_monto_novasoft=col_monto_novasoft if col_monto_novasoft != "No disponible" else None,
            )

            if not resultado.get("ok"):
                registrar_transaccion(
                    modulo="Auditoría",
                    accion="Ejecutar conciliación",
                    estado="ERROR",
                    detalle=resultado.get("mensaje", "Ocurrió un error en la conciliación."),
                    archivo_1=archivo_dian.name if archivo_dian else "",
                    archivo_2=archivo_novasoft.name if archivo_novasoft else "",
                    username=username,
                    nombre_usuario=nombre_usuario,
                    rol=rol
                )

                status_box(
                    resultado.get("mensaje", "Ocurrió un error en la conciliación."),
                    kind="error"
                )
                return

            status_box(
                resultado.get("mensaje", "Conciliación procesada correctamente."),
                kind="ok"
            )

            resumen = resultado["resumen"]
            detalle = resultado["detalle"]
            solo_dian = resultado["solo_dian"]
            solo_novasoft = resultado["solo_novasoft"]
            dif_montos = resultado["dif_montos"]
            conciliados_df = resultado["conciliados_df"]
            registrar_transaccion(
                modulo="Auditoría",
                accion="Ejecutar conciliación",
                estado="OK",
                detalle=(
                    f"DIAN: {archivo_dian.name}. "
                    f"Novasoft: {archivo_novasoft.name}. "
                    f"Conciliados: {resumen.get('conciliados', 0)}. "
                    f"Con diferencia: {resumen.get('con_diferencia', 0)}. "
                    f"Solo DIAN: {resumen.get('solo_dian', 0)}. "
                    f"Solo Novasoft: {resumen.get('solo_novasoft', 0)}. "
                    f"Diferencia total: {resumen.get('diferencia_total', 0)}."
                ),
                archivo_1=archivo_dian.name if archivo_dian else "",
                archivo_2=archivo_novasoft.name if archivo_novasoft else "",
                username=username,
                nombre_usuario=nombre_usuario,
                rol=rol
            )

            soft_divider()

            # ==========================
            # KPIs principales
            # ==========================
            st.markdown("### Resultado de la conciliación")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                kpi_card(
                    "Total DIAN",
                    f"${resumen['total_dian']:,.0f}",
                    "Suma consolidada del archivo DIAN"
                )

            with c2:
                kpi_card(
                    "Total Novasoft",
                    f"${resumen['total_novasoft']:,.0f}",
                    "Suma consolidada del archivo Novasoft"
                )

            with c3:
                kpi_card(
                    "Terceros conciliados",
                    resumen["conciliados"],
                    "Terceros sin diferencia"
                )

            with c4:
                kpi_card(
                    "Con diferencia",
                    resumen["con_diferencia"],
                    "Terceros con valores distintos"
                )

            st.markdown("")

            c5, c6, c7, c8 = st.columns(4)

            with c5:
                kpi_card(
                    "Diferencia total",
                    f"${resumen['diferencia_total']:,.0f}",
                    "DIAN - Novasoft"
                )

            with c6:
                kpi_card(
                    "Terceros DIAN",
                    resumen["terceros_dian"],
                    "Terceros detectados en DIAN"
                )

            with c7:
                kpi_card(
                    "Terceros Novasoft",
                    resumen["terceros_novasoft"],
                    "Terceros detectados en Novasoft"
                )

            with c8:
                kpi_card(
                    "Registros procesados",
                    resumen["registros_dian"] + resumen["registros_novasoft"],
                    "Suma de filas leídas en ambos archivos"
                )

            soft_divider()

            # ==========================
            # Resumen ejecutivo
            # ==========================
            st.markdown("### 🧾 Resumen ejecutivo")

            diferencia_total = resumen["diferencia_total"]
            conciliados = resumen["conciliados"]
            con_diferencia = resumen["con_diferencia"]

            if abs(diferencia_total) < 0.01 and con_diferencia == 0:
                status_box(
                    "La conciliación no presenta diferencias entre los valores consolidados de DIAN y Novasoft.",
                    kind="ok"
                )
            else:
                status_box(
                    f"Se detectaron diferencias en la conciliación. "
                    f"Total conciliado: <strong>{conciliados}</strong> tercero(s). "
                    f"Con diferencia: <strong>{con_diferencia}</strong> tercero(s). "
                    f"Diferencia total: <strong>${diferencia_total:,.0f}</strong>.",
                    kind="warning"
                )

            # ==========================
            # Tabla principal
            # ==========================
            st.markdown("### 📋 Detalle consolidado por tercero")

            st.dataframe(
                detalle,
                width="stretch",
                hide_index=True
            )

            soft_divider()

            # ==========================
            # Subresultados de conciliación
            # ==========================
            st.markdown("### 🔎 Detalle de hallazgos")

            if not dif_montos.empty:
                st.markdown("#### 💰 Diferencias de monto")
                st.dataframe(
                    dif_montos,
                    width="stretch",
                    hide_index=True
                )

            if not solo_dian.empty:
                st.markdown("#### 📄 Registros presentes solo en DIAN")
                st.dataframe(
                    solo_dian,
                    width="stretch",
                    hide_index=True
                )

            if not solo_novasoft.empty:
                st.markdown("#### 🧾 Registros presentes solo en Novasoft")
                st.dataframe(
                solo_novasoft,
                width="stretch",
                hide_index=True
                )

            if not conciliados_df.empty:
                with st.expander("🟢 Ver registros conciliados", expanded=False):
                    st.dataframe(
                    conciliados_df,
                    width="stretch",
                    hide_index=True
                )

            soft_divider()

            # ==========================
            # Descargar resultado
            # ==========================
            st.markdown("### 📥 Exportar resultado de conciliación")

            buffer = io.BytesIO()

            # Blindar dataframes por si alguno viene None
            detalle_export = detalle if isinstance(detalle, pd.DataFrame) else pd.DataFrame()
            solo_dian_export = solo_dian if isinstance(solo_dian, pd.DataFrame) else pd.DataFrame()
            solo_novasoft_export = solo_novasoft if isinstance(solo_novasoft, pd.DataFrame) else pd.DataFrame()
            dif_montos_export = dif_montos if isinstance(dif_montos, pd.DataFrame) else pd.DataFrame()
            conciliados_export = conciliados_df if isinstance(conciliados_df, pd.DataFrame) else pd.DataFrame()

            # Si detalle viene vacío, al menos crear una hoja mínima para evitar el error
            if detalle_export.empty:
                detalle_export = pd.DataFrame([{"Mensaje": "No se encontraron resultados para exportar"}])

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                # Hoja 1: resumen
                resumen_df = pd.DataFrame([
                    {
                        "Total DIAN": resumen.get("total_dian", 0),
                        "Total Novasoft": resumen.get("total_novasoft", 0),
                        "Diferencia total": resumen.get("diferencia_total", 0),
                        "Terceros DIAN": resumen.get("terceros_dian", 0),
                        "Terceros Novasoft": resumen.get("terceros_novasoft", 0),
                        "Registros DIAN": resumen.get("registros_dian", 0),
                        "Registros Novasoft": resumen.get("registros_novasoft", 0),
                        "Conciliados": resumen.get("conciliados", 0),
                        "Con diferencia": resumen.get("con_diferencia", 0),
                        "Solo en DIAN": resumen.get("solo_dian", 0),
                        "Solo en Novasoft": resumen.get("solo_novasoft", 0),
                        "Diferencias de monto": resumen.get("dif_montos", 0),
                    }
                ])
                resumen_df.to_excel(writer, sheet_name="Resumen", index=False)

                # Hoja 2: detalle general
                detalle_export.to_excel(writer, sheet_name="Detalle", index=False)

                # Hoja 3: solo DIAN
                if solo_dian_export.empty:
                    solo_dian_export = pd.DataFrame([{"Mensaje": "Sin registros solo en DIAN"}])
                solo_dian_export.to_excel(writer, sheet_name="Solo DIAN", index=False)

                # Hoja 4: solo Novasoft
                if solo_novasoft_export.empty:
                    solo_novasoft_export = pd.DataFrame([{"Mensaje": "Sin registros solo en Novasoft"}])
                solo_novasoft_export.to_excel(writer, sheet_name="Solo Novasoft", index=False)

                # Hoja 5: diferencias de monto
                if dif_montos_export.empty:
                    dif_montos_export = pd.DataFrame([{"Mensaje": "Sin diferencias de monto"}])
                dif_montos_export.to_excel(writer, sheet_name="Dif Montos", index=False)

                # Hoja 6: conciliados
                if conciliados_export.empty:
                    conciliados_export = pd.DataFrame([{"Mensaje": "Sin registros conciliados"}])
                conciliados_export.to_excel(writer, sheet_name="Conciliados", index=False)

            buffer.seek(0)

            descarga = st.download_button(
                label="📥 Descargar conciliación final (.xlsx)",
                data=buffer,
                file_name="conciliacion_final_exogena.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

            if descarga:
                registrar_transaccion(
                    modulo="Auditoría",
                    accion="Descargar conciliación",
                    estado="OK",
                    detalle="Descarga del archivo consolidado de conciliación.",
                    archivo_1=archivo_dian.name if archivo_dian else "",
                    archivo_2=archivo_novasoft.name if archivo_novasoft else "",
                    username=username,
                    nombre_usuario=nombre_usuario,
                    rol=rol
                )
        except Exception as e:
            registrar_transaccion(
                modulo="Auditoría",
                accion="Ejecutar conciliación",
                estado="ERROR",
                detalle=f"Error al procesar la conciliación: {e}",
                archivo_1=archivo_dian.name if archivo_dian else "",
                archivo_2=archivo_novasoft.name if archivo_novasoft else "",
                username=username,
                nombre_usuario=nombre_usuario,
                rol=rol
            )

            status_box(f"Error al procesar la conciliación: {e}", kind="error")