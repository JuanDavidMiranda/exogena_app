import streamlit as st
import pandas as pd

from Service.transacciones_service import (
    obtener_resumen_admin,
    listar_transacciones,
    listar_usuarios,
    obtener_uso_por_modulo,
    obtener_errores_por_modulo,
    actualizar_rol_usuario
)


def _safe_metric_delta(actual: int, total: int) -> str:
    if total <= 0:
        return "0%"
    return f"{round((actual / total) * 100, 1)}%"


def render_admin_page():
    st.markdown("## 📊 Panel Administrativo")
    st.caption(
        "Vista transversal del sistema: uso por módulo, errores, historial de actividad y gestión de usuarios."
    )

    # ==========================================================
    # CARGA DE DATOS
    # ==========================================================
    resumen = obtener_resumen_admin()
    usuarios_df = listar_usuarios()
    uso_modulo = obtener_uso_por_modulo()
    errores_modulo = obtener_errores_por_modulo()
    df_transacciones = listar_transacciones()

    total_transacciones = int(resumen.get("transacciones", 0))
    total_errores = int(resumen.get("errores", 0))
    total_usuarios = int(resumen.get("usuarios", 0))
    total_diagnosticos = int(resumen.get("diagnosticos", 0))
    total_auditorias = int(resumen.get("auditorias", 0))
    total_xml = int(resumen.get("xml_generados", 0))

    # ==========================================================
    # NORMALIZAR FECHA PARA FILTROS / MÉTRICAS
    # ==========================================================
    if not df_transacciones.empty and "Fecha" in df_transacciones.columns:
        df_transacciones["Fecha_dt"] = pd.to_datetime(
            df_transacciones["Fecha"], errors="coerce"
        )
    else:
        df_transacciones["Fecha_dt"] = pd.NaT

    # ==========================================================
    # KPIS PRINCIPALES
    # ==========================================================
    st.markdown("### 📌 Resumen general")

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    modulo_mas_usado = "-"
    if not uso_modulo.empty and "Módulo" in uso_modulo.columns:
        modulo_mas_usado = str(uso_modulo.iloc[0]["Módulo"])

    usuario_mas_activo = "-"
    if not df_transacciones.empty and "Usuario" in df_transacciones.columns:
        usuarios_actividad = (
            df_transacciones["Usuario"]
            .fillna("")
            .astype(str)
            .replace("", pd.NA)
            .dropna()
            .value_counts()
        )
        if not usuarios_actividad.empty:
            usuario_mas_activo = usuarios_actividad.index[0]

    with c1:
        st.metric("Usuarios activos", total_usuarios)

    with c2:
        st.metric("Transacciones", total_transacciones)

    with c3:
        st.metric("Errores", total_errores, _safe_metric_delta(total_errores, total_transacciones))

    with c4:
        st.metric("Diagnósticos", total_diagnosticos)

    with c5:
        st.metric("Auditorías", total_auditorias)

    with c6:
        st.metric("XML generados", total_xml)

    x1, x2 = st.columns(2)
    with x1:
        st.info(f"**Módulo más usado:** {modulo_mas_usado}")
    with x2:
        st.info(f"**Usuario con más actividad:** {usuario_mas_activo}")

    st.markdown("---")

    # ==========================================================
    # ANALÍTICA VISUAL
    # ==========================================================
    st.markdown("### 📈 Analítica del sistema")

    g1, g2 = st.columns(2)

    with g1:
        st.markdown("#### Uso por módulo")
        if not uso_modulo.empty:
            uso_chart = uso_modulo.set_index("Módulo")
            st.bar_chart(uso_chart)
            st.dataframe(uso_modulo, width="stretch", hide_index=True)
        else:
            st.info("Aún no hay transacciones registradas.")

    with g2:
        st.markdown("#### Errores por módulo")
        if not errores_modulo.empty:
            errores_chart = errores_modulo.set_index("Módulo")
            st.bar_chart(errores_chart)
            st.dataframe(errores_modulo, width="stretch", hide_index=True)
        else:
            st.success("No hay errores registrados hasta el momento.")

    st.markdown("---")

    # ==========================================================
    # HISTORIAL AVANZADO
    # ==========================================================
    st.markdown("### 🧾 Historial de transacciones")

    # Opciones de filtros
    usuarios_opciones = ["Todos"]
    if not usuarios_df.empty and "username" in usuarios_df.columns:
        usuarios_opciones += (
            usuarios_df["username"].dropna().astype(str).drop_duplicates().tolist()
        )

    modulos_opciones = ["Todos"]
    if not df_transacciones.empty and "Módulo" in df_transacciones.columns:
        modulos_detectados = (
            df_transacciones["Módulo"].dropna().astype(str).drop_duplicates().tolist()
        )
        modulos_opciones += sorted(modulos_detectados)

    estados_opciones = ["Todos"]
    if not df_transacciones.empty and "Estado" in df_transacciones.columns:
        estados_detectados = (
            df_transacciones["Estado"].dropna().astype(str).drop_duplicates().tolist()
        )
        estados_opciones += sorted(estados_detectados)

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        filtro_usuario = st.selectbox("Usuario", usuarios_opciones)

    with f2:
        filtro_modulo = st.selectbox("Módulo", modulos_opciones)

    with f3:
        filtro_estado = st.selectbox("Estado", estados_opciones)

    with f4:
        solo_hoy = st.checkbox("Solo hoy", value=False)

    # Filtro de fechas
    if not df_transacciones.empty and df_transacciones["Fecha_dt"].notna().any():
        min_fecha = df_transacciones["Fecha_dt"].min().date()
        max_fecha = df_transacciones["Fecha_dt"].max().date()
    else:
        hoy = pd.Timestamp.now().date()
        min_fecha = hoy
        max_fecha = hoy

    d1, d2 = st.columns(2)
    with d1:
        fecha_desde = st.date_input("Fecha desde", value=min_fecha)
    with d2:
        fecha_hasta = st.date_input("Fecha hasta", value=max_fecha)

    # ==========================================================
    # APLICAR FILTROS SOBRE EL DATAFRAME
    # ==========================================================
    df_filtrado = df_transacciones.copy()

    if filtro_usuario != "Todos" and "Usuario" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Usuario"].astype(str) == filtro_usuario]

    if filtro_modulo != "Todos" and "Módulo" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Módulo"].astype(str) == filtro_modulo]

    if filtro_estado != "Todos" and "Estado" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Estado"].astype(str) == filtro_estado]

    if "Fecha_dt" in df_filtrado.columns and df_filtrado["Fecha_dt"].notna().any():
        if solo_hoy:
            hoy = pd.Timestamp.now().date()
            df_filtrado = df_filtrado[df_filtrado["Fecha_dt"].dt.date == hoy]
        else:
            df_filtrado = df_filtrado[
                (df_filtrado["Fecha_dt"].dt.date >= fecha_desde)
                & (df_filtrado["Fecha_dt"].dt.date <= fecha_hasta)
            ]

    # KPIs rápidos del filtro
    st.markdown("#### Resumen del filtro aplicado")
    r1, r2, r3, r4 = st.columns(4)

    total_filtrado = len(df_filtrado)
    errores_filtrados = 0
    if not df_filtrado.empty and "Estado" in df_filtrado.columns:
        errores_filtrados = (df_filtrado["Estado"].astype(str) == "ERROR").sum()

    modulos_filtrados = 0
    if not df_filtrado.empty and "Módulo" in df_filtrado.columns:
        modulos_filtrados = df_filtrado["Módulo"].nunique()

    usuarios_filtrados = 0
    if not df_filtrado.empty and "Usuario" in df_filtrado.columns:
        usuarios_filtrados = df_filtrado["Usuario"].nunique()

    with r1:
        st.metric("Transacciones filtradas", total_filtrado)
    with r2:
        st.metric("Errores filtrados", int(errores_filtrados))
    with r3:
        st.metric("Módulos involucrados", int(modulos_filtrados))
    with r4:
        st.metric("Usuarios involucrados", int(usuarios_filtrados))

    # Ordenar y limpiar columna auxiliar
    if not df_filtrado.empty and "Fecha_dt" in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values("Fecha_dt", ascending=False)

    df_mostrar = df_filtrado.copy()
    if "Fecha_dt" in df_mostrar.columns:
        df_mostrar = df_mostrar.drop(columns=["Fecha_dt"])

    if not df_mostrar.empty:
        st.dataframe(df_mostrar, width="stretch", hide_index=True)
    else:
        st.info("No hay transacciones para los filtros seleccionados.")

    st.markdown("---")

    # ==========================================================
    # GESTIÓN DE USUARIOS
    # ==========================================================
    st.markdown("### 👥 Gestión de usuarios")

    if usuarios_df.empty:
        st.info("No hay usuarios registrados todavía.")
        return

    # Vista general de usuarios
    st.markdown("#### Usuarios registrados")
    st.dataframe(usuarios_df, width="stretch", hide_index=True)

    st.markdown("#### Cambiar rol de usuario")

    # Normalizar para edición
    usuarios_roles_df = usuarios_df.copy()
    if "Nombre" not in usuarios_roles_df.columns:
        usuarios_roles_df["Nombre"] = ""

    col_user, col_info = st.columns([1.2, 1.8])

    with col_user:
        username_seleccionado = st.selectbox(
            "Selecciona un usuario",
            usuarios_roles_df["username"].astype(str).tolist()
        )

    fila_usuario = usuarios_roles_df[
        usuarios_roles_df["username"].astype(str) == str(username_seleccionado)
    ]

    rol_actual = "usuario"
    nombre_actual = ""
    if not fila_usuario.empty:
        rol_actual = str(fila_usuario.iloc[0].get("Rol", "usuario"))
        nombre_actual = str(fila_usuario.iloc[0].get("Nombre", ""))

    with col_info:
        st.markdown(
            f"""
            <div style="
                background:#F8FAFC;
                border:1px solid #E2E8F0;
                border-radius:14px;
                padding:16px;
                margin-top:28px;
            ">
                <strong>Usuario:</strong> {username_seleccionado}<br>
                <strong>Nombre:</strong> {nombre_actual or '-'}<br>
                <strong>Rol actual:</strong> {rol_actual}
            </div>
            """,
            unsafe_allow_html=True
        )

    nuevo_rol = st.radio(
        "Nuevo rol",
        options=["usuario", "admin"],
        index=0 if rol_actual == "usuario" else 1,
        horizontal=True
    )

    if st.button("💾 Actualizar rol", type="primary", width="stretch"):
        try:
            actualizar_rol_usuario(username_seleccionado, nuevo_rol)
            st.success(
                f"Rol actualizado correctamente: **{username_seleccionado}** ahora es **{nuevo_rol}**."
            )
            st.rerun()
        except Exception as e:
            st.error(f"No fue posible actualizar el rol del usuario: {e}")