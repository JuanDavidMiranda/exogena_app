import io
import pandas as pd
import streamlit as st

from Service.audit_service import ejecutar_auditoria_service
import Service.audit_service as audit_module
st.write("ARCHIVO AUDIT SERVICE:", audit_module.__file__)

from Ui.components import section_header, kpi_card, status_box, soft_divider
from Service.transacciones_service import registrar_transaccion



def _tabla_exportable(df):
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


def render_auditoria_page():
    section_header(
        "🔄 Auditoría de datos: Novasoft vs DIAN",
        "Compara las compras factura por factura sin asumir que DIAN y Novasoft utilizan el mismo número de factura."
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
            "Sube el reporte de DIAN",
            type=["xlsx", "xls", "csv"],
            key="dian_file"
        )

    if not archivo_novasoft or not archivo_dian:
        st.info("Carga ambos archivos para ejecutar la auditoría y conciliación.")
        return

    st.markdown("### 🧠 Criterio de identificación")
    st.info(
        "El sistema no compara el número de factura entre los archivos. "
        "Primero consolida Novasoft por NIT + documento + fecha y calcula el total. "
        "Luego busca cada factura DIAN por NIT + fecha + valor. Si no hay coincidencia exacta, "
        "busca una coincidencia única por NIT + valor dentro de la tolerancia de días."
    )

    c1, c2 = st.columns(2)
    with c1:
        tolerancia_dias = st.number_input(
            "Tolerancia de fecha para coincidencias probables (días)",
            min_value=0,
            max_value=15,
            value=3,
            step=1,
            help="La coincidencia exacta siempre exige la misma fecha. Esta tolerancia solo se usa como segunda oportunidad y queda marcada como 'Probable'."
        )
    with c2:
        tolerancia_monto = st.number_input(
            "Tolerancia de valor ($)",
            min_value=0.0,
            max_value=10000.0,
            value=1.0,
            step=1.0,
            help="Permite pequeñas diferencias de redondeo."
        )

    with st.expander("ℹ️ ¿Cómo se identifica una factura?", expanded=False):
        st.markdown(
            """
            **1. NIT:** relaciona el proveedor/emisor en ambos sistemas.  
            **2. Fecha:** es el principal identificador adicional.  
            **3. Valor:** confirma que la factura corresponde al mismo documento.  
            **4. Número de factura:** se conserva únicamente como referencia de cada sistema; no se usa para cruzarlos.  
            **5. Regla uno-a-uno:** un documento de Novasoft no puede ser asignado a dos facturas DIAN.  
            **6. Notas crédito:** no se mezclan con las facturas electrónicas en este cruce de compras.
            """
        )

    if st.button("📊 Ejecutar conciliación", width="stretch"):
        try:
            resultado = ejecutar_auditoria_service(
                archivo_dian,
                archivo_novasoft,
                tolerancia_monto=tolerancia_monto,
                tolerancia_dias=tolerancia_dias,
            )

            if not resultado.get("ok"):
                registrar_transaccion(
                    modulo="Auditoría",
                    accion="Ejecutar conciliación",
                    estado="ERROR",
                    detalle=resultado.get("mensaje", "Ocurrió un error en la conciliación."),
                    archivo_1=archivo_dian.name,
                    archivo_2=archivo_novasoft.name,
                    username=username,
                    nombre_usuario=nombre_usuario,
                    rol=rol
                )
                status_box(resultado.get("mensaje", "Ocurrió un error en la conciliación."), kind="error")
                return

            resumen = resultado["resumen"]
            detalle = resultado["detalle"]
            solo_dian = resultado["solo_dian"]
            solo_novasoft = resultado["solo_novasoft"]
            dif_montos = resultado["dif_montos"]
            conciliados_df = resultado["conciliados_df"]
            probables_df = resultado.get("probables_df", pd.DataFrame())
            ambiguas_df = resultado.get("ambiguas_df", pd.DataFrame())

            status_box(resultado["mensaje"], kind="ok")

            registrar_transaccion(
                modulo="Auditoría",
                accion="Ejecutar conciliación",
                estado="OK",
                detalle=(
                    f"DIAN: {archivo_dian.name}. Novasoft: {archivo_novasoft.name}. "
                    f"Exactas: {resumen['conciliados']}. Probables: {resumen['probables']}. "
                    f"Ambiguas: {resumen['ambiguas']}. No encontradas: {resumen['no_encontradas']}."
                ),
                archivo_1=archivo_dian.name,
                archivo_2=archivo_novasoft.name,
                username=username,
                nombre_usuario=nombre_usuario,
                rol=rol
            )

            soft_divider()
            st.markdown("### Resultado de la conciliación")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                kpi_card("Facturas DIAN", resumen["facturas_dian"], "Facturas electrónicas analizadas")
            with c2:
                kpi_card("🟢 Exactas", resumen["conciliados"], "NIT + fecha + valor")
            with c3:
                kpi_card("🟡 Probables", resumen["probables"], "NIT + valor + fecha cercana")
            with c4:
                kpi_card("🔴 No encontradas", resumen["no_encontradas"], "Sin coincidencia válida")

            st.markdown("")
            c5, c6, c7, c8 = st.columns(4)
            with c5:
                kpi_card("🟠 Ambiguas", resumen["ambiguas"], "Requieren revisión manual")
            with c6:
                kpi_card("Facturas Novasoft", resumen["facturas_novasoft"], "Documentos consolidados")
            with c7:
                kpi_card("Solo Novasoft", resumen["solo_novasoft"], "Sin factura DIAN asociada")
            with c8:
                kpi_card("Diferencia total", f"${resumen['diferencia_total']:,.0f}", "DIAN - Novasoft")

            soft_divider()
            st.markdown("### 📋 Detalle factura por factura")
            st.dataframe(detalle, width="stretch", hide_index=True)

            if not probables_df.empty:
                st.markdown("#### 🟡 Coincidencias probables")
                st.caption("Estas coincidencias usan NIT + valor y una fecha cercana. Deben revisarse antes de considerarlas definitivas.")
                st.dataframe(probables_df, width="stretch", hide_index=True)

            if not ambiguas_df.empty:
                st.markdown("#### 🟠 Coincidencias ambiguas")
                st.dataframe(ambiguas_df, width="stretch", hide_index=True)

            if not solo_dian.empty:
                st.markdown("#### 🔴 Facturas DIAN no encontradas")
                st.dataframe(solo_dian, width="stretch", hide_index=True)

            if not solo_novasoft.empty:
                st.markdown("#### 🧾 Documentos Novasoft sin asociación")
                st.dataframe(solo_novasoft, width="stretch", hide_index=True)

            if not dif_montos.empty:
                st.markdown("#### 💰 Diferencias de monto")
                st.dataframe(dif_montos, width="stretch", hide_index=True)

            if not conciliados_df.empty:
                with st.expander("🟢 Ver coincidencias exactas", expanded=False):
                    st.dataframe(conciliados_df, width="stretch", hide_index=True)

            soft_divider()
            st.markdown("### 📥 Exportar resultado de conciliación")
            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                resumen_df = pd.DataFrame([{
                    "Total DIAN": resumen["total_dian"],
                    "Total Novasoft": resumen["total_novasoft"],
                    "Diferencia total": resumen["diferencia_total"],
                    "Facturas DIAN": resumen["facturas_dian"],
                    "Facturas Novasoft": resumen["facturas_novasoft"],
                    "Exactas": resumen["conciliados"],
                    "Probables": resumen["probables"],
                    "Ambiguas": resumen["ambiguas"],
                    "No encontradas": resumen["no_encontradas"],
                    "Solo Novasoft": resumen["solo_novasoft"],
                    "Tolerancia días": tolerancia_dias,
                    "Tolerancia valor": tolerancia_monto,
                }])
                resumen_df.to_excel(writer, sheet_name="Resumen", index=False)
                _tabla_exportable(detalle).to_excel(writer, sheet_name="Detalle", index=False)
                _tabla_exportable(probables_df).to_excel(writer, sheet_name="Probables", index=False)
                _tabla_exportable(ambiguas_df).to_excel(writer, sheet_name="Ambiguas", index=False)
                _tabla_exportable(solo_dian).to_excel(writer, sheet_name="Solo DIAN", index=False)
                _tabla_exportable(solo_novasoft).to_excel(writer, sheet_name="Solo Novasoft", index=False)
                _tabla_exportable(dif_montos).to_excel(writer, sheet_name="Dif Montos", index=False)
                _tabla_exportable(conciliados_df).to_excel(writer, sheet_name="Exactas", index=False)

            buffer.seek(0)
            descarga = st.download_button(
                "📥 Descargar conciliación final (.xlsx)",
                data=buffer,
                file_name="conciliacion_factura_por_factura.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )

            if descarga:
                registrar_transaccion(
                    modulo="Auditoría",
                    accion="Descargar conciliación",
                    estado="OK",
                    detalle="Descarga del archivo de conciliación factura por factura.",
                    archivo_1=archivo_dian.name,
                    archivo_2=archivo_novasoft.name,
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
