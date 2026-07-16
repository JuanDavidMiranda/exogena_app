import pandas as pd
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
    historial = listar_transacciones(usuario=username)

    if historial.empty:
        st.info("Aún no tienes procesos registrados en el sistema.")
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
