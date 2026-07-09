import io
import pandas as pd
import streamlit as st

from Service.audit_service import ejecutar_auditoria_service
from Ui.components import section_header, kpi_card, status_box, soft_divider


def render_auditoria_page():
    section_header(
        "🔄 Auditoría de datos: Novasoft vs formatos DIAN",
        "Cruza el archivo base de Novasoft con el borrador del formato DIAN para identificar diferencias en valores por tercero."
    )

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

    if st.button("📊 Ejecutar conciliación", width="stretch"):
        try:
            # OJO: tu service recibe primero DIAN y luego Novasoft
            resultado = ejecutar_auditoria_service(archivo_dian, archivo_novasoft)

            if not resultado.get("ok"):
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
            # Descargar resultado
            # ==========================
            st.markdown("### 📥 Exportar resultado de conciliación")

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                detalle.to_excel(writer, sheet_name="Conciliacion", index=False)

            buffer.seek(0)

            st.download_button(
                label="📥 Descargar conciliación final (.xlsx)",
                data=buffer,
                file_name="conciliacion_final_exogena.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

        except Exception as e:
            status_box(f"Error al procesar la conciliación: {e}", kind="error")