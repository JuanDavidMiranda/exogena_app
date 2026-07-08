import pandas as pd
import streamlit as st

from Service.diagnostic_service import ejecutar_diagnostico_service
from Ui.components import section_header, kpi_card, status_box, soft_divider


def render_diagnostico_page():
    section_header(
        "📋 Diagnóstico preliminar de formatos",
        "Analiza el libro de Excel y detecta qué formatos DIAN contienen información útil para reporte."
    )

    # ==========================
    # Bloque de carga
    # ==========================
    st.markdown("### 📂 Archivo de entrada")
    st.caption(
        "Carga el libro de Excel que contiene las hojas de formatos DIAN para realizar "
        "la validación preliminar de estructura y presencia de información."
    )

    archivo_maestro = st.file_uploader(
        "Sube el libro de Excel con los formatos DIAN",
        type=["xlsx"],
        key="diag_preliminar"
    )

    if archivo_maestro is None:
        st.info("Carga un archivo Excel para ejecutar el diagnóstico preliminar.")
        return

    st.write("")
    c_info1, c_info2 = st.columns([2, 1])

    with c_info1:
        st.markdown(f"""
        <div style="
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 8px;
        ">
            <strong>📄 Archivo cargado:</strong> {archivo_maestro.name}
        </div>
        """, unsafe_allow_html=True)

    with c_info2:
        ejecutar = st.button(
            "▶️ Ejecutar diagnóstico",
            use_container_width=True,
            type="primary"
        )

    if not ejecutar:
        st.info("Presiona **Ejecutar diagnóstico** para analizar el archivo cargado.")
        return

    # ==========================
    # Ejecución del diagnóstico
    # ==========================
    try:
        with st.spinner("Analizando archivo y detectando formatos..."):
            resultado = ejecutar_diagnostico_service(archivo_maestro)

        if not resultado["resultados"]:
            status_box(
                "No se identificaron pestañas válidas dentro del archivo cargado.",
                kind="warning"
            )
            return

        total_terceros = sum(
            fila.get("Terceros Detectados", 0)
            for fila in resultado["resultados"]
        )

        formatos_con_datos = resultado.get("formatos_con_datos", 0)
        formatos_vacios = resultado.get("formatos_vacios", 0)
        total_formatos = resultado.get("total_formatos", 0)

        # ==========================
        # Resumen general
        # ==========================
        st.write("")
        st.markdown("## 🧾 Resumen del diagnóstico")

        if formatos_con_datos > 0:
            status_box(
                f"Se analizaron <strong>{total_formatos}</strong> formatos. "
                f"Se detectó información útil en <strong>{formatos_con_datos}</strong> "
                f"formato(s), por lo que el archivo requiere revisión para una posible "
                f"generación de XML.",
                kind="ok"
            )
        else:
            status_box(
                f"Se analizaron <strong>{total_formatos}</strong> formatos, pero no se "
                f"detectó información útil para reporte en esta ejecución.",
                kind="warning"
            )

        # ==========================
        # KPIs principales
        # ==========================
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            kpi_card(
                "Formatos analizados",
                total_formatos,
                "Pestañas válidas encontradas"
            )

        with c2:
            kpi_card(
                "Formatos con datos",
                formatos_con_datos,
                "Formatos con terceros detectados"
            )

        with c3:
            kpi_card(
                "Formatos vacíos",
                formatos_vacios,
                "Sin registros útiles para reporte"
            )

        with c4:
            kpi_card(
                "Terceros detectados",
                f"{total_terceros:,}",
                "Total de registros identificados"
            )

        soft_divider()

        # ==========================
        # Resultado detallado
        # ==========================
        st.markdown("### 📑 Resultado detallado del análisis")

        df_resultados = pd.DataFrame(resultado["resultados"])

        if "Terceros Detectados" in df_resultados.columns:
            df_resultados = df_resultados.sort_values(
                by="Terceros Detectados",
                ascending=False
            )

        st.dataframe(df_resultados, use_container_width=True)

        soft_divider()

        # ==========================
        # Plan de acción sugerido
        # ==========================
        st.markdown("### 💡 Plan de acción sugerido")

        formatos_utiles = []
        formatos_sin_datos = []

        for fila in resultado["resultados"]:
            formato = fila.get("Formato DIAN", "N/A")
            pestana = fila.get("Nombre de la Pestaña", "N/A")
            terceros = fila.get("Terceros Detectados", 0)
            dictamen = fila.get("Dictamen", "")

            if "🟢" in dictamen:
                formatos_utiles.append((formato, pestana, terceros))
            else:
                formatos_sin_datos.append((formato, pestana, terceros))

        if formatos_utiles:
            status_box(
                f"Se encontraron <strong>{len(formatos_utiles)}</strong> formato(s) con "
                f"información útil. Se recomienda validar estas hojas y considerar su "
                f"posterior generación de XML.",
                kind="ok"
            )

            for formato, pestana, terceros in formatos_utiles:
                st.markdown(
                    f"""
                    <div style="
                        background: #F0FDF4;
                        border: 1px solid #BBF7D0;
                        border-radius: 14px;
                        padding: 14px 16px;
                        margin-bottom: 10px;
                    ">
                        <strong>{formato}</strong> · {pestana}<br>
                        Registros detectados: <strong>{terceros}</strong><br>
                        Acción sugerida: revisar la hoja y validar su generación en XML.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if formatos_sin_datos:
            status_box(
                f"Se encontraron <strong>{len(formatos_sin_datos)}</strong> formato(s) "
                f"sin información útil para reporte en esta ejecución.",
                kind="warning"
            )

            for formato, pestana, _ in formatos_sin_datos:
                st.markdown(
                    f"""
                    <div style="
                        background: #FFF7ED;
                        border: 1px solid #FED7AA;
                        border-radius: 14px;
                        padding: 14px 16px;
                        margin-bottom: 10px;
                    ">
                        <strong>{formato}</strong> · {pestana}<br>
                        Acción sugerida: puede omitirse en esta ejecución, salvo validación manual.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        status_box(f"Error en el diagnóstico preliminar: {e}", kind="error")