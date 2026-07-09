import io
import pandas as pd
import streamlit as st

from Service.audit_service import ejecutar_auditoria_service
from Ui.components import section_header, kpi_card, status_box, soft_divider


def render_auditoria_page():
    section_header(
        "🔄 Auditoría de datos: Novasoft vs formatos DIAN",
        "Cruza el archivo base de Novasoft con el borrador del formato DIAN para identificar diferencias, faltantes y registros exclusivos."
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
            type=["xlsx", "csv", "xls"],
            key="dian_file"
        )

    if not archivo_novasoft or not archivo_dian:
        st.info("Carga ambos archivos para ejecutar la auditoría y conciliación.")
        return

    try:
        resultado = ejecutar_auditoria_service(archivo_novasoft, archivo_dian)

        resumen = resultado["resumen"]
        dif_montos = resultado["dif_montos"]
        solo_dian = resultado["solo_dian"]
        solo_novasoft = resultado["solo_novasoft"]

        # ==========================
        # KPIs principales
        # ==========================
        st.markdown("### Resultado de la conciliación")
        c1, c2, c3 = st.columns(3)

        with c1:
            kpi_card(
                "Diferencias en montos",
                resumen["diferencias_montos"],
                "Registros con cuantías distintas"
            )

        with c2:
            kpi_card(
                "Solo en DIAN",
                resumen["solo_dian"],
                "Registros que no aparecen en Novasoft"
            )

        with c3:
            kpi_card(
                "Solo en Novasoft",
                resumen["solo_novasoft"],
                "Registros que no aparecen en DIAN"
            )

        status_box(
            "Cruce completado con éxito. Revisa los tres grupos de diferencias y descarga el consolidado final.",
            kind="ok"
        )

        soft_divider()

        # ==========================
        # Resultados en expanders
        # ==========================
        with st.expander("📌 Ver diferencias de montos", expanded=False):
            if isinstance(dif_montos, pd.DataFrame) and not dif_montos.empty:
                st.dataframe(dif_montos, use_container_width=True)
            else:
                st.info("No se encontraron diferencias de montos.")

        with st.expander("📌 Ver registros solo en DIAN", expanded=False):
            if isinstance(solo_dian, pd.DataFrame) and not solo_dian.empty:
                st.dataframe(solo_dian, use_container_width=True)
            else:
                st.info("No se encontraron registros exclusivos en DIAN.")

        with st.expander("📌 Ver registros solo en Novasoft", expanded=False):
            if isinstance(solo_novasoft, pd.DataFrame) and not solo_novasoft.empty:
                st.dataframe(solo_novasoft, use_container_width=True)
            else:
                st.info("No se encontraron registros exclusivos en Novasoft.")

        soft_divider()

        # ==========================
        # Exportar consolidado
        # ==========================
        st.markdown("### 📥 Exportar resultado de conciliación")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            dif_montos.to_excel(writer, sheet_name="Diferencias_Montos", index=False)
            solo_dian.to_excel(writer, sheet_name="Solo_en_DIAN", index=False)
            solo_novasoft.to_excel(writer, sheet_name="Solo_en_Novasoft", index=False)

        buffer.seek(0)

        st.download_button(
            label="📥 Descargar conciliación final (.xlsx)",
            data=buffer,
            file_name="conciliacion_final_exogena.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        status_box(f"Error al procesar la conciliación: {e}", kind="error")