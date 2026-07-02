import pandas as pd
import streamlit as st

from Service.diagnostic_service import ejecutar_diagnostico_service
from Ui.components import section_header, kpi_card, status_box, soft_divider


def render_diagnostico_page():
    section_header(
        "📋 Diagnóstico preliminar de formatos",
        "Analiza el libro de Excel y determina qué formatos DIAN parecen tener información para ser reportados."
    )

    st.markdown("### Archivo de entrada")
    archivo_maestro = st.file_uploader(
        "Sube el libro de Excel con los formatos DIAN",
        type=["xlsx"],
        key="diag_preliminar"
    )

    if archivo_maestro is None:
        st.info("Carga un archivo Excel para ejecutar el diagnóstico preliminar.")
        return

    try:
        resultado = ejecutar_diagnostico_service(archivo_maestro)

        if not resultado["resultados"]:
            status_box(
                "No se identificaron pestañas válidas dentro del archivo cargado.",
                kind="warning"
            )
            return

        total_terceros = sum(r["Terceros Detectados"] for r in resultado["resultados"])

        # ==========================
        # KPIs principales
        # ==========================
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card(
                "Formatos analizados",
                resultado["total_formatos"],
                "Pestañas válidas encontradas"
            )
        with c2:
            kpi_card(
                "Formatos con datos",
                resultado["formatos_con_datos"],
                "Formatos con terceros detectados"
            )
        with c3:
            kpi_card(
                "Formatos vacíos",
                resultado["formatos_vacios"],
                "Formatos sin registros útiles"
            )
        with c4:
            kpi_card(
                "Terceros detectados",
                f"{total_terceros:,}",
                "Suma de registros identificados"
            )

        soft_divider()

        # ==========================
        # Tabla de resultados
        # ==========================
        st.markdown("### Resultado del análisis")
        df_resultados = pd.DataFrame(resultado["resultados"])
        st.dataframe(df_resultados, use_container_width=True)

        soft_divider()

        # ==========================
        # Plan de acción sugerido
        # ==========================
        st.markdown("### 💡 Plan de acción sugerido")

        for fila in resultado["resultados"]:
            formato = fila["Formato DIAN"]
            pestana = fila["Nombre de la Pestaña"]
            terceros = fila["Terceros Detectados"]
            dictamen = fila["Dictamen"]

            if "🟢" in dictamen:
                status_box(
                    f"<strong>{formato} ({pestana})</strong>: "
                    f"Se detectaron <strong>{terceros}</strong> registros. "
                    f"Se recomienda revisar esta hoja y considerar su generación en XML.",
                    kind="ok"
                )
            else:
                status_box(
                    f"<strong>{formato} ({pestana})</strong>: "
                    f"No presenta información útil para reporte. Puede omitirse en esta ejecución.",
                    kind="warning"
                )

    except Exception as e:
        status_box(f"Error en el diagnóstico preliminar: {e}", kind="error")