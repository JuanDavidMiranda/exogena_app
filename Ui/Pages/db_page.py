import streamlit as st

from Service.transacciones_service import listar_usuarios


def render_db_page():
    st.markdown("## 🔎 Usuarios en la base de datos SQLite")
    st.caption("Consulta en vivo de la tabla `usuarios` desde la base de datos utilizada por la aplicación.")

    try:
        usuarios_df = listar_usuarios()

        st.markdown("### Resultados")
        if usuarios_df.empty:
            st.info("No hay usuarios registrados en la base de datos.")
        else:
            st.dataframe(usuarios_df, use_container_width=True)

        st.markdown(
            "---\n"
            "Este listado se obtiene directamente de la base de datos SQLite `data/app.db`."
        )
    except Exception as e:
        st.error(f"No se pudo cargar la tabla de usuarios: {e}")
