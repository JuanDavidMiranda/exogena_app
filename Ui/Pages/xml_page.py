import traceback
import pandas as pd
import streamlit as st

from Service.diagnostic_service import diagnosticar_formato_excel_service
from Service.xml_service import (
    obtener_pestanas_validas_service,
    generar_xml_service
)
from Ui.components import (
    section_header,
    kpi_card,
    status_box,
    step_card,
    soft_divider,
    detectar_formato_desde_pestana
)


def render_xml_page():
    section_header(
        "📦 Generador XML para la DIAN",
        "Carga el archivo del formato, selecciona la pestaña a procesar, diagnostica la estructura y genera el XML oficial del reporte."
    )

    # ==========================
    # Configuración del proceso
    # ==========================
    st.markdown("### ⚙️ Configuración del proceso")
    col1, col2, col3 = st.columns(3)

    with col1:
        ano = st.number_input(
            "Año gravable",
            min_value=2020,
            max_value=2030,
            value=2025
        )

    with col2:
        envio = st.number_input(
            "Número de envío",
            min_value=1,
            max_value=9999,
            value=1
        )

    with col3:
        st.info("ℹ️ La versión XML se configura automáticamente según el formato.")

    soft_divider()

    # ==========================
    # Archivo y formato
    # ==========================
    st.markdown("### 📂 Archivo y selección de formato")
    archivo_excel = st.file_uploader(
        "Carga el archivo de Excel oficial (.xlsx)",
        type=["xlsx"],
        key="xml_file"
    )

    if archivo_excel is None:
        st.info("Carga un archivo Excel para iniciar el diagnóstico y la generación del XML.")
        return

    try:
        pestanas_formatos = obtener_pestanas_validas_service(archivo_excel)

        if not pestanas_formatos:
            status_box(
                "No se encontraron pestañas válidas para formatos DIAN en el archivo cargado.",
                kind="warning"
            )
            return

        pestana_seleccionada = st.selectbox(
            "Selecciona la pestaña del formato a procesar",
            pestanas_formatos
        )

        formato_detectado = detectar_formato_desde_pestana(pestana_seleccionada)

        # ==========================
        # Botones de acción (subidos para que se vean sin bajar tanto)
        # ==========================
        st.write("")
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            btn_diagnosticar = st.button(
                "🩺 Diagnosticar hoja antes de generar XML",
                width="stretch"
            )

        with col_btn2:
            btn_generar = st.button(
                "🚀 Generar XML",
                width="stretch"
            )

        soft_divider()

        # ==========================
        # Resumen rápido del contexto
        # ==========================
        st.markdown("### 🧾 Resumen del formato seleccionado")
        c1, c2, c3 = st.columns(3)

        with c1:
            kpi_card(
                "Pestaña seleccionada",
                pestana_seleccionada,
                "Hoja activa para el procesamiento"
            )

        with c2:
            kpi_card(
                "Formato detectado",
                formato_detectado if formato_detectado else "No detectado",
                "Detectado desde el nombre de la pestaña"
            )

        with c3:
            kpi_card(
                "Año / envío",
                f"{ano} / {envio}",
                "Parámetros del XML"
            )

        soft_divider()

        # ==========================
        # Flujo sugerido (ahora colapsable para no empujar botones hacia abajo)
        # ==========================
        with st.expander("🧭 Ver flujo de trabajo sugerido", expanded=False):
            step_card(
                "Paso 1 — Configuración del envío",
                "Define el año gravable y el número de envío que se usarán en la construcción del XML."
            )
            step_card(
                "Paso 2 — Selección del formato",
                "Carga el archivo de Excel y selecciona la pestaña del formato a procesar."
            )
            step_card(
                "Paso 3 — Diagnóstico previo",
                "Revisa estructura, columnas detectadas, advertencias y errores antes de generar el XML."
            )
            step_card(
                "Paso 4 — Generación final",
                "Genera el XML oficial y descárgalo cuando el diagnóstico sea consistente."
            )

        # =====================================================
        # ACCIÓN: DIAGNOSTICAR HOJA
        # =====================================================
        if btn_diagnosticar:
            if not formato_detectado:
                status_box(
                    "No fue posible detectar el formato DIAN desde el nombre de la pestaña seleccionada.",
                    kind="error"
                )
            else:
                diagnostico = diagnosticar_formato_excel_service(
                    archivo_excel=archivo_excel,
                    pestana_seleccionada=pestana_seleccionada,
                    formato_detectado=formato_detectado,
                    vigencia=ano
                )

                st.markdown("## 🧪 Diagnóstico detallado del formato")

                resumen = diagnostico["resumen"]
                columnas_detectadas = diagnostico["columnas_detectadas"]
                estructura = diagnostico["validacion_estructura"]
                errores = diagnostico["errores"]
                advertencias = diagnostico["advertencias"]
                estado_general = diagnostico["estado_general"]

                # ==========================
                # KPIs del diagnóstico
                # ==========================
                c1, c2, c3 = st.columns(3)

                with c1:
                    kpi_card(
                        "Registros detectados",
                        resumen["total_registros"],
                        "Filas útiles identificadas"
                    )

                with c2:
                    kpi_card(
                        "Columnas encontradas",
                        resumen["columnas_encontradas"],
                        "Encabezados leídos del archivo"
                    )

                with c3:
                    kpi_card(
                        "Filas TOTAL detectadas",
                        resumen["filas_total_detectadas"],
                        "Posibles filas de resumen"
                    )

                # ==========================
                # Estado general
                # ==========================
                if estado_general == "OK":
                    status_box(
                        "Diagnóstico sin observaciones críticas. El archivo parece listo para la generación del XML.",
                        kind="ok"
                    )
                elif estado_general == "CON ADVERTENCIAS":
                    status_box(
                        "El archivo presenta advertencias. Se recomienda revisar antes de generar el XML.",
                        kind="warning"
                    )
                else:
                    status_box(
                        "El archivo presenta errores que deberían corregirse antes de generar el XML.",
                        kind="error"
                    )

                soft_divider()

                # ==========================
                # Mapeo de columnas detectadas
                # ==========================
                st.markdown("### 🧭 Mapeo de columnas detectadas")

                df_cols = pd.DataFrame(
                    [
                        {
                            "Campo lógico": campo,
                            "Columna detectada": columna if columna else "No detectada",
                            "Estado": "OK" if columna else "Revisar"
                        }
                        for campo, columna in columnas_detectadas.items()
                    ]
                )

                st.dataframe(
                    df_cols,
                    width="stretch",
                    hide_index=True
                )

                soft_divider()

                # ==========================
                # Validación de estructura mínima
                # ==========================
                st.markdown("### 🏗️ Validación de estructura mínima")
                col_e1, col_e2 = st.columns(2)

                with col_e1:
                    st.markdown("**Columnas mínimas presentes**")
                    if estructura["presentes"]:
                        for item in estructura["presentes"]:
                            st.write(f"• {item}")
                    else:
                        st.write("• Ninguna")

                with col_e2:
                    st.markdown("**Columnas mínimas faltantes**")
                    if estructura["faltantes"]:
                        for item in estructura["faltantes"]:
                            st.write(f"• {item}")
                    else:
                        st.write("• Ninguna")

                soft_divider()

                # ==========================
                # Errores y advertencias
                # ==========================
                if errores:
                    st.markdown("### ❌ Errores detectados")
                    for err in errores:
                        st.error(err)

                if advertencias:
                    st.markdown("### ⚠️ Advertencias")
                    for adv in advertencias:
                        st.warning(adv)

                if not errores and not advertencias:
                    status_box(
                        "No se detectaron errores ni advertencias relevantes para este formato.",
                        kind="ok"
                    )

        # =====================================================
        # ACCIÓN: GENERAR XML
        # =====================================================
        if btn_generar:
            if not formato_detectado:
                status_box(
                    "No fue posible detectar el formato DIAN desde el nombre de la pestaña seleccionada.",
                    kind="error"
                )
            else:
                with st.spinner(f"Procesando la pestaña '{pestana_seleccionada}'..."):
                    resultado = generar_xml_service(
                        archivo_excel=archivo_excel,
                        pestana_seleccionada=pestana_seleccionada,
                        ano=ano,
                        envio=envio
                    )

                status_box(
                    f"XML del Formato {resultado['formato_detectado']} generado exitosamente.",
                    kind="ok"
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    kpi_card(
                        "Formato generado",
                        resultado["formato_detectado"],
                        "Formato DIAN procesado"
                    )

                with c2:
                    kpi_card(
                        "Terceros reportados",
                        f"{resultado['total_registros']:,}",
                        "Registros incluidos en el XML"
                    )

                with c3:
                    kpi_card(
                        "Cuantía total",
                        f"${resultado['total_cuantias']:,.0f}",
                        "Suma total informada"
                    )

                st.download_button(
                    label="💾 Descargar archivo XML oficial",
                    data=resultado["xml_bytes"],
                    file_name=resultado["nombre_archivo"],
                    mime="text/xml",
                    width="stretch"
                )

    except Exception as e:
        status_box(f"Error durante el procesamiento del XML: {e}", kind="error")
        st.code(traceback.format_exc())