from datetime import date

import streamlit as st

from Service.auth_service import obtener_usuario_actual
from Service.transacciones_service import listar_transacciones
from Ui.components import section_header, soft_divider, status_box


def render_historial_page():
    section_header(
        "🧾 Mi historial de procesos",
        "Consulta los procesos que has ejecutado, incluyendo archivos, acciones, estado y detalle del resultado."
    )

    user_info = obtener_usuario_actual() or {}
    username = user_info.get("username", "")

    if not username:
        status_box("No fue posible identificar el usuario activo.", kind="error")
        return

    st.markdown("### Historial personal")

    for key, default in {
        "historial_modulo_filtro": "Todos",
        "historial_estado_filtro": "Todos",
        "historial_archivo_filtro": "",
        "historial_fecha_inicio": None,
        "historial_fecha_fin": None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    filtros = st.columns(6)
    with filtros[0]:
        modulo_filtro = st.selectbox(
            "Módulo",
            options=["Todos", "Diagnóstico", "Auditoría", "Generar XML"],
            key="historial_modulo_filtro",
        )
    with filtros[1]:
        estado_filtro = st.selectbox(
            "Estado",
            options=["Todos", "OK", "ERROR"],
            key="historial_estado_filtro",
        )
    with filtros[2]:
        archivo_filtro = st.text_input(
            "Archivo",
            placeholder="Nombre del archivo",
            key="historial_archivo_filtro",
        )
    with filtros[3]:
        fecha_inicio = st.date_input(
            "Desde",
            value=st.session_state["historial_fecha_inicio"],
            key="historial_fecha_inicio",
        )
    with filtros[4]:
        fecha_fin = st.date_input(
            "Hasta",
            value=st.session_state["historial_fecha_fin"],
            key="historial_fecha_fin",
        )
    with filtros[5]:
        if st.button("Limpiar filtros", use_container_width=True):
            for key in [
                "historial_modulo_filtro",
                "historial_estado_filtro",
                "historial_archivo_filtro",
                "historial_fecha_inicio",
                "historial_fecha_fin",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

    modulo_value = None if modulo_filtro == "Todos" else modulo_filtro
    estado_value = None if estado_filtro == "Todos" else estado_filtro
    fecha_inicio_value = fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else None
    fecha_fin_value = fecha_fin.strftime("%Y-%m-%d") if isinstance(fecha_fin, date) else None

    historial = listar_transacciones(
        usuario=username,
        modulo=modulo_value,
        estado=estado_value,
        fecha_inicio=fecha_inicio_value,
        fecha_fin=fecha_fin_value,
        archivo=archivo_filtro.strip() or None,
    )

    if historial.empty:
        st.info(
            "No se encontraron procesos con los filtros seleccionados. Prueba con otros valores o usa el botón para limpiar filtros."
        )
        return

    st.dataframe(historial, use_container_width=True, hide_index=True)

    soft_divider()

    st.markdown("### Exportar historial")
    csv_data = historial.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar historial (.csv)",
        data=csv_data,
        file_name=f"historial_{username}.csv",
        mime="text/csv",
        use_container_width=True,
    )
