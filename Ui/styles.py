import streamlit as st


def load_global_styles():
    st.markdown("""
    <style>
    /* ===== Fondo general ===== */
    .stApp {
        background-color: #f5f7fb;
    }

    /* ===== Contenedor principal ===== */
    /* Quitar espacio superior del contenedor principal */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px;
    }

    /* Quitar espacio extra del header de Streamlit */
    header[data-testid="stHeader"] {
        height: 0rem;
    }

    div[data-testid="stToolbar"] {
        display: none;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* ===== Hero / cabecera ===== */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
        border-radius: 22px;
        padding: 28px 32px;
        color: white;
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.18);
        margin-bottom: 1.2rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        margin-bottom: 1rem;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }

    .badge-pill {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.16);
        color: #fff;
        padding: 7px 14px;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 600;
    }

    /* ===== Tarjetas de sección ===== */
    .section-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.35rem;
    }

    .section-subtitle {
        color: #475569;
        font-size: 0.96rem;
        margin-bottom: 0.8rem;
    }

    /* ===== KPI cards ===== */
    .kpi-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 18px 18px 16px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        min-height: 110px;
    }

    .kpi-label {
        color: #64748b;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .kpi-help {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 8px;
    }

    /* ===== Cajas de estado ===== */
    .status-ok {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 12px 14px;
        border-radius: 14px;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .status-warning {
        background: #fff7ed;
        border: 1px solid #fdba74;
        color: #9a3412;
        padding: 12px 14px;
        border-radius: 14px;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .status-error {
        background: #fef2f2;
        border: 1px solid #fca5a5;
        color: #991b1b;
        padding: 12px 14px;
        border-radius: 14px;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* ===== Step cards ===== */
    .step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #2563eb;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }

    .step-title {
        font-weight: 800;
        color: #0f172a;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }

    .step-desc {
        color: #475569;
        font-size: 0.92rem;
        margin-bottom: 0.2rem;
    }

    /* ===== Botones ===== */
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.72rem 1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
    }

    .stButton > button:hover {
        filter: brightness(1.03);
        transform: translateY(-1px);
    }

    /* ===== Download button ===== */
    .stDownloadButton > button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.72rem 1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        color: white;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.22);
    }

    /* ===== Inputs ===== */
    div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stFileUploader"] section {
        border-radius: 14px !important;
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        font-weight: 700;
        color: #0f172a;
    }

    /* ===== Separadores ===== */
    .soft-divider {
        height: 1px;
        background: linear-gradient(
            90deg,
            rgba(148,163,184,0.15),
            rgba(148,163,184,0.45),
            rgba(148,163,184,0.15)
        );
        margin: 1rem 0 1.2rem 0;
    }
        /* =========================================================
       LOGIN PROFESIONAL
    ========================================================= */
    .login-page-shell {
        min-height: calc(100vh - 80px);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0.5rem 0 2rem 0;
    }

    .login-page-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .login-page-badge {
        display: inline-block;
        background: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .login-page-header h1 {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
        letter-spacing: -0.4px;
    }

    .login-page-header p {
        color: #475569;
        font-size: 1rem;
        max-width: 860px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .login-layout-card {
        background: rgba(255,255,255,0.78);
        border: 1px solid #e2e8f0;
        border-radius: 28px;
        padding: 1.2rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
        backdrop-filter: blur(8px);
    }

    .login-brand-panel {
        background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
        border-radius: 24px;
        padding: 2rem 1.6rem;
        color: white;
        min-height: 620px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.18);
    }

    .login-brand-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .login-brand-subtitle {
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.75;
        margin-bottom: 1.4rem;
    }

    .login-feature-box {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 0.9rem;
    }

    .login-feature-box strong {
        display: block;
        font-size: 0.98rem;
        margin-bottom: 0.35rem;
        color: #ffffff;
    }

    .login-feature-box span {
        display: block;
        color: #dbeafe;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .login-security-note {
        margin-top: 1.2rem;
        background: rgba(15, 23, 42, 0.20);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 16px;
        padding: 1rem;
    }

    .login-security-note strong {
        display: block;
        margin-bottom: 0.35rem;
        color: white;
    }

    .login-security-note span {
        color: #dbeafe;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .login-form-panel {
        margin-bottom: 0.8rem;
    }

    .login-form-header {
        text-align: center;
        padding-top: 0.5rem;
    }

    .login-form-header h2 {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .login-form-header p {
        color: #64748b;
        font-size: 0.96rem;
        margin-bottom: 0;
    }

    .login-form-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        padding: 1.25rem 1.15rem 1rem 1.15rem;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    }

    .login-mini-help {
        margin-top: 0.9rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        color: #475569;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 0.28rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        height: 46px;
        font-weight: 700;
        color: #334155;
    }

    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }

    .stTextInput > div > div > input {
        border-radius: 14px !important;
        min-height: 46px;
        border: 1px solid #dbe4ee !important;
    }

    .stTextInput label {
        font-weight: 600 !important;
        color: #0f172a !important;
    }

    @media (max-width: 992px) {
        .login-brand-panel {
            min-height: auto;
        }

        .login-page-header h1 {
            font-size: 1.7rem;
        }
    }            
    </style>
    """, unsafe_allow_html=True)