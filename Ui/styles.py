import streamlit as st


def load_global_styles():
    st.markdown("""
    <style>
    /* ===== Fondo general ===== */
    .stApp {
        background-color: #f5f7fb;
    }

    /* ===== Contenedor principal ===== */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
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
    </style>
    """, unsafe_allow_html=True)