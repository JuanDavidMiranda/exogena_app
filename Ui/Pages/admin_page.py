import streamlit as st
import pandas as pd

from Service.transacciones_service import (
    obtener_resumen_admin,
    listar_transacciones,
    listar_usuarios,
    obtener_uso_por_modulo,
    obtener_errores_por_modulo
)


def render_admin_page():
    st.markdown("## 📊 Panel Administrativo")
    st.caption("Vista transversal del uso del sistema, historial y métricas generales.")

    # ==========================================================
    # KPIs
    # ==========================================================
    resumen = obtener_resumen_admin()

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    with c1:
        st.metric("Usuarios activos", resumen.get("usuarios", 0))

    with c2:
        st.metric("Transacciones", resumen.get("transacciones", 0))

    with c3:
        st.metric("Diagnósticos", resumen.get("diagnosticos", 0))

    with c4:
        st.metric("Auditorías", resumen.get("auditorias", 0))

    with c5:
        st.metric("XML generados", resumen.get("xml_generados", 0))

    with c6:
        st.metric("Errores", resumen.get("errores", 0))

    st.markdown("---")

    # ==========================================================
    # Resumen por módulo
    # ==========================================================
    st.markdown("### 📌 Uso del sistema por módulo")

    uso_modulo = obtener_uso_por_modulo()
    if not uso_modulo.empty:
        st.dataframe(uso_modulo, width="stretch", hide_index=True)
    else:
        st.info("Aún no hay transacciones registradas.")

    st.markdown("### ⚠️ Errores por módulo")
    errores_modulo = obtener_errores_por_modulo()

    if not errores_modulo.empty:
        st.dataframe(errores_modulo, width="stretch", hide_index=True)
    else:
        st.success("No hay errores registrados hasta el momento.")

    st.markdown("---")

    # ==========================================================
    # Historial de transacciones
    # ==========================================================
    st.markdown("### 🧾 Historial de transacciones")

    usuarios_df = listar_usuarios()
    usuarios_opciones = ["Todos"]
    if not usuarios_df.empty and "username" in usuarios_df.columns:
        usuarios_opciones += usuarios_df["username"].dropna().astype(str).tolist()

    modulos_opciones = [
        "Todos",
        "Diagnóstico",
        "Auditoría",
        "Generar XML"
    ]

    estados_opciones = ["Todos", "OK", "ERROR"]

    f1, f2, f3 = st.columns(3)

    with f1:
        filtro_usuario = st.selectbox("Usuario", usuarios_opciones)

    with f2:
        filtro_modulo = st.selectbox("Módulo", modulos_opciones)

    with f3:
        filtro_estado = st.selectbox("Estado", estados_opciones)

    usuario_val = None if filtro_usuario == "Todos" else filtro_usuario
    modulo_val = None if filtro_modulo == "Todos" else filtro_modulo
    estado_val = None if filtro_estado == "Todos" else filtro_estado

    df_transacciones = listar_transacciones(
        usuario=usuario_val,
        modulo=modulo_val,
        estado=estado_val
    )

    if not df_transacciones.empty:
        st.dataframe(df_transacciones, width="stretch", hide_index=True)
    else:
        st.info("No hay transacciones para los filtros seleccionados.")

    st.markdown("---")

    # ==========================================================
    # Usuarios registrados
    # ==========================================================
    st.markdown("### 👥 Usuarios registrados")

    if not usuarios_df.empty:
        st.dataframe(usuarios_df, width="stretch", hide_index=True)
    else:
        st.info("No hay usuarios registrados en SQLite todavía.")