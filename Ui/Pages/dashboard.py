import streamlit as st
from Service.auth_service import obtener_usuario_actual
from Service.normative_service import obtener_formatos_soportados

def render_dashboard():
    usuario = obtener_usuario_actual()

    nombre = "Usuario"
    rol = "usuario"

    if usuario:
        nombre = usuario.get("nombre", "Usuario")
        rol = usuario.get("rol", "usuario")

    formatos = obtener_formatos_soportados(2025)
    cantidad_formatos = len(formatos)
    cantidad_modulos = 3

    # =========================
    # HERO / ENCABEZADO
    # =========================
    st.markdown("""
    <div style="
        background: linear-gradient(90deg,#0f62fe,#2563eb);
        padding:30px;
        border-radius:18px;
        color:white;
        margin-bottom:25px;
        box-shadow:0 6px 18px rgba(0,0,0,.12);
    ">
        <h1 style="margin:0;">📊 EXÓGENA DIAN</h1>
        <p style="font-size:18px;margin-top:8px;">
            Sistema de Automatización de Información Exógena
        </p>
        <p style="margin-top:5px;">
            Vigencia Base 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"# ¡Bienvenido, {nombre}! 👋")
    st.write("Selecciona uno de los módulos para comenzar a trabajar.")

    # =========================
    # ESTILOS DE TARJETAS
    # =========================
    st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 24px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
        min-height: 220px;
        margin-bottom: 10px;
    }

    .card-icon {
        font-size: 38px;
        margin-bottom: 8px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 10px;
    }

    .card-text {
        color: #475569;
        line-height: 1.6;
        font-size: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # TARJETAS SUPERIORES
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-icon">🔍</div>
            <div class="card-title">Diagnóstico Preliminar</div>
            <div class="card-text">
                Analiza el archivo Excel para detectar automáticamente los formatos
                DIAN presentes y validar la estructura antes del procesamiento.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "🔍 Abrir Diagnóstico",
            key="dashboard_diag",
            use_container_width=True
        ):
            st.session_state.modulo = "Diagnóstico Preliminar de Formatos"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-icon">📊</div>
            <div class="card-title">Comparar Excel</div>
            <div class="card-text">
                Compara la estructura del archivo Novasoft con el formato oficial
                de la DIAN para identificar diferencias e inconsistencias.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "📊 Abrir Comparador",
            key="dashboard_compare",
            use_container_width=True
        ):
            st.session_state.modulo = "Comparar Excel Dian vs Novasoft"
            st.rerun()

    # =========================
    # TARJETA INFERIOR
    # =========================
    st.write("")

    st.markdown("""
    <div class="card">
        <div class="card-icon">📄</div>
        <div class="card-title">Generar XML</div>
        <div class="card-text">
            Convierte automáticamente los datos del Excel en el XML requerido por
            la DIAN, realizando las validaciones necesarias antes de la generación.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "📄 Generar XML",
        key="dashboard_xml",
        use_container_width=True
    ):
        st.session_state.modulo = "Generar XML para la DIAN"
        st.rerun()

    # =========================
    # MÉTRICAS
    # =========================
    st.write("")
    st.divider()

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Versión", "1.0")

    with m2:
        st.metric("Vigencia", "2025")

    with m3:
        st.metric("Estado", "Operativo ✅")

    st.divider()

    st.caption(
        "Bienvenido a Exógena DIAN. Utiliza el menú lateral o las tarjetas de inicio para acceder a los módulos."
    )

    st.write("")
    st.markdown("## 🧾 Resumen del sistema")

    st.markdown("""
    <style>
    .kpi-card {
        background: #ffffff;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 3px 10px rgba(0,0,0,.06);
        text-align: center;
        min-height: 130px;
    }

    .kpi-icon {
        font-size: 28px;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 6px;
        word-break: break-word;
    }

    .kpi-label {
        font-size: 14px;
        color: #475569;
        font-weight: 500;
    }

    .kpi-sub {
        font-size: 12px;
        color: #64748B;
        margin-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👤</div>
            <div class="kpi-value">{nombre}</div>
            <div class="kpi-label">Usuario activo</div>
            <div class="kpi-sub">Rol: {rol}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📂</div>
            <div class="kpi-value">{cantidad_formatos}</div>
            <div class="kpi-label">Formatos soportados</div>
            <div class="kpi-sub">Vigencia 2025</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧩</div>
            <div class="kpi-value">{cantidad_modulos}</div>
            <div class="kpi-label">Módulos disponibles</div>
            <div class="kpi-sub">Diagnóstico, Comparador y XML</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">📅</div>
            <div class="kpi-value">2025</div>
            <div class="kpi-label">Vigencia base</div>
            <div class="kpi-sub">Configuración normativa activa</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.markdown("## ⚡ Accesos rápidos")
    st.caption("Ingresa directamente al módulo que necesitas utilizar.")

    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button(
            "🔍 Ir a Diagnóstico",
            key="quick_diag",
            use_container_width=True
        ):
            st.session_state.modulo = "Diagnóstico Preliminar de Formatos"
            st.rerun()

    with a2:
        if st.button(
            "📊 Ir a Comparador",
            key="quick_compare",
            use_container_width=True
        ):
            st.session_state.modulo = "Comparar Excel Dian vs Novasoft"
            st.rerun()

    with a3:
        if st.button(
            "📄 Ir a Generar XML",
            key="quick_xml",
            use_container_width=True
        ):
            st.session_state.modulo = "Generar XML para la DIAN"
            st.rerun()
    
    st.write("")
    st.markdown("## 🚀 Flujo recomendado de trabajo")
    st.caption("Sigue este orden para procesar correctamente la información exógena antes de generar el XML final.")

    st.markdown("""
    <style>
    .flow-card {
        background: #ffffff;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,.06);
        min-height: 200px;
        text-align: center;
    }

    .flow-step {
        font-size: 14px;
        font-weight: 700;
        color: #2563EB;
        margin-bottom: 8px;
    }

    .flow-icon {
        font-size: 34px;
        margin-bottom: 10px;
    }

    .flow-title {
        font-size: 20px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 10px;
    }

    .flow-text {
        font-size: 14px;
        color: #475569;
        line-height: 1.5;
    }

    .flow-arrow {
        text-align: center;
        font-size: 32px;
        color: #94A3B8;
        margin-top: 70px;
    }
    </style>
    """, unsafe_allow_html=True)

    f1, flecha1, f2, flecha2, f3 = st.columns([3, 1, 3, 1, 3])

    with f1:
        st.markdown("""
        <div class="flow-card">
            <div class="flow-step">PASO 1</div>
            <div class="flow-icon">🔍</div>
            <div class="flow-title">Diagnóstico</div>
            <div class="flow-text">
                Carga el Excel y detecta los formatos DIAN presentes, validando la
                estructura mínima y el estado preliminar del archivo.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with flecha1:
        st.markdown('<div class="flow-arrow">➡️</div>', unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="flow-card">
            <div class="flow-step">PASO 2</div>
            <div class="flow-icon">📊</div>
            <div class="flow-title">Comparación</div>
            <div class="flow-text">
                Compara la estructura del archivo Novasoft frente a la estructura
                esperada por la DIAN para identificar diferencias o inconsistencias.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with flecha2:
        st.markdown('<div class="flow-arrow">➡️</div>', unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="flow-card">
            <div class="flow-step">PASO 3</div>
            <div class="flow-icon">📄</div>
            <div class="flow-title">Generación XML</div>
            <div class="flow-text">
                Una vez validada la información, genera el XML final con la estructura
                requerida para la presentación ante la DIAN.
            </div>
        </div>
        """, unsafe_allow_html=True)