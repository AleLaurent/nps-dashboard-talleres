import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN Y ESTILO
# ==========================================
st.set_page_config(layout="wide", page_title="NPS Executive Dashboard | Monitoreo de Talleres")

# Estilo CSS para un look ejecutivo y limpio
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    div[data-testid="stMetricValue"] { color: #1E3A8A; font-weight: bold; }
    .stPlotlyChart { background-color: #ffffff; border-radius: 15px; padding: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# CONFIGURACIÓN DE ENLACES (TUS LINKS REALES)
# ==========================================
RAW_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=0&single=true&output=csv"
BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFwGrETct25PZMCnJ6nsSGbSKmoJofkQ3q94hUjfV7QivAckahllA_ld4DQlmxYwnvOZp9bmUTXNDq/pub?gid=1615778287&single=true&output=csv"

# ==========================================
# CAPA DE PROCESAMIENTO DE DATOS (ETL)
# ==========================================
@st.cache_data(ttl=600)
def load_and_process_data():
    # Carga de datos
    df_raw = pd.read_csv(RAW_URL)
    df_base = pd.read_csv(BASE_URL)

    # --- 1. AUDITORÍA Y LIMPIEZA DEL RAW ---
    # Convertir porcentajes de texto ("20.00%") a float (0.20)
    cols_pct = ['Promotores', 'Detractores', 'Neutros', '% DE RESPUESTAS']
    for col in cols_pct:
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float) / 100

    # --- 2. RECALCULO DE CONTEOS REALES (Sugerencia de Verdad) ---
    # No confiamos en la base_dashboard para los conteos, los calculamos del RAW
    df_raw['promotores_count'] = (df_raw['Promotores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
    df_raw['detractores_count'] = (df_raw['Detractores'] * df_raw['Q DE RESPUESTAS']).round().astype(int)
    df_raw['respuestas'] = df_raw['Q DE RESPUESTAS'].astype(int)
    df_raw['asistentes'] = df_raw['ASISTENTES'].astype(int)
    
    # --- 3. NORMALIZACIÓN Y CAMPOS CANÓNICOS ---
    df_raw['speaker_std'] = df_raw['SPEAKER'].str.strip().str.title()
    df_raw['session_uid'] = df_raw['LARGADA'].astype(str) + "_" + df_raw['FECHA'] + "_" + df_raw['TEMA']
    df_raw['fecha'] = pd.to_datetime(df_raw['FECHA'], dayfirst=True, errors='coerce')
    
    # Cálculo de Speaker Score (Promedio de las 3 dimensiones)
    # Convertimos los % de habilidades a escala 0-100
    skill_cols = ['Habilidad de exposición', 'Dominio del tema', 'Interacción con participantes']
    for col in skill_cols:
        df_raw[col] = df_raw[col].astype(str).str.replace('%', '').astype(float)
    
    df_raw['speaker_score_global_pts'] = df_raw[skill_cols].mean(axis=1)

    # --- 4. FLAGS DE CALIDAD ---
    df_raw['flag_response_gt_100'] = np.where(df_raw['% DE RESPUESTAS'] > 1.0, "REVISAR", "OK")
    df_raw['flag_missing_core'] = np.where(df_raw['Q DE RESPUESTAS'].isna(), "REVISAR", "OK")

    return df_raw

# Cargar datos
try:
    df = load_and_process_data()
except Exception as e:
    st.error(f"Error crítico cargando los datos: {e}")
    st.stop()

# ==========================================
# FILTROS GLOBALES (SIDEBAR)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3589/3589030.png", width=80)
st.sidebar.title("Filtros Ejecutivos")

f_coordinador = st.sidebar.multiselect("Coordinador", options=df['COORDINADOR'].unique())
f_speaker = st.sidebar.multiselect("Speaker", options=df['speaker_std'].unique())
f_cliente = st.sidebar.multiselect("Cliente", options=df['CLIENTE'].unique())
f_modalidad = st.sidebar.multiselect("Modalidad", options=df['MODALIDAD'].unique())
f_tema = st.sidebar.multiselect("Tema", options=df['TEMA'].unique())

# Máscara de filtrado
mask = pd.Series([True] * len(df))
if f_coordinador: mask &= df['COORDINADOR'].isin(f_coordinador)
if f_speaker: mask &= df['speaker_std'].isin(f_speaker)
if f_cliente: mask &= df['CLIENTE'].isin(f_cliente)
if f_modalidad: mask &= df['MODALIDAD'].isin(f_modalidad)
if f_tema: mask &= df['TEMA'].isin(f_tema)

df_f = df[mask]

# ==========================================
# CÁLCULOS MAESTROS (Lógica Ponderada Estricta)
# ==========================================
sum_resp = df_f['respuestas'].sum()
sum_asist = df_f['asistentes'].sum()
sum_prom = df_f['promotores_count'].sum()
sum_det = df_f['detractores_count'].sum()

# KPIs Finales
nps_ponderado = ((sum_prom - sum_det) / sum_resp * 100) if sum_resp > 0 else 0
tasa_respuesta = (sum_resp / sum_asist * 100) if sum_asist > 0 else 0
sesiones_validas = df_f['session_uid'].nunique()
score_speaker_avg = df_f['speaker_score_global_pts'].mean()

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("🚀 Dashboard de Calidad NPS")
st.markdown(f"**Actualizado automáticamente desde Google Sheets** | Datos filtrados: {len(df_f)} sesiones")

tabs = st.tabs(["📈 Resumen Ejecutivo", "🎤 Speakers", "🏢 Clientes", "⚙️ Operación", "💬 Insights", "⚠️ Calidad"])

# --- VISTA 1: RESUMEN EJECUTIVO ---
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesiones Válidas", sesiones_validas)
    col2.metric("NPS Ponderado", f"{nps_ponderado:.1f}")
    col3.metric("Tasa de Respuesta", f"{tasa_respuesta:.1f}%")
    col4.metric("Score Promedio Speaker", f"{score_speaker_avg:.1f}/100")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    
    # Evolución Temporal
    df_time = df_f.set_index('fecha').resample('M').apply(
        lambda x: ((x['promotores_count'].sum() - x['detractores_count'].sum()) / x['respuestas'].sum() * 100) if x['respuestas'].sum() > 0 else 0
    ).reset_index()
    df_time.columns = ['Fecha', 'NPS']
    df_time['Fecha'] = df_time['Fecha'].dt.strftime('%Y-%m')
    
    fig_time = px.line(df_time, x='Fecha', y='NPS', title="Tendencia de NPS Ponderado", markers=True,
                       line_shape="linear", render_mode="svg")
    fig_time.update_traces(line_color='#1E3A8A', line_width=3)
    fig_time.update_layout(yaxis_range=[0, 100])
    c_left.plotly_chart(fig_time, use_container_width=True)
    
    # Ranking Speakers
    speaker_nps = df_f.groupby('speaker_std').apply(
        lambda x: ((x['promotores_count'].sum() - x['detractores_count'].sum()) / x['respuestas'].sum() * 100) if x['respuestas'].sum() > 0 else 0
    ).sort_values(ascending=False).reset_index()
    speaker_nps.columns = ['Speaker', 'NPS']
    
    fig_speak = px.bar(speaker_nps, x='NPS', y='Speaker', orientation='h', 
                       title="Ranking NPS por Speaker", color='NPS', color_continuous_scale='Blues')
    fig_speak.update_layout(yaxis={'categoryorder':'total ascending'})
    c_right.plotly_chart(fig_speak, use_container_width=True)

# --- VISTA 2: SPEAKERS ---
with tabs[1]:
    st.subheader("Análisis Detallado de Talento")
    # Tabla de métricas por speaker
    speaker_stats = df_f.groupby('speaker_std').agg({
        'session_uid': 'nunique',
        'respuestas': 'sum',
        'speaker_score_global_pts': 'mean'
    }).reset_index()
    
    # Calcular NPS individual
    speaker_stats['NPS'] = df_f.groupby('speaker_std').apply(
        lambda x: ((x['promotores_count'].sum() - x['detractores_count'].sum()) / x['respuestas'].sum() * 100) if x['respuestas'].sum() > 0 else 0
    ).values
    
    speaker_stats.columns = ['Speaker', 'Sesiones', 'Total Respuestas', 'Score Técnico', 'NPS']
    st.dataframe(speaker_stats.sort_values('NPS', ascending=False), use_container_width=True)
    
    # Scatter Plot: Técnica vs Satisfacción
    fig_scatter = px.scatter(speaker_stats, x='Score Técnico', y='NPS', size='Sesiones', 
                             hover_name='Speaker', title="Relación: Calidad Técnica vs NPS",
                             color='NPS', color_continuous_scale='Viridis')
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- VISTA 3: CLIENTES ---
with tabs[2]:
    st.subheader("Desempeño por Cliente / Proyecto")
    cliente_nps = df_f.groupby('CLIENTE').apply(
        lambda x: ((x['promotores_count'].sum() - x['detractores_count'].sum()) / x['respuestas'].sum() * 100) if x['respuestas'].sum() > 0 else 0
    ).sort_values(ascending=False).reset_index()
    cliente_nps.columns = ['Cliente', 'NPS']
    
    fig_cli = px.bar(cliente_nps, x='NPS', y='Cliente', orientation='h', title="NPS por Cliente", color_discrete_sequence=['#1E3A8A'])
    fig_cli.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cli, use_container_width=True)

# --- VISTA 4: OPERACIÓN ---
with tabs[3]:
    st.subheader("Eficiencia Operativa")
    col_op1, col_op2 = st.columns(2)
    
    # NPS por Modalidad
    mod_nps = df_f.groupby('MODALIDAD').apply(
        lambda x: ((x['promotores_count'].sum() - x['detractores_count'].sum()) / x['respuestas'].sum() * 100) if x['respuestas'].sum() > 0 else 0
    ).reset_index()
    mod_nps.columns = ['Modalidad', 'NPS']
    fig_mod = px.bar(mod_nps, x='Modalidad', y='NPS', title="NPS por Modalidad", color='Modalidad')
    col_op1.plotly_chart(fig_mod, use_container_width=True)
    
    # Tasa de respuesta por Modalidad
    mod_resp = df_f.groupby('MODALIDAD').apply(
        lambda x: (x['respuestas'].sum() / x['asistentes'].sum() * 100) if x['asistentes'].sum() > 0 else 0
    ).reset_index()
    mod_resp.columns = ['Modalidad', 'Tasa_Resp']
    fig_resp = px.bar(mod_resp, x='Modalidad', y='Tasa_Resp', title="Tasa de Respuesta por Modalidad", color_discrete_sequence=['#C0C0C0'])
    col_op2.plotly_chart(fig_resp, use_container_width=True)

# --- VISTA 5: INSIGHTS ---
with tabs[4]:
    st.subheader("Análisis de Comentarios (Voz del Cliente)")
    
    # Análisis simple de keywords para simular los flags
    df_f['pos_dinamismo'] = df_f['COMENTARIOS POSITIVOS'].str.contains('dinámico|juegos|interactuar|divertido|dinamica', case=False, na=False).astype(int)
    df_f['pos_claridad'] = df_f['COMENTARIOS POSITIVOS'].str.contains('claro|entendi|explicacion|preciso', case=False, na=False).astype(int)
    
    total_coment = df_f['COMENTARIOS POSITIVOS'].notna().sum()
    
    if total_coment > 0:
        pct_din = (df_f['pos_dinamismo'].sum() / total_coment * 100)
        pct_cla = (df_f['pos_claridad'].sum() / total_coment * 100)
        
        c_ins1, c_ins2 = st.columns(2)
        c_ins1.metric("Índice de Dinamismo", f"{pct_din:.1f}%")
        c_ins2.metric("Índice de Claridad", f"{pct_cla:.1f}%")
        
        st.markdown("---")
        st.write("### Detalle de Comentarios Recientes")
        st.table(df_f[['speaker_std', 'TEMA', 'COMENTARIOS POSITIVOS']].dropna().tail(15))
    else:
        st.info("No hay comentarios disponibles para analizar con los filtros seleccionados.")

# --- VISTA 6: CALIDAD ---
with tabs[5]:
    st.subheader("Auditoría de Datos")
    
    # Filtrar registros con errores
    errores = df_f[(df_f['flag_response_gt_100'] == "REVISAR") | (df_f['flag_missing_core'] == "REVISAR")]
    
    if not errores.empty:
        st.warning(f"Se han detectado {len(errores)} registros con anomalías.")
        st.dataframe(errores[['session_uid', 'SPEAKER', 'TEMA', 'flag_response_gt_100', 'flag_missing_core']], use_container_width=True)
    else:
        st.success("✅ Todos los datos procesados cumplen con los criterios de calidad.")

# Pie de página
st.markdown("---")
st.caption("Dashboard de Monitoreo de Calidad | Desarrollado para CEO & Coordinadores")
