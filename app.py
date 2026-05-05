import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURACIÓN DE IDENTIDAD VISUAL (CSS)
# ==========================================
st.set_page_config(layout="wide", page_title="NPS Executive Dashboard")

st.markdown(f"""
    <style>
    /* Fondo principal y tipografía */
    .stApp {{
        background-color: #FFFFFF;
        color: #111827;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Títulos principales */
    h1, h2, h3 {{
        color: #111827 !important;
        font-weight: 800 !important;
    }}

    /* Tarjetas de KPIs - Alto Contraste y Bordes Redondeados */
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}

    /* VALOR DEL KPI - Azul vibrante */
    div[data-testid="stMetricValue"] {{
        color: #1852FF !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }}
    
    /* ETIQUETA DEL KPI - Gris oscuro, negrita y legible */
    div[data-testid="stMetricLabel"] {{
        color: #374151 !important; 
        font-size: 1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Contenedores de Gráficos */
    .stPlotlyChart {{
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #F9FAFB;
        border-right: 1px solid #E5E7EB;
    }}

    /* Tabs Estilizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: #FFFFFF;
        border-radius: 12px 12px 0px 0px;
        color: #374151 !important;
        font-weight: 600 !important;
        border: 1px solid #E5E7EB;
    }}
    .stTabs [aria-selected="true"] {{
        color: #1852FF !important;
        border-bottom: 3px solid #1852FF !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONFIGURACIÓN DE ENLACES Y DATOS
# ==========================================
RAW_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=0&single=true&output=csv"
BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=1615778287&single=true&output=csv"

@st.cache_data(ttl=600)
def load_and_process_data():
    with st.spinner('⏳ Cargando y auditando datos...'):
        try:
            df_raw = pd.read_csv(RAW_URL)
            
            # Limpieza de porcentajes (RAW -> Float)
            cols_pct = ['Promotores', 'Detractores', 'Neutros', '% DE RESPUESTAS']
            for col in cols_pct:
                if col in df_raw.columns:
                    df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float) / 100

            # Recálculo de conteos reales para NPS Ponderado
            df_raw['promotores_count'] = (df_raw['Promotores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
            df_raw['detractores_count'] = (df_raw['Detractores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
            df_raw['respuestas'] = df_raw['Q DE RESPUESTAS'].astype(int)
            df_raw['asistentes'] = df_raw['ASISTENTES'].astype(int)
            
            # Normalización
            df_raw['speaker_std'] = df_raw['SPEAKER'].str.strip().str.title()
            
            # CORRECCIÓN AQUÍ: Se eliminó el error de escritura 'df_//raw'
            df_raw['session_uid'] = df_raw['LARGADA'].astype(str) + "_" + df_raw['FECHA'].astype(str) + "_" + df_raw['TEMA'].astype(str)
            
            df_raw['fecha'] = pd.to_datetime(df_raw['FECHA'], dayfirst=True, errors='coerce')
            
            # Speaker Score Global
            skill_cols = ['Habilidad de exposición', 'Dominio del tema', 'Interacción con participantes']
            for col in skill_cols:
                if col in df_raw.columns:
                    df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float)
            
            # Evitar error si no existen las columnas de skills
            available_skills = [c for c in skill_cols if c in df_raw.columns]
            if available_skills:
                df_raw['speaker_score_global_pts'] = df_raw[available_skills].mean(axis=1)
            else:
                df_raw['speaker_score_global_pts'] = 0

            # Flags de Calidad
            df_raw['flag_response_gt_100'] = np.where(df_raw['% DE RESPUESTAS'] > 1.0, "REVISAR", "OK")
            df_raw['flag_missing_core'] = np.where(df_raw['Q DE RESPUESTAS'].isna(), "REVISAR", "OK")

            return df_raw
        except Exception as e:
            st.error(f"Error crítico en la carga de datos: {e}")
            return None

df = load_and_process_data()
if df is None: st.stop()

# ==========================================
# 3. FILTROS Y LÓGICA DE NEGOCIO
# ==========================================
st.sidebar.markdown("<h2 style='color: #1852FF;'>🎯 Filtros</h2>", unsafe_allow_html=True)
f_coordinador = st.sidebar.multiselect("Coordinador", options=df['COORDINADOR'].unique())
f_speaker = st.sidebar.multiselect("Speaker", options=df['speaker_std'].unique())
f_cliente = st.sidebar.multiselect("Cliente", options=df['CLIENTE'].unique())
f_modalidad = st.sidebar.multiselect("Modalidad", options=df['MODALIDAD'].unique())

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

# ==========================================
# 4. DISEÑO DE INTERFAZ (UI)
# ==========================================
st.title("🚀 Monitoreo de Experiencia NPS")
st.markdown(f"<p style='color: #374151; font-size: 1.1rem; font-weight: 500;'>Análisis de calidad de talleres y desempeño de speakers</p>", unsafe_allow_html=True)

tabs = st.tabs(["📈 Resumen Ejecutivo", "🎤 Speakers", "🏢 Clientes", "⚙️ Operación", "💬 Insights", "⚠️ Calidad"])

PRIMARY = "#1852FF"
SECONDARY = "#3064F2"
TEXT_DARK = "#111827"
TEXT_MED = "#374151"

# --- VISTA 1: RESUMEN EJECUTIVO ---
with tabs[0]:
    if df_f.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sesiones Válidas", df_f['session_uid'].nunique())
        col2.metric("NPS Ponderado", f"{calculate_nps(df_f):.1f}")
        col3.metric("Tasa de Respuesta", f"{(df_f['respuestas'].sum()/df_f['asistentes'].sum()*100):.1f}%" if df_f['asistentes'].sum()>0 else "0%")
        col4.metric("Score Speaker", f"{df_f['speaker_score_global_pts'].mean():.1f}")

        st.markdown("<br>", unsafe_allow_html=True)
        c_left, c_right = st.columns(2)
        
        if not df_f['fecha'].isna().all():
            # Resample 'ME' para compatibilidad con Pandas 3.0
            df_time = df_f.set_index('fecha').resample('ME').apply(lambda x: calculate_nps(x)).reset_index()
            df_time.columns = ['Fecha', 'NPS']
            df_time['Fecha'] = df_time['Fecha'].dt.strftime('%Y-%m')
            
            fig_time = px.line(df_time, x='Fecha', y='NPS', title="<b>Evolución NPS Ponderado</b>", markers=True)
            fig_time.update_traces(line_color=PRIMARY, line_width=4, marker=dict(size=8, color=SECONDARY))
            fig_time.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                font=dict(color=TEXT_DARK, family="Inter"),
                title_font=dict(color=TEXT_DARK, size=20),
                yaxis=dict(range=[0,100], gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
                xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
            )
            c_left.plotly_chart(fig_time, use_container_width=True)
        
        speaker_nps = df_f.groupby('speaker_std').apply(lambda x: calculate_nps(x)).sort_values(ascending=False).reset_index()
        speaker_nps.columns = ['Speaker', 'NPS']
        
        fig_speak = px.bar(speaker_nps, x='NPS', y='Speaker', orientation='h', title="<b>Ranking NPS por Speaker</b>", 
                           color='NPS', color_continuous_scale=[SECONDARY, PRIMARY])
        fig_speak.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=TEXT_DARK, family="Inter"),
            title_font=dict(color=TEXT_DARK, size=20),
            xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
            yaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
        )
        c_right.plotly_chart(fig_speak, use_container_width=True)

# --- VISTA 2: SPEAKERS ---
with tabs[1]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.subheader("Análisis Detallado de Talento")
        speaker_stats = df_f.groupby('speaker_std').agg({
            'session_uid': 'nunique',
            'respuestas': 'sum',
            'speaker_score_global_pts': 'mean'
        }).reset_index()
        speaker_stats['NPS'] = df_f.groupby('speaker_std').apply(lambda x: calculate_nps(x)).values
        speaker_stats.columns = ['Speaker', 'Sesiones', 'Total Respuestas', 'Score Técnico', 'NPS']
        st.dataframe(speaker_stats.sort_values('NPS', ascending=False), use_container_width=True)
        
        fig_scatter = px.scatter(speaker_stats, x='Score Técnico', y='NPS', size='Sesiones', 
                                 hover_name='Speaker', title="<b>Calidad Técnica vs Satisfacción (NPS)</b>",
                                 color='NPS', color_continuous_scale=[SECONDARY, PRIMARY])
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=TEXT_DARK, family="Inter"),
            title_font=dict(color=TEXT_DARK, size=20),
            xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
            yaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# --- VISTA 3: CLIENTES ---
with tabs[2]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.subheader("Desempeño por Cliente")
        cliente_nps = df_f.groupby('CLIENTE').apply(lambda x: calculate_nps(x)).sort_values(ascending=False).reset_index()
        cliente_nps.columns = ['Cliente', 'NPS']
        fig_cli = px.bar(cliente_nps, x='NPS', y='Cliente', orientation='h', title="<b>NPS por Cliente</b>", 
                         color_discrete_sequence=[PRIMARY])
        fig_cli.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=TEXT_DARK, family="Inter"),
            title_font=dict(color=TEXT_DARK, size=20),
            yaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
            xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
        )
        st.plotly_chart(fig_cli, use_container_width=True)

# --- VISTA 4: OPERACIÓN ---
with tabs[3]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.subheader("Eficiencia de Operaciones")
        col_op1, col_op2 = st.columns(2)
        
        mod_nps = df_f.groupby('MODALIDAD').apply(lambda x: calculate_nps(x)).reset_index()
        mod_nps.columns = ['Modalidad', 'NPS']
        fig_mod = px.bar(mod_nps, x='Modalidad', y='NPS', title="<b>NPS por Modalidad</b>", color_discrete_sequence=[PRIMARY])
        fig_mod.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=TEXT_DARK, family="Inter"),
            title_font=dict(color=TEXT_DARK, size=20),
            xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
            yaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
        )
        col_op1.plotly_chart(fig_mod, use_container_width=True)
        
        mod_resp = df_f.groupby('MODALIDAD').apply(
            lambda x: (x['respuestas'].sum() / x['asistentes'].sum() * 100) if x['asistentes'].sum() > 0 else 0
        ).reset_index()
        mod_resp.columns = ['Modalidad', 'Tasa_Resp']
        fig_resp = px.bar(mod_resp, x='Modalidad', y='Tasa_Resp', title="<b>Tasa de Respuesta por Modalidad</b>", 
                          color_discrete_sequence=[SECONDARY])
        fig_resp.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color=TEXT_DARK, family="Inter"),
            title_font=dict(color=TEXT_DARK, size=20),
            xaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED)), 
            yaxis=dict(gridcolor="#EDEDED", tickfont=dict(color=TEXT_MED))
        )
        col_op2.plotly_chart(fig_resp, use_container_width=True)

# --- VISTA 5: INSIGHTS ---
with tabs[4]:
    if df_f.empty:
        st.warning("No hay datos disponibles.")
    else:
        st.subheader("Análisis de Sentimiento")
        df_f['pos_dinamismo'] = df_f['COMENTARIOS POSITIVOS'].str.contains('dinámico|juegos|interactuar|divertido|dinamica', case=False, na=False).astype(int)
        df_f['pos_claridad'] = df_f['COMENTARIOS POSITIVOS'].str.contains('claro|entendi|explicacion|preciso', case=False, na=False).astype(int)
        total_coment = df_f['COMENTARIOS POSITIVOS'].notna().sum()
        if total_coment > 0:
            c_ins1, c_ins2 = st.columns(2)
            c_ins1.metric("Índice de Dinamismo", f"{(df_f['pos_dinamismo'].sum()/total_coment*100):.1f}%")
            c_ins2.metric("Índice de Claridad", f"{(df_f['pos_claridad'].sum()/total_coment*100):.1f}%")
            st.markdown("---")
            st.write("### 💬 Feedback Reciente")
            st.table(df_f[['speaker_std', 'TEMA', 'COMENTARIOS POSITIVOS']].dropna().tail(15))
        else:
            st.info("No hay comentarios disponibles.")

# --- VISTA 6: CALIDAD ---
with tabs[5]:
    st.subheader("Control de Calidad")
    errores = df_f[(df_f['flag_response_gt_100'] == "REVISAR") | (df_f['flag_missing_core'] == "REVISAR")]
    if not errores.empty:
        st.warning(f"Se han detectado {len(errores)} registros con anomalías.")
        st.dataframe(errores[['session_uid', 'SPEAKER', 'TEMA', 'flag_response_gt_100', 'flag_missing_core']], use_container_width=True)
    else:
        st.success("✅ Todos los datos procesados cumplen con los criterios de calidad.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Dashboard de Monitoreo de Calidad | Identidad Visual v2.0 (High Contrast)</p>", unsafe_allow_html=True)
