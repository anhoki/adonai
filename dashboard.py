# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import json

# Importar desde matrix.py
from matrix import load_project_data, get_summary_statistics

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Proyectos - Guatemala",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Seguimiento de Proyectos")
st.markdown("---")

# ============================================
# CARGA DE DATOS
# ============================================
@st.cache_data
def load_data():
    """
    Carga los datos usando la función de matrix.py
    """
    df = load_project_data('followingmatrix.xlsx')
    return df

# Cargar datos
try:
    df = load_data()
    if df is not None and not df.empty:
        st.success(f"✅ Datos cargados correctamente: {len(df)} proyectos")
    else:
        st.error("❌ No se encontraron datos en el archivo")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("📝 Asegúrate de que el archivo 'followingmatrix.xlsx' existe en el mismo directorio")
    st.stop()

# ============================================
# FILTROS JERÁRQUICOS - AÑO PRIMERO
# ============================================
st.sidebar.header("🔍 Filtros")

# FILTRO 1: AÑO (Principal)
st.sidebar.subheader("📅 1. Seleccionar Año")
años_disponibles = sorted(df['ANIO_INICIO'].unique())
años_seleccionados = st.sidebar.multiselect(
    "Año de inicio",
    options=años_disponibles,
    default=años_disponibles,
    help="Selecciona uno o más años para filtrar los proyectos"
)

# Filtrar por año primero
df_filtrado_año = df[df['ANIO_INICIO'].isin(años_seleccionados)]

# Verificar si hay datos después del filtro de año
if df_filtrado_año.empty:
    st.warning("⚠️ No hay proyectos en los años seleccionados. Por favor, selecciona otros años.")
    st.stop()

# FILTRO 2: INSTITUCIÓN (dependiente del año)
st.sidebar.subheader("🏛️ 2. Seleccionar Institución")
instituciones_disponibles = sorted(df_filtrado_año['INSTITUCION'].unique())
instituciones_seleccionadas = st.sidebar.multiselect(
    "Institución",
    options=instituciones_disponibles,
    default=instituciones_disponibles,
    help="Las instituciones disponibles dependen del año seleccionado"
)

# Filtrar por institución
df_filtrado_inst = df_filtrado_año[df_filtrado_año['INSTITUCION'].isin(instituciones_seleccionadas)]

# Verificar si hay datos después del filtro de institución
if df_filtrado_inst.empty:
    st.warning("⚠️ No hay proyectos para las instituciones seleccionadas en los años elegidos.")
    st.stop()

# FILTRO 3: Tipo de Proyecto
st.sidebar.subheader("📁 3. Seleccionar Tipo de Proyecto")
tipos_disponibles = sorted(df_filtrado_inst['TIPO_PROYECTO'].unique())
tipos_seleccionados = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=tipos_disponibles,
    default=tipos_disponibles
)

# Filtrar por tipo de proyecto
df_filtrado_tipo = df_filtrado_inst[df_filtrado_inst['TIPO_PROYECTO'].isin(tipos_seleccionados)]

# FILTRO 4: Departamento
st.sidebar.subheader("🗺️ 4. Seleccionar Departamento")
departamentos_disponibles = sorted(df_filtrado_tipo['DEPARTAMENTO'].unique())
departamentos_seleccionados = st.sidebar.multiselect(
    "Departamento",
    options=departamentos_disponibles,
    default=departamentos_disponibles
)

# Filtrar por departamento
df_filtrado_dep = df_filtrado_tipo[df_filtrado_tipo['DEPARTAMENTO'].isin(departamentos_seleccionados)]

# FILTRO 5: Estatus
st.sidebar.subheader("📌 5. Seleccionar Estatus")
estatus_disponibles = sorted(df_filtrado_dep['ESTATUS'].unique())
estatus_seleccionados = st.sidebar.multiselect(
    "Estatus del Proyecto",
    options=estatus_disponibles,
    default=estatus_disponibles
)

# Filtrar por estatus
df_filtrado = df_filtrado_dep[df_filtrado_dep['ESTATUS'].isin(estatus_seleccionados)]

# FILTRO 6: Rango de Avance
st.sidebar.subheader("📈 6. Rango de Avance Físico")
rango_avance = st.sidebar.slider(
    "Porcentaje de avance (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Filtrar por rango de avance
df_filtrado = df_filtrado[
    df_filtrado['AVANCE_FISICO'].between(rango_avance[0], rango_avance[1])
]

# Mostrar resumen de filtros aplicados
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumen de filtros")
st.sidebar.info(f"""
**Años:** {len(años_seleccionados)} seleccionados  
**Instituciones:** {len(instituciones_seleccionadas)} de {len(instituciones_disponibles)}  
**Tipos:** {len(tipos_seleccionados)}  
**Departamentos:** {len(departamentos_seleccionados)}  
**Estatus:** {len(estatus_seleccionados)}  
**Proyectos resultantes:** {len(df_filtrado)}
""")

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================
st.header("📈 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_proyectos = len(df_filtrado)
    st.metric("Total Proyectos", total_proyectos)

with col2:
    avance_fisico_promedio = df_filtrado['AVANCE_FISICO'].mean()
    st.metric("Avance Físico Promedio", f"{avance_fisico_promedio:.1f}%")

with col3:
    avance_financiero_promedio = df_filtrado['AVANCE_FINANCIERO'].mean()
    st.metric("Avance Financiero Promedio", f"{avance_financiero_promedio:.1f}%")

with col4:
    monto_total = df_filtrado['MONTO_MODIFICADO'].sum()
    st.metric("Monto Total de Contratos", f"Q{monto_total:,.2f}")
st.markdown("---")

# ============================================
# GRÁFICOS PRINCIPALES
# ============================================

# Gráfico 1: Evolución por año
st.subheader("📅 Evolución de Proyectos por Año")
proyectos_por_año = df_filtrado.groupby('ANIO_INICIO').size().reset_index(name='Cantidad')
fig_temporal = px.line(
    proyectos_por_año,
    x='ANIO_INICIO',
    y='Cantidad',
    title=f"Proyectos Iniciados ({', '.join(map(str, años_seleccionados))})",
    markers=True,
    line_shape='linear'
)
fig_temporal.update_traces(line=dict(width=3), marker=dict(size=10))
st.plotly_chart(fig_temporal, use_container_width=True)

# Gráficos en dos columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Avance por Tipo de Proyecto")
    avance_por_tipo = df_filtrado.groupby('TIPO_PROYECTO')[['AVANCE_FISICO', 'AVANCE_FINANCIERO']].mean().reset_index()
    fig_avance_tipo = px.bar(
        avance_por_tipo,
        x='TIPO_PROYECTO',
        y=['AVANCE_FISICO', 'AVANCE_FINANCIERO'],
        barmode='group',
        title="Avance Promedio por Tipo de Proyecto",
        labels={'value': 'Porcentaje (%)', 'variable': 'Tipo de Avance'},
        color_discrete_map={'AVANCE_FISICO': '#2E86AB', 'AVANCE_FINANCIERO': '#A23B72'}
    )
    st.plotly_chart(fig_avance_tipo, use_container_width=True)

with col2:
    st.subheader("💰 Montos por Institución")
    montos_inst = df_filtrado.groupby('INSTITUCION')['MONTO_MODIFICADO'].sum().reset_index()
    montos_inst = montos_inst.sort_values('MONTO_MODIFICADO', ascending=True)
    fig_montos = px.bar(
        montos_inst,
        x='MONTO_MODIFICADO',
        y='INSTITUCION',
        orientation='h',
        title="Distribución de Montos por Institución",
        labels={'MONTO_MODIFICADO': 'Monto Total (Q)', 'INSTITUCION': 'Institución'},
        color='MONTO_MODIFICADO',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_montos, use_container_width=True)

# Gráfico 3: Matriz de avance
st.subheader("🎯 Matriz de Avance Físico vs Financiero")
fig_scatter = px.scatter(
    df_filtrado,
    x='AVANCE_FISICO',
    y='AVANCE_FINANCIERO',
    color='ESTATUS',
    size='MONTO_MODIFICADO',
    hover_data=['NOMBRE_PROYECTO', 'INSTITUCION', 'TIPO_PROYECTO'],
    title="Relación entre Avance Físico y Financiero",
    labels={'AVANCE_FISICO': 'Avance Físico (%)', 'AVANCE_FINANCIERO': 'Avance Financiero (%)'}
)
fig_scatter.add_trace(
    go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Línea de Referencia (Ideal)',
        line=dict(dash='dash', color='gray', width=2)
    )
)
fig_scatter.update_layout(showlegend=True)
st.plotly_chart(fig_scatter, use_container_width=True)

if mapas_disponibles and not df_filtrado.empty:
    # TODO el código de los mapas (tabs, etc.)
    # con su indentación correcta
    with tab1:
        # ...
    with tab2:
        # ...
    with tab3:
        # ...
else:
    if df_filtrado.empty:
        st.info("ℹ️ No hay proyectos con los filtros seleccionados")



# ============================================
# TABLA DE DATOS
# ============================================
st.subheader("📋 Detalle de Proyectos")

# Seleccionar columnas para mostrar
columnas_mostrar = [
    'ID', 'NOMBRE_PROYECTO', 'ANIO_INICIO', 'INSTITUCION', 'TIPO_PROYECTO',
    'DEPARTAMENTO', 'MUNICIPIO', 'AVANCE_FISICO', 'AVANCE_FINANCIERO',
    'ESTATUS', 'MONTO_MODIFICADO', 'EMPRESA'
]

# Añadir barra de búsqueda
busqueda = st.text_input("🔍 Buscar por nombre de proyecto:", "")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE_PROYECTO'].str.contains(busqueda, case=False, na=False)]

# Mostrar tabla
st.dataframe(
    df_filtrado[columnas_mostrar].style.format({
        'AVANCE_FISICO': '{:.1f}%',
        'AVANCE_FINANCIERO': '{:.1f}%',
        'MONTO_MODIFICADO': 'Q{:,.2f}'
    }),
    use_container_width=True,
    height=400
)

# ============================================
# ALERTAS
# ============================================
st.subheader("⚠️ Alertas de Proyectos")

# Proyectos con baja ejecución
proyectos_alerta = df_filtrado[
    (df_filtrado['AVANCE_FISICO'] < 30) & 
    (df_filtrado['ESTATUS'] == 'En ejecución')
]

if len(proyectos_alerta) > 0:
    st.warning(f"🚨 {len(proyectos_alerta)} proyectos con avance físico menor al 30%")
    st.dataframe(
        proyectos_alerta[['NOMBRE_PROYECTO', 'INSTITUCION', 'ANIO_INICIO', 'AVANCE_FISICO', 'AVANCE_FINANCIERO', 'EMPRESA']],
        use_container_width=True
    )
else:
    st.success("✅ No hay proyectos con alertas críticas")

# Proyectos con retraso en ejecución financiera
proyectos_retraso = df_filtrado[
    (df_filtrado['AVANCE_FINANCIERO'] < df_filtrado['AVANCE_FISICO'] - 20)
]

if len(proyectos_retraso) > 0:
    st.info(f"📉 {len(proyectos_retraso)} proyectos con retraso financiero (avance financiero menor al avance físico)")
    with st.expander("Ver detalles"):
        st.dataframe(
            proyectos_retraso[['NOMBRE_PROYECTO', 'INSTITUCION', 'AVANCE_FISICO', 'AVANCE_FINANCIERO']],
            use_container_width=True
        )

# ============================================
# EXPORTAR DATOS
# ============================================
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar Datos")

if st.sidebar.button("Exportar a CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar CSV",
        data=csv,
        file_name=f"dashboard_proyectos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# ============================================
# INFORMACIÓN ADICIONAL
# ============================================
with st.expander("ℹ️ Información del Dashboard"):
    stats = get_summary_statistics(df_filtrado)
    st.markdown(f"""
**Resumen General de la Selección Actual:**
- Total de proyectos: {stats.get('total_proyectos', 0)}
- Monto total: Q{stats.get('total_monto', 0):,.2f}
- Avance físico promedio: {stats.get('avance_fisico_promedio', 0):.1f}%
- Avance financiero promedio: {stats.get('avance_financiero_promedio', 0):.1f}%
- Proyectos completados (≥95%): {stats.get('proyectos_completados', 0)}
- Proyectos críticos (<30%): {stats.get('proyectos_criticos', 0)}
- Empresas contratistas: {stats.get('total_empresas', 0)}
- Instituciones: {stats.get('total_instituciones', 0)}

**Cómo usar el dashboard:**
1. **Selecciona primero el año** - esto determina las opciones disponibles
2. Luego elige la institución
3. Continúa con tipo de proyecto, departamento y estatus
4. Ajusta el rango de avance si lo deseas
5. Explora los gráficos y los mapas interactivos
6. Exporta los datos filtrados si es necesario

**Nota:** Los filtros son jerárquicos - cada selección afecta las opciones disponibles.
""")

st.markdown("---")
st.markdown(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
