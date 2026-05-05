import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="NPS Executive Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. PALETA VISUAL Y CSS DE ALTO CONTRASTE
# ============================================================

COLORS = {
    "primary": "#1852FF",
    "primary_dark": "#0B2EA8",
    "primary_soft": "#EEF3FF",
    "accent": "#00A6A6",
    "success": "#12805C",
    "warning": "#B7791F",
    "danger": "#C53030",
    "bg": "#F5F7FB",
    "surface": "#FFFFFF",
    "surface_alt": "#F9FAFB",
    "border": "#D9E2F2",
    "text": "#111827",
    "text_muted": "#4B5563",
    "text_soft": "#6B7280",
    "grid": "#E5E7EB"
}

PRIMARY = COLORS["primary"]
PRIMARY_DARK = COLORS["primary_dark"]
PRIMARY_SOFT = COLORS["primary_soft"]
ACCENT = COLORS["accent"]
SUCCESS = COLORS["success"]
WARNING = COLORS["warning"]
DANGER = COLORS["danger"]
BG = COLORS["bg"]
SURFACE = COLORS["surface"]
SURFACE_ALT = COLORS["surface_alt"]
BORDER = COLORS["border"]
TEXT = COLORS["text"]
TEXT_MUTED = COLORS["text_muted"]
TEXT_SOFT = COLORS["text_soft"]
GRID = COLORS["grid"]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* ========================================================
       BASE GLOBAL: evita texto invisible por contraste pobre
       ======================================================== */

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    .stApp {{
        background: linear-gradient(180deg, {BG} 0%, #FFFFFF 42%, #FFFFFF 100%) !important;
        color: {TEXT} !important;
    }}

    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1500px !important;
    }}

    h1, h2, h3, h4, h5, h6,
    p, span, label, div, small,
    .stMarkdown, .stText, .stCaption {{
        color: {TEXT} !important;
    }}

    a {{
        color: {PRIMARY_DARK} !important;
        font-weight: 700 !important;
    }}

    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {{
        background: {SURFACE} !important;
        border-right: 1px solid {BORDER} !important;
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {PRIMARY_DARK} !important;
    }}

    /* Inputs, multiselects y etiquetas visibles */
    label[data-testid="stWidgetLabel"],
    .stMultiSelect label,
    .stSelectbox label,
    .stDateInput label {{
        color: {TEXT} !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input,
    textarea {{
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border-color: {BORDER} !important;
    }}

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="popover"] span,
    div[data-baseweb="popover"] div {{
        color: {TEXT} !important;
        background-color: transparent !important;
    }}

    div[data-baseweb="tag"] {{
        background-color: {PRIMARY_SOFT} !important;
        border: 1px solid {BORDER} !important;
    }}

    div[data-baseweb="tag"] span {{
        color: {PRIMARY_DARK} !important;
        font-weight: 700 !important;
    }}

    /* ========================================================
       HERO Y TARJETAS
       ======================================================== */

    .hero-card {{
        background: linear-gradient(135deg, #FFFFFF 0%, #F3F6FF 58%, #EAF0FF 100%);
        border: 1px solid {BORDER};
        border-radius: 28px;
        padding: 28px 32px;
        box-shadow: 0 18px 45px rgba(17, 24, 39, 0.08);
        margin-bottom: 22px;
    }}

    .hero-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {PRIMARY_SOFT};
        color: {PRIMARY_DARK} !important;
        border: 1px solid #C7D7FE;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}

    .hero-title {{
        color: {TEXT} !important;
        font-size: clamp(2rem, 4vw, 3.4rem);
        font-weight: 900;
        letter-spacing: -0.06em;
        line-height: 0.98;
        margin: 0;
    }}

    .hero-subtitle {{
        color: {TEXT_MUTED} !important;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.55;
        margin-top: 12px;
        max-width: 850px;
    }}

    .section-title {{
        color: {TEXT} !important;
        font-size: 1.35rem;
        font-weight: 850;
        margin: 8px 0 12px 0;
        letter-spacing: -0.03em;
    }}

    .section-caption {{
        color: {TEXT_MUTED} !important;
        font-size: 0.94rem;
        line-height: 1.45;
        margin-top: -4px;
        margin-bottom: 14px;
    }}

    .metric-card {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 20px 20px 18px 20px;
        box-shadow: 0 12px 32px rgba(17, 24, 39, 0.07);
        min-height: 132px;
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, {PRIMARY}, {ACCENT});
    }}

    .metric-label {{
        color: {TEXT_MUTED} !important;
        font-size: 0.83rem;
        font-weight: 800;
        letter-spacing: 0.025em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}

    .metric-value {{
        color: {TEXT} !important;
        font-size: 2.1rem;
        font-weight: 900;
        letter-spacing: -0.055em;
        line-height: 1;
    }}

    .metric-help {{
        color: {TEXT_SOFT} !important;
        font-size: 0.82rem;
        margin-top: 10px;
        font-weight: 500;
    }}

    .insight-card {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 10px 28px rgba(17, 24, 39, 0.06);
        margin-bottom: 14px;
    }}

    .insight-title {{
        color: {TEXT} !important;
        font-size: 1rem;
        font-weight: 850;
        margin-bottom: 6px;
    }}

    .insight-text {{
        color: {TEXT_MUTED} !important;
        font-size: 0.92rem;
        line-height: 1.48;
        margin: 0;
    }}

    .pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
        margin: 2px 4px 2px 0;
        border: 1px solid {BORDER};
        background: {PRIMARY_SOFT};
        color: {PRIMARY_DARK} !important;
    }}

    .pill-success {{
        background: #ECFDF5;
        color: {SUCCESS} !important;
        border-color: #A7F3D0;
    }}

    .pill-warning {{
        background: #FFFBEB;
        color: {WARNING} !important;
        border-color: #FDE68A;
    }}

    .pill-danger {{
        background: #FEF2F2;
        color: {DANGER} !important;
        border-color: #FECACA;
    }}

    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background: transparent !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 999px !important;
        padding: 10px 16px !important;
        color: {TEXT_MUTED} !important;
        font-weight: 800 !important;
        height: auto !important;
    }}

    .stTabs [data-baseweb="tab"] p {{
        color: {TEXT_MUTED} !important;
        font-weight: 800 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: {PRIMARY} !important;
        border-color: {PRIMARY} !important;
        color: #FFFFFF !important;
    }}

    .stTabs [aria-selected="true"] p {{
        color: #FFFFFF !important;
    }}

    /* ========================================================
       CHARTS Y TABLAS
       ======================================================== */

    .stPlotlyChart {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 22px !important;
        padding: 12px !important;
        box-shadow: 0 10px 28px rgba(17, 24, 39, 0.06);
    }}

    .stDataFrame,
    [data-testid="stTable"] {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 18px !important;
        padding: 8px !important;
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.05);
        overflow: hidden !important;
    }}

    .stDataFrame * ,
    [data-testid="stTable"] * {{
        color: {TEXT} !important;
    }}

    [data-testid="stTable"] table {{
        color: {TEXT} !important;
        background: {SURFACE} !important;
    }}

    [data-testid="stTable"] th {{
        background: {SURFACE_ALT} !important;
        color: {TEXT} !important;
        font-weight: 800 !important;
    }}

    [data-testid="stTable"] td {{
        background: {SURFACE} !important;
        color: {TEXT} !important;
    }}

    /* ========================================================
       ALERTAS NATIVAS
       ======================================================== */

    [data-testid="stAlert"] {{
        border-radius: 18px !important;
        border: 1px solid {BORDER} !important;
    }}

    [data-testid="stAlert"] * {{
        color: {TEXT} !important;
    }}

    /* Oculta elementos decorativos innecesarios */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 3. FUENTES DE DATOS
# ============================================================

RAW_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=0&single=true&output=csv"
BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=1615778287&single=true&output=csv"

# ============================================================
# 4. FUNCIONES UTILITARIAS
# ============================================================

def parse_percentage(series: pd.Series, divide_by_100: bool = True) -> pd.Series:
    """Convierte porcentajes escritos como '80%', '80,5%' o 0.805 a número."""
    cleaned = (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    values = pd.to_numeric(cleaned, errors="coerce")
    return values / 100 if divide_by_100 else values


def safe_int(series: pd.Series) -> pd.Series:
    """Convierte una columna a entero tolerando vacíos o textos."""
    return pd.to_numeric(series, errors="coerce").fillna(0).round().astype(int)


def safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator and denominator != 0 else 0.0


def calculate_nps(dataframe: pd.DataFrame) -> float:
    sum_resp = dataframe["respuestas"].sum()
    sum_prom = dataframe["promotores_count"].sum()
    sum_det = dataframe["detractores_count"].sum()
    return ((sum_prom - sum_det) / sum_resp * 100) if sum_resp > 0 else 0


def nps_label(value: float) -> str:
    if value >= 75:
        return "Excelente"
    if value >= 50:
        return "Sólido"
    if value >= 30:
        return "En observación"
    return "Crítico"


def nps_badge_class(value: float) -> str:
    if value >= 75:
        return "pill pill-success"
    if value >= 50:
        return "pill"
    if value >= 30:
        return "pill pill-warning"
    return "pill pill-danger"


def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def insight_card(title: str, text: str, badge: str | None = None, badge_class: str = "pill") -> None:
    badge_html = f'<span class="{badge_class}">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="insight-card">
            {badge_html}
            <div class="insight-title">{title}</div>
            <p class="insight-text">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def base_fig_layout(fig: go.Figure, title: str | None = None, y_range: list[int] | None = None) -> go.Figure:
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else None,
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 20, "color": TEXT, "family": "Inter"}
        },
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT, "family": "Inter", "size": 13},
        margin={"l": 20, "r": 20, "t": 72, "b": 35},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"color": TEXT}
        },
        coloraxis_showscale=False
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont={"color": TEXT_MUTED},
        title_font={"color": TEXT, "size": 13}
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont={"color": TEXT_MUTED},
        title_font={"color": TEXT, "size": 13}
    )
    if y_range:
        fig.update_yaxes(range=y_range)
    return fig


def empty_state(message: str = "No hay datos disponibles para los filtros seleccionados.") -> None:
    st.warning(message)


def display_dataframe(df_display: pd.DataFrame, height: int | None = None) -> None:
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=height
    )

# ============================================================
# 5. CARGA Y PROCESAMIENTO DE DATOS
# ============================================================

@st.cache_data(ttl=600, show_spinner="Cargando y procesando datos...")
def load_and_process_data() -> pd.DataFrame | None:
    try:
        df_raw = pd.read_csv(RAW_URL)
        df_raw.columns = df_raw.columns.str.strip()

        required_cols = [
            "Promotores", "Detractores", "Neutros", "% DE RESPUESTAS",
            "Q DE RESPUESTAS", "ASISTENTES", "SPEAKER", "LARGADA",
            "FECHA", "TEMA", "COORDINADOR", "CLIENTE", "MODALIDAD"
        ]
        missing = [col for col in required_cols if col not in df_raw.columns]
        if missing:
            st.error(f"Faltan columnas necesarias en la fuente: {', '.join(missing)}")
            return None

        cols_pct = ["Promotores", "Detractores", "Neutros", "% DE RESPUESTAS"]
        for col in cols_pct:
            df_raw[col] = parse_percentage(df_raw[col], divide_by_100=True)

        df_raw["respuestas"] = safe_int(df_raw["Q DE RESPUESTAS"])
        df_raw["asistentes"] = safe_int(df_raw["ASISTENTES"])
        df_raw["promotores_count"] = (df_raw["Promotores"] * df_raw["respuestas"]).round().fillna(0).astype(int)
        df_raw["detractores_count"] = (df_raw["Detractores"] * df_raw["respuestas"]).round().fillna(0).astype(int)

        df_raw["speaker_std"] = df_raw["SPEAKER"].astype(str).str.strip().str.title()
        df_raw["coordinador_std"] = df_raw["COORDINADOR"].astype(str).str.strip().str.title()
        df_raw["cliente_std"] = df_raw["CLIENTE"].astype(str).str.strip()
        df_raw["modalidad_std"] = df_raw["MODALIDAD"].astype(str).str.strip().str.title()

        df_raw["session_uid"] = (
            df_raw["LARGADA"].astype(str).str.strip() + "_" +
            df_raw["FECHA"].astype(str).str.strip() + "_" +
            df_raw["TEMA"].astype(str).str.strip()
        )
        df_raw["fecha"] = pd.to_datetime(df_raw["FECHA"], dayfirst=True, errors="coerce")

        skill_cols = [
            "Habilidad de exposición",
            "Dominio del tema",
            "Interacción con participantes"
        ]
        available_skills = [c for c in skill_cols if c in df_raw.columns]

        for col in available_skills:
            df_raw[col] = parse_percentage(df_raw[col], divide_by_100=False)

        df_raw["speaker_score_global_pts"] = (
            df_raw[available_skills].mean(axis=1) if available_skills else np.nan
        )

        df_raw["tasa_respuesta"] = np.where(
            df_raw["asistentes"] > 0,
            df_raw["respuestas"] / df_raw["asistentes"],
            0
        )

        df_raw["flag_response_gt_100"] = np.where(df_raw["% DE RESPUESTAS"] > 1.0, "REVISAR", "OK")
        df_raw["flag_missing_core"] = np.where(
            df_raw[["Q DE RESPUESTAS", "ASISTENTES", "SPEAKER", "CLIENTE"]].isna().any(axis=1),
            "REVISAR",
            "OK"
        )
        df_raw["flag_invalid_attendance"] = np.where(df_raw["respuestas"] > df_raw["asistentes"], "REVISAR", "OK")

        return df_raw

    except Exception as e:
        st.error(f"Error crítico en la carga de datos: {e}")
        return None


df = load_and_process_data()
if df is None:
    st.stop()

# ============================================================
# 6. SIDEBAR / FILTROS
# ============================================================

st.sidebar.markdown(
    f"""
    <div style="padding: 8px 2px 18px 2px;">
        <h2 style="margin-bottom: 4px; color: {PRIMARY_DARK} !important;">🎯 Filtros</h2>
        <p style="margin: 0; color: {TEXT_MUTED} !important; font-size: 0.9rem; line-height: 1.4;">
            Segmenta la información para revisar experiencia, operación y desempeño de speakers.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

f_coordinador = st.sidebar.multiselect(
    "Coordinador",
    options=sorted(df["coordinador_std"].dropna().unique())
)
f_speaker = st.sidebar.multiselect(
    "Speaker",
    options=sorted(df["speaker_std"].dropna().unique())
)
f_cliente = st.sidebar.multiselect(
    "Cliente",
    options=sorted(df["cliente_std"].dropna().unique())
)
f_modalidad = st.sidebar.multiselect(
    "Modalidad",
    options=sorted(df["modalidad_std"].dropna().unique())
)

valid_dates = df["fecha"].dropna()
if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    selected_dates = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_dates = None

mask = pd.Series(True, index=df.index)
if f_coordinador:
    mask &= df["coordinador_std"].isin(f_coordinador)
if f_speaker:
    mask &= df["speaker_std"].isin(f_speaker)
if f_cliente:
    mask &= df["cliente_std"].isin(f_cliente)
if f_modalidad:
    mask &= df["modalidad_std"].isin(f_modalidad)
if selected_dates and isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    mask &= df["fecha"].dt.date.between(start_date, end_date)

df_f = df[mask].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div class="insight-card" style="box-shadow:none; margin-top: 6px;">
        <div class="insight-title">Datos filtrados</div>
        <p class="insight-text">
            <b>{len(df_f):,}</b> registros visibles de <b>{len(df):,}</b> registros totales.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 7. HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-eyebrow">Dashboard ejecutivo · NPS & experiencia</div>
        <h1 class="hero-title">Monitoreo de Experiencia NPS</h1>
        <p class="hero-subtitle">
            Análisis de calidad de talleres, satisfacción de participantes, desempeño de speakers,
            respuesta operativa y alertas de calidad de datos.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 8. TABS
# ============================================================

tabs = st.tabs([
    "📈 Resumen Ejecutivo",
    "🎤 Speakers",
    "🏢 Clientes",
    "⚙️ Operación",
    "💬 Insights",
    "⚠️ Calidad"
])

# ============================================================
# 9. RESUMEN EJECUTIVO
# ============================================================

with tabs[0]:
    if df_f.empty:
        empty_state()
    else:
        nps_global = calculate_nps(df_f)
        tasa_respuesta_global = safe_divide(df_f["respuestas"].sum(), df_f["asistentes"].sum()) * 100
        score_global = df_f["speaker_score_global_pts"].mean()
        sesiones_validas = df_f["session_uid"].nunique()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            metric_card("Sesiones válidas", f"{sesiones_validas:,}", "Sesiones únicas consideradas")
        with k2:
            metric_card("NPS ponderado", f"{nps_global:.1f}", f"Estado: {nps_label(nps_global)}")
        with k3:
            metric_card("Tasa de respuesta", f"{tasa_respuesta_global:.1f}%", "Respuestas sobre asistentes")
        with k4:
            metric_card("Score speaker", f"{score_global:.1f}" if not np.isnan(score_global) else "S/D", "Promedio de atributos técnicos")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div>
                <span class="{nps_badge_class(nps_global)}">NPS global: {nps_label(nps_global)}</span>
                <span class="pill">{df_f['respuestas'].sum():,} respuestas</span>
                <span class="pill">{df_f['asistentes'].sum():,} asistentes</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        c_left, c_right = st.columns([1.15, 0.85])

        with c_left:
            if not df_f["fecha"].isna().all():
                df_time = (
                    df_f.dropna(subset=["fecha"])
                    .set_index("fecha")
                    .resample("ME")
                    .apply(calculate_nps)
                    .reset_index()
                )
                df_time.columns = ["Fecha", "NPS"]
                df_time["Mes"] = df_time["Fecha"].dt.strftime("%Y-%m")

                fig_time = px.line(
                    df_time,
                    x="Mes",
                    y="NPS",
                    markers=True,
                    text=df_time["NPS"].round(1)
                )
                fig_time.update_traces(
                    line_color=PRIMARY,
                    line_width=4,
                    marker={"size": 10, "color": ACCENT, "line": {"color": "#FFFFFF", "width": 2}},
                    textposition="top center",
                    textfont={"color": TEXT, "size": 12, "family": "Inter"}
                )
                fig_time.add_hline(
                    y=50,
                    line_dash="dash",
                    line_color="#A3AAB8",
                    annotation_text="Referencia 50",
                    annotation_font_color=TEXT_MUTED
                )
                fig_time = base_fig_layout(fig_time, "Evolución mensual del NPS ponderado", [0, 100])
                c_left.plotly_chart(fig_time, use_container_width=True)
            else:
                empty_state("No hay fechas válidas para construir la evolución mensual.")

        with c_right:
            speaker_nps = (
                df_f.groupby("speaker_std")
                .apply(calculate_nps, include_groups=False)
                .sort_values(ascending=True)
                .reset_index(name="NPS")
            )
            speaker_nps = speaker_nps.tail(12)

            fig_speaker = px.bar(
                speaker_nps,
                x="NPS",
                y="speaker_std",
                orientation="h",
                text=speaker_nps["NPS"].round(1),
                color="NPS",
                color_continuous_scale=["#DCE7FF", PRIMARY]
            )
            fig_speaker.update_traces(
                textposition="outside",
                textfont={"color": TEXT, "size": 12, "family": "Inter"},
                marker_line_color="#FFFFFF",
                marker_line_width=1.2,
                cliponaxis=False
            )
            fig_speaker = base_fig_layout(fig_speaker, "Top speakers por NPS", [0, 100])
            fig_speaker.update_yaxes(title="Speaker")
            fig_speaker.update_xaxes(title="NPS")
            c_right.plotly_chart(fig_speaker, use_container_width=True)

# ============================================================
# 10. SPEAKERS
# ============================================================

with tabs[1]:
    if df_f.empty:
        empty_state()
    else:
        st.markdown('<div class="section-title">Análisis detallado de talento</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Cruza satisfacción percibida, score técnico y volumen de sesiones para identificar referentes y oportunidades de mejora.</div>',
            unsafe_allow_html=True
        )

        speaker_stats = (
            df_f.groupby("speaker_std")
            .agg(
                Sesiones=("session_uid", "nunique"),
                Total_Respuestas=("respuestas", "sum"),
                Total_Asistentes=("asistentes", "sum"),
                Score_Tecnico=("speaker_score_global_pts", "mean")
            )
            .reset_index()
            .rename(columns={"speaker_std": "Speaker"})
        )

        nps_by_speaker = (
            df_f.groupby("speaker_std")
            .apply(calculate_nps, include_groups=False)
            .reset_index(name="NPS")
            .rename(columns={"speaker_std": "Speaker"})
        )

        speaker_stats = speaker_stats.merge(nps_by_speaker, on="Speaker", how="left")
        speaker_stats["Tasa_Respuesta"] = (
            speaker_stats["Total_Respuestas"] / speaker_stats["Total_Asistentes"].replace(0, np.nan) * 100
        ).fillna(0)

        speaker_stats_display = speaker_stats.copy()
        speaker_stats_display["Score_Tecnico"] = speaker_stats_display["Score_Tecnico"].round(1)
        speaker_stats_display["NPS"] = speaker_stats_display["NPS"].round(1)
        speaker_stats_display["Tasa_Respuesta"] = speaker_stats_display["Tasa_Respuesta"].round(1).astype(str) + "%"
        speaker_stats_display = speaker_stats_display.sort_values("NPS", ascending=False)

        display_dataframe(speaker_stats_display, height=420)

        fig_scatter = px.scatter(
            speaker_stats,
            x="Score_Tecnico",
            y="NPS",
            size="Sesiones",
            hover_name="Speaker",
            hover_data={
                "Total_Respuestas": True,
                "Tasa_Respuesta": ":.1f",
                "Score_Tecnico": ":.1f",
                "NPS": ":.1f"
            },
            color="NPS",
            color_continuous_scale=["#FECACA", "#FDE68A", "#A7F3D0", PRIMARY]
        )
        fig_scatter.update_traces(
            marker={"line": {"color": "#FFFFFF", "width": 1.5}, "opacity": 0.9}
        )
        fig_scatter.add_hline(y=50, line_dash="dash", line_color="#A3AAB8")
        fig_scatter = base_fig_layout(fig_scatter, "Calidad técnica vs satisfacción NPS", [0, 100])
        fig_scatter.update_xaxes(title="Score técnico")
        fig_scatter.update_yaxes(title="NPS")
        st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================
# 11. CLIENTES
# ============================================================

with tabs[2]:
    if df_f.empty:
        empty_state()
    else:
        st.markdown('<div class="section-title">Desempeño por cliente</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Identifica clientes con alta satisfacción y cuentas que podrían requerir seguimiento.</div>',
            unsafe_allow_html=True
        )

        cliente_stats = (
            df_f.groupby("cliente_std")
            .agg(
                Sesiones=("session_uid", "nunique"),
                Respuestas=("respuestas", "sum"),
                Asistentes=("asistentes", "sum")
            )
            .reset_index()
            .rename(columns={"cliente_std": "Cliente"})
        )
        cliente_nps = (
            df_f.groupby("cliente_std")
            .apply(calculate_nps, include_groups=False)
            .reset_index(name="NPS")
            .rename(columns={"cliente_std": "Cliente"})
        )
        cliente_stats = cliente_stats.merge(cliente_nps, on="Cliente", how="left")
        cliente_stats["Tasa_Respuesta"] = (
            cliente_stats["Respuestas"] / cliente_stats["Asistentes"].replace(0, np.nan) * 100
        ).fillna(0)
        cliente_stats = cliente_stats.sort_values("NPS", ascending=True)

        fig_clientes = px.bar(
            cliente_stats.tail(18),
            x="NPS",
            y="Cliente",
            orientation="h",
            text=cliente_stats.tail(18)["NPS"].round(1),
            color="NPS",
            color_continuous_scale=["#FECACA", "#FDE68A", "#A7F3D0", PRIMARY]
        )
        fig_clientes.update_traces(
            textposition="outside",
            textfont={"color": TEXT, "size": 12},
            marker_line_color="#FFFFFF",
            marker_line_width=1.2,
            cliponaxis=False
        )
        fig_clientes = base_fig_layout(fig_clientes, "NPS por cliente", [0, 100])
        fig_clientes.update_xaxes(title="NPS")
        fig_clientes.update_yaxes(title="Cliente")
        st.plotly_chart(fig_clientes, use_container_width=True)

        cliente_display = cliente_stats.sort_values("NPS", ascending=False).copy()
        cliente_display["NPS"] = cliente_display["NPS"].round(1)
        cliente_display["Tasa_Respuesta"] = cliente_display["Tasa_Respuesta"].round(1).astype(str) + "%"
        display_dataframe(cliente_display, height=360)

# ============================================================
# 12. OPERACIÓN
# ============================================================

with tabs[3]:
    if df_f.empty:
        empty_state()
    else:
        st.markdown('<div class="section-title">Eficiencia de operaciones</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Compara modalidad, tasa de respuesta y consistencia operativa de los talleres.</div>',
            unsafe_allow_html=True
        )

        col_op1, col_op2 = st.columns(2)

        mod_nps = (
            df_f.groupby("modalidad_std")
            .apply(calculate_nps, include_groups=False)
            .reset_index(name="NPS")
            .rename(columns={"modalidad_std": "Modalidad"})
        )

        fig_mod = px.bar(
            mod_nps,
            x="Modalidad",
            y="NPS",
            text=mod_nps["NPS"].round(1),
            color="NPS",
            color_continuous_scale=["#FECACA", "#FDE68A", "#A7F3D0", PRIMARY]
        )
        fig_mod.update_traces(
            textposition="outside",
            textfont={"color": TEXT, "size": 12},
            marker_line_color="#FFFFFF",
            marker_line_width=1.2,
            cliponaxis=False
        )
        fig_mod = base_fig_layout(fig_mod, "NPS por modalidad", [0, 100])
        fig_mod.update_xaxes(title="Modalidad")
        fig_mod.update_yaxes(title="NPS")
        col_op1.plotly_chart(fig_mod, use_container_width=True)

        mod_resp = (
            df_f.groupby("modalidad_std")
            .agg(Respuestas=("respuestas", "sum"), Asistentes=("asistentes", "sum"))
            .reset_index()
            .rename(columns={"modalidad_std": "Modalidad"})
        )
        mod_resp["Tasa_Resp"] = (
            mod_resp["Respuestas"] / mod_resp["Asistentes"].replace(0, np.nan) * 100
        ).fillna(0)

        fig_resp = px.bar(
            mod_resp,
            x="Modalidad",
            y="Tasa_Resp",
            text=mod_resp["Tasa_Resp"].round(1).astype(str) + "%",
            color_discrete_sequence=[ACCENT]
        )
        fig_resp.update_traces(
            textposition="outside",
            textfont={"color": TEXT, "size": 12},
            marker_line_color="#FFFFFF",
            marker_line_width=1.2,
            cliponaxis=False
        )
        fig_resp = base_fig_layout(fig_resp, "Tasa de respuesta por modalidad", [0, 100])
        fig_resp.update_xaxes(title="Modalidad")
        fig_resp.update_yaxes(title="Tasa de respuesta (%)")
        col_op2.plotly_chart(fig_resp, use_container_width=True)

        coordinador_stats = (
            df_f.groupby("coordinador_std")
            .agg(
                Sesiones=("session_uid", "nunique"),
                Respuestas=("respuestas", "sum"),
                Asistentes=("asistentes", "sum")
            )
            .reset_index()
            .rename(columns={"coordinador_std": "Coordinador"})
        )
        coordinador_nps = (
            df_f.groupby("coordinador_std")
            .apply(calculate_nps, include_groups=False)
            .reset_index(name="NPS")
            .rename(columns={"coordinador_std": "Coordinador"})
        )
        coordinador_stats = coordinador_stats.merge(coordinador_nps, on="Coordinador", how="left")
        coordinador_stats["Tasa_Respuesta"] = (
            coordinador_stats["Respuestas"] / coordinador_stats["Asistentes"].replace(0, np.nan) * 100
        ).fillna(0)

        coord_display = coordinador_stats.sort_values("NPS", ascending=False).copy()
        coord_display["NPS"] = coord_display["NPS"].round(1)
        coord_display["Tasa_Respuesta"] = coord_display["Tasa_Respuesta"].round(1).astype(str) + "%"

        st.markdown('<div class="section-title">Resumen por coordinador</div>', unsafe_allow_html=True)
        display_dataframe(coord_display, height=320)

# ============================================================
# 13. INSIGHTS
# ============================================================

with tabs[4]:
    if df_f.empty:
        empty_state()
    else:
        st.markdown('<div class="section-title">Análisis de sentimiento</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Lectura rápida de patrones en comentarios positivos para detectar atributos valorados por los participantes.</div>',
            unsafe_allow_html=True
        )

        positive_col = "COMENTARIOS POSITIVOS"
        if positive_col not in df_f.columns:
            st.info("No existe la columna de comentarios positivos en la fuente.")
        else:
            comments = df_f[positive_col].fillna("").astype(str)
            total_comments = comments.str.strip().ne("").sum()

            df_f["pos_dinamismo"] = comments.str.contains(
                "dinámico|dinamico|juegos|interactuar|interactivo|divertido|dinámica|dinamica|participativo",
                case=False,
                na=False,
                regex=True
            ).astype(int)
            df_f["pos_claridad"] = comments.str.contains(
                "claro|clara|entendí|entendi|explicación|explicacion|preciso|precisa|didáctico|didactico",
                case=False,
                na=False,
                regex=True
            ).astype(int)
            df_f["pos_aplicabilidad"] = comments.str.contains(
                "aplicable|práctico|practico|herramienta|útil|util|casos|ejemplo|ejemplos",
                case=False,
                na=False,
                regex=True
            ).astype(int)

            if total_comments > 0:
                din = df_f["pos_dinamismo"].sum() / total_comments * 100
                cla = df_f["pos_claridad"].sum() / total_comments * 100
                apl = df_f["pos_aplicabilidad"].sum() / total_comments * 100

                i1, i2, i3 = st.columns(3)
                with i1:
                    metric_card("Índice de dinamismo", f"{din:.1f}%", "Comentarios con señales de interacción")
                with i2:
                    metric_card("Índice de claridad", f"{cla:.1f}%", "Comentarios con señales de explicación clara")
                with i3:
                    metric_card("Índice de aplicabilidad", f"{apl:.1f}%", "Comentarios con señales de utilidad práctica")

                st.markdown("<br>", unsafe_allow_html=True)

                top_theme = max(
                    [("Dinamismo", din), ("Claridad", cla), ("Aplicabilidad", apl)],
                    key=lambda x: x[1]
                )
                insight_card(
                    "Principal fortaleza percibida",
                    f"El patrón más mencionado es {top_theme[0].lower()}, con una presencia aproximada de {top_theme[1]:.1f}% dentro de los comentarios positivos.",
                    badge="Insight automático",
                    badge_class="pill pill-success"
                )

                feedback_cols = ["speaker_std", "TEMA", positive_col]
                feedback = (
                    df_f[feedback_cols]
                    .dropna(subset=[positive_col])
                    .tail(15)
                    .rename(columns={
                        "speaker_std": "Speaker",
                        "TEMA": "Tema",
                        positive_col: "Comentario positivo"
                    })
                )

                st.markdown('<div class="section-title">Feedback reciente</div>', unsafe_allow_html=True)
                display_dataframe(feedback, height=420)
            else:
                st.info("No hay comentarios positivos disponibles para los filtros seleccionados.")

# ============================================================
# 14. CALIDAD DE DATOS
# ============================================================

with tabs[5]:
    st.markdown('<div class="section-title">Control de calidad</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Revisa registros con posibles inconsistencias antes de tomar decisiones ejecutivas.</div>',
        unsafe_allow_html=True
    )

    if df_f.empty:
        empty_state()
    else:
        errores = df_f[
            (df_f["flag_response_gt_100"] == "REVISAR") |
            (df_f["flag_missing_core"] == "REVISAR") |
            (df_f["flag_invalid_attendance"] == "REVISAR")
        ].copy()

        total_errores = len(errores)
        total_registros = len(df_f)
        calidad = (1 - safe_divide(total_errores, total_registros)) * 100

        q1, q2, q3 = st.columns(3)
        with q1:
            metric_card("Registros revisados", f"{total_registros:,}", "Según filtros aplicados")
        with q2:
            metric_card("Alertas detectadas", f"{total_errores:,}", "Registros que requieren revisión")
        with q3:
            metric_card("Índice de calidad", f"{calidad:.1f}%", "Registros sin alertas críticas")

        st.markdown("<br>", unsafe_allow_html=True)

        if not errores.empty:
            st.warning(f"Se han detectado {total_errores} registros con anomalías.")
            errores_display = errores[[
                "session_uid",
                "SPEAKER",
                "TEMA",
                "% DE RESPUESTAS",
                "respuestas",
                "asistentes",
                "flag_response_gt_100",
                "flag_missing_core",
                "flag_invalid_attendance"
            ]].rename(columns={
                "session_uid": "Sesión",
                "SPEAKER": "Speaker",
                "TEMA": "Tema",
                "% DE RESPUESTAS": "% Respuestas",
                "respuestas": "Respuestas",
                "asistentes": "Asistentes",
                "flag_response_gt_100": "Respuesta > 100%",
                "flag_missing_core": "Dato central faltante",
                "flag_invalid_attendance": "Respuestas > asistentes"
            })
            errores_display["% Respuestas"] = (errores_display["% Respuestas"] * 100).round(1).astype(str) + "%"
            display_dataframe(errores_display, height=420)
        else:
            st.success("✅ Todos los datos procesados cumplen con los criterios de calidad definidos.")

# ============================================================
# 15. FOOTER
# ============================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center; color:{TEXT_SOFT} !important; font-size:0.86rem; padding: 18px 0;">
        Dashboard de Monitoreo de Calidad · Identidad Visual v4.0 · Alto contraste y legibilidad reforzada
    </div>
    """,
    unsafe_allow_html=True
)

