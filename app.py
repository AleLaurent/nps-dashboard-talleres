import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. CONFIGURACIÓN DE IDENTIDAD VISUAL (CSS ROBUSTO)
# ==========================================
st.set_page_config(layout="wide", page_title="NPS Executive Dashboard", page_icon="📈")

# CSS inyectado para forzar el tema claro y evitar choques de color (texto invisible)
st.markdown("""
    <style>
    /* Forzar fondo claro y texto oscuro en toda la app */
    .stApp {
        background-color: #F8FAFC !important;
    }
    
    /* Asegurar que todos los textos principales sean oscuros */
    p, span, div, h1, h2, h3, h4, h5, h6, label, li {
        color: #0F172A !important;
        font-family: 'Inter', sans-serif;
    }

    /* TARJETAS DE KPIs - Estilo moderno tipo "Glass" o tarjeta limpia */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }

    /* Valor del KPI: Azul vibrante */
    div[data-testid="stMetricValue"] > div {
        color: #2563EB !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    
    /* Etiqueta del KPI: Gris oscuro legible */
    div[data-testid="stMetricLabel"] > div {
        color: #475569 !important; 
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Sidebar - Fondo sutilmente diferente para separar visualmente */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Estilo de los Tabs (Pestañas) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748B !important;
        font-weight: 600 !important;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }
    
    /* Ajuste para alertas / mensajes de error o advertencia */
    .stAlert > div {
        color: inherit !important; /* Permite que el texto del alert tome su color nativo oscuro */
    }
    </style>
    """, unsafe_allow_html=True)

# Paleta de colores para gráficos
PRIMARY = "#2563EB"   # Azul principal
SECONDARY = "#3B82F6" # Azul claro
TEXT_DARK = "#0F172A"
TEXT_MED = "#475569"
BG_WHITE = "#FFFFFF"

# ==========================================
# 2. CONFIGURACIÓN DE DATOS
# ==========================================
RAW_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)
def load_and_process_data():
    try:
        df_raw = pd.read_csv(RAW_URL)
        
        cols_pct = ['Promotores', 'Detractores', 'Neutros', '% DE RESPUESTAS']
        for col in cols_pct:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float) / 100

        df_raw['promotores_count'] = (df_raw['Promotores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
        df_raw['detractores_count'] = (df_raw['Detractores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
        df_raw['respuestas'] = df_raw['Q DE RESPUESTAS'].astype(int)
        df_raw['asistentes'] = df_raw['ASISTENTES'].astype(int)
        df_raw['speaker_std'] = df_raw['SPEAKER'].str.strip().str.title()
        df_raw['session_uid'] = df_raw['LARGADA'].astype(str) + "_" + df_raw['FECHA'].astype(str) + "_" + df_raw['TEMA'].astype(str)
        df_raw['fecha'] = pd.to_datetime(df_raw['FECHA'], dayfirst=True, errors='coerce')
        
        skill_cols = ['Habilidad de exposición', 'Dominio del tema', 'Interacción con participantes']
        for col in skill_cols:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float)
        
        available_skills = [c for c in skill_cols if c in df_raw.columns]
        df_raw['speaker_score_global_pts'] = df_raw[available_skills].mean(axis=1) if available_skills else 0

        df_raw['flag_response_gt_100'] = np.where(df_raw['% DE RESPUESTAS'] > 1.0, "REVISAR", "OK")
        df_raw['flag_missing_core'] = np.where(df_raw['Q DE RESPUESTAS'].isna(), "REVISAR", "OK")

        return df_raw
    except Exception as e:
        st.error(f"Error crítico en la carga de datos: {e}")
        return None

df = load_and_process_data()
if df is None: st.stop()

# ==========================================
# 3. FILTROS Y LÓGICA
# ==========================================
st.sidebar.markdown("<h2 style='color: #2563EB !important;'>🎯 Filtros</h2>", unsafe_allow_html=True)
f_coordinador = st.sidebar.multiselect("Coordinador", options=df['COORDINADOR'].dropna().unique())
f_speaker = st.sidebar.multiselect("Speaker", options=df['speaker_std'].dropna().unique())
f_cliente = st.sidebar.multiselect("Cliente", options=df['CLIENTE'].dropna().unique())
f_modalidad = st.sidebar.multiselect("Modalidad", options=df['MODALIDAD'].dropna().unique())

mask = pd.Series([True] * len(df))
if f_coordinador: mask &= df['COORDINADOR'].isin(f_coordinador)
if f_speaker: mask &= df['speaker_std'].isin(f_speaker)
if f_cliente: mask &= df['CLIENTE'].isin(f_cliente)
if f_modalidad: mask &= df['MODALIDAD'].isin(f_modalidad)
df_f = df[mask].copy()

def calculate_nps(dataframe):
    sum_resp = dataframe['respuestas'].sum()
    sum_prom = dataframe['promotores_count'].sum()
    sum_det = dataframe['detractores_count'].sum()
    return ((sum_prom - sum_det) / sum_resp * 100) if sum_resp > 0 else 0

# Función auxiliar para configurar gráficos estandarizados
def apply_chart_style(fig):
    fig.update_layout(
        plot_bgcolor=BG_WHITE, 
        paper_bgcolor=BG_WHITE, 
        font=dict(color=TEXT_DARK, family="Inter"),
        title_font=dict(color=TEXT_DARK, size=18, family="Inter", weight="bold"),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(gridcolor="#F1F5F9", tickfont=dict(color=TEXT_MED), linecolor="#E2E8F0"), 
        yaxis=dict(gridcolor="#F1F5F9", tickfont=dict(color=TEXT_MED), linecolor="#E2E8F0")
    )
    return fig

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.markdown("<h1 style='margin-bottom: 0px;'>🚀 Monitoreo de Experiencia NPS</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569 !important; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px;'>Análisis de calidad de talleres y desempeño de speakers</p>", unsafe_allow_html=True)

tabs = st.tabs(["📈 Resumen Ejecutivo", "🎤 Speakers", "🏢 Clientes", "⚙️ Operación", "💬 Insights", "⚠️ Calidad"])

with tabs[0]:
    if df_f.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sesiones Válidas", df_f['session_uid'].nunique())
        col2.metric("NPS Ponderado", f"{calculate_nps(df_f):.1f}")
        col3.metric("Tasa de Respuesta", f"{(df_f['respuestas'].sum()/df_f['asistentes'].sum()*100):.1f}%" if df_f['asistentes'].sum()>0 else "0%")
        col4.metric("Score Speaker", f"{df_f['speaker_score_global_pts'].mean():.1f} / 100")

        st.markdown("<br>", unsafe_allow_html=True)
        c_left, c_right = st.columns(2)
        
        # Gráfico: Evolución NPS
        if not df_f['fecha'].isna().all():
            df_time = df_f.set_index('fecha').resample('ME').apply(lambda x: calculate_nps(x)).reset_index()
            df_time.columns = ['Fecha', 'NPS']
            df_time['Fecha'] = df_time['Fecha'].dt.strftime('%Y-%m')
            
            fig_time = px.line(df_time, x='Fecha', y='NPS', title="Evolución NPS Ponderado", markers=True)
            fig_time.update_traces(line_color=PRIMARY, line_width=3, marker=dict(size=8, color=PRIMARY))
            fig_time.update_layout(yaxis=dict(range=[0,100]))
            c_left.plotly_chart(apply_chart_style(fig_time), use_container_width=True)
        
        # Gráfico: Ranking Speakers
        speaker_nps = df_f.groupby('speaker_std').apply(lambda x: calculate_nps(x)).sort_values(ascending=False).reset_index()
        speaker_nps.columns = ['Speaker', 'NPS']
        
        fig_speak = px.bar(speaker_nps.head(10), x='NPS', y='Speaker', orientation='h', title="Top 10 Speakers por NPS")
        fig_speak.update_traces(marker_color=SECONDARY)
        fig_speak.update_layout(yaxis={'categoryorder':'total ascending'})
        c_right.plotly_chart(apply_chart_style(fig_speak), use_container_width=True)

with tabs[1]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.markdown("### Análisis Detallado de Talento")
        speaker_stats = df_f.groupby('speaker_std').agg({
            'session_uid': 'nunique',
            'respuestas': 'sum',
            'speaker_score_global_pts': 'mean'
        }).reset_index()
        speaker_stats['NPS'] = df_f.groupby('speaker_std').apply(lambda x: calculate_nps(x)).values
        speaker_stats.columns = ['Speaker', 'Sesiones', 'Total Respuestas', 'Score Técnico', 'NPS']
        
        # Uso de st.dataframe en lugar de st.table para un renderizado más limpio que no choca con CSS
        st.dataframe(
            speaker_stats.sort_values('NPS', ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score Técnico": st.column_config.NumberColumn(format="%.1f"),
                "NPS": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100)
            }
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        fig_scatter = px.scatter(speaker_stats, x='Score Técnico', y='NPS', size='Sesiones', 
                                 hover_name='Speaker', title="Calidad Técnica vs Satisfacción (NPS)")
        fig_scatter.update_traces(marker=dict(color=PRIMARY, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(apply_chart_style(fig_scatter), use_container_width=True)

with tabs[2]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.markdown("### Desempeño por Cliente")
        cliente_nps = df_f.groupby('CLIENTE').apply(lambda x: calculate_nps(x)).sort_values(ascending=False).reset_index()
        cliente_nps.columns = ['Cliente', 'NPS']
        fig_cli = px.bar(cliente_nps, x='NPS', y='Cliente', orientation='h', title="NPS Promedio por Cliente")
        fig_cli.update_traces(marker_color=PRIMARY)
        fig_cli.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(apply_chart_style(fig_cli), use_container_width=True)

with tabs[3]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.markdown("### Eficiencia de Operaciones")
        col_op1, col_op2 = st.columns(2)
        
        mod_nps = df_f.groupby('MODALIDAD').apply(lambda x: calculate_nps(x)).reset_index()
        mod_nps.columns = ['Modalidad', 'NPS']
        fig_mod = px.bar(mod_nps, x='Modalidad', y='NPS', title="NPS por Modalidad")
        fig_mod.update_traces(marker_color=PRIMARY)
        col_op1.plotly_chart(apply_chart_style(fig_mod), use_container_width=True)
        
        mod_resp = df_f.groupby('MODALIDAD').apply(
            lambda x: (x['respuestas'].sum() / x['asistentes'].sum() * 100) if x['asistentes'].sum() > 0 else 0
        ).reset_index()
        mod_resp.columns = ['Modalidad', 'Tasa_Resp']
        fig_resp = px.bar(mod_resp, x='Modalidad', y='Tasa_Resp', title="Tasa de Respuesta por Modalidad (%)")
        fig_resp.update_traces(marker_color=SECONDARY)
        col_op2.plotly_chart(apply_chart_style(fig_resp), use_container_width=True)

with tabs[4]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.markdown("### Análisis de Sentimiento y Feedback")
        df_f['pos_dinamismo'] = df_f['COMENTARIOS POSITIVOS'].astype(str).str.contains('dinámico|juegos|interactuar|divertido|dinamica', case=False, na=False).astype(int)
        df_f['pos_claridad'] = df_f['COMENTARIOS POSITIVOS'].astype(str).str.contains('claro|entendi|explicacion|preciso', case=False, na=False).astype(int)
        total_coment = df_f['COMENTARIOS POSITIVOS'].notna().sum()
        
        if total_coment > 0:
            c_ins1, c_ins2 = st.columns(2)
            c_ins1.metric("Menciones de Dinamismo", f"{(df_f['pos_dinamismo'].sum()/total_coment*100):.1f}%")
            c_ins2.metric("Menciones de Claridad", f"{(df_f['pos_claridad'].sum()/total_coment*100):.1f}%")
            
            st.markdown("<br><b>Últimos Comentarios Positivos</b>", unsafe_allow_html=True)
            # Reemplazado st.table por st.dataframe
            st.dataframe(
                df_f[['FECHA', 'speaker_std', 'TEMA', 'COMENTARIOS POSITIVOS']].dropna().tail(15), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No hay comentarios disponibles en el periodo seleccionado.")

with tabs[5]:
    st.markdown("### Control de Calidad de Datos")
    errores = df_f[(df_f['flag_response_gt_100'] == "REVISAR") | (df_f['flag_missing_core'] == "REVISAR")]
    if not errores.empty:
        st.error(f"⚠️ Se han detectado {len(errores)} registros con anomalías que requieren revisión.")
        st.dataframe(
            errores[['session_uid', 'SPEAKER', 'TEMA', 'flag_response_gt_100', 'flag_missing_core']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ Todos los datos procesados cumplen con los criterios de calidad. No hay advertencias.")

st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8 !important; font-size: 0.9rem;'>Dashboard de Monitoreo de Calidad | Interfaz Optimizada 4.0</p>", unsafe_allow_html=True)
