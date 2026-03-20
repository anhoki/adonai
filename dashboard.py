# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Importar funciones desde matrix.py
from matrix import load_project_data, get_summary_statistics, get_projects_by_status, get_projects_by_department

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Proyectos",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Seguimiento de Proyectos")
st.markdown("---")

# Cargar datos desde el archivo Excel
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

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Obtener estadísticas resumidas
stats = get_summary_statistics(df)

# Filtros en el sidebar
instituciones = st.sidebar.multiselect(
    "Institución",
    options=df['INSTITUCION'].unique(),
    default=df['INSTITUCION'].unique()
)

tipos_proyecto = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=df['TIPO_PROYECTO'].unique(),
    default=df['TIPO_PROYECTO'].unique()
)

departamentos = st.sidebar.multiselect(
    "Departamento",
    options=df['DEPARTAMENTO'].unique(),
    default=df['DEPARTAMENTO'].unique()
)

estatus = st.sidebar.multiselect(
    "Estatus del Proyecto",
    options=df['ESTATUS'].unique(),
    default=df['ESTATUS'].unique()
)

rango_avance = st.sidebar.slider(
    "Rango de Avance Físico (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Aplicar filtros
df_filtrado = df[
    (df['INSTITUCION'].isin(instituciones)) &
    (df['TIPO_PROYECTO'].isin(tipos_proyecto)) &
    (df['DEPARTAMENTO'].isin(departamentos)) &
    (df['ESTATUS'].isin(estatus)) &
    (df['AVANCE_FISICO'].between(rango_avance[0], rango_avance[1]))
]

# Continuar con el resto del dashboard...
# [Aquí va todo el código del dashboard que ya te proporcioné,
#  pero usando los nombres de columnas actualizados:
#  - AVANCE_FISICO en lugar de '% AVANCE FISICO REAL'
#  - AVANCE_FINANCIERO en lugar de '% AVANCE FINANCIERO'
#  - INSTITUCION en lugar de 'INSTITUCIÓN'
#  - etc.]

# Métricas principales
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
    st.metric("Monto Total de Contratos", f"${monto_total:,.2f}")

st.markdown("---")

# Gráficos principales
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Avance por Tipo de Proyecto")
    fig_avance_tipo = px.bar(
        df_filtrado.groupby('TIPO_PROYECTO')[['AVANCE_FISICO', 'AVANCE_FINANCIERO']].mean().reset_index(),
        x='TIPO_PROYECTO',
        y=['AVANCE_FISICO', 'AVANCE_FINANCIERO'],
        barmode='group',
        title="Avance Promedio por Tipo de Proyecto"
    )
    st.plotly_chart(fig_avance_tipo, use_container_width=True)

with col2:
    st.subheader("💰 Montos por Institución")
    montos_inst = df_filtrado.groupby('INSTITUCION')['MONTO_MODIFICADO'].sum().reset_index()
    fig_montos = px.pie(
        montos_inst,
        values='MONTO_MODIFICADO',
        names='INSTITUCION',
        title="Distribución de Montos por Institución"
    )
    st.plotly_chart(fig_montos, use_container_width=True)

# Gráfico de evolución temporal
st.subheader("📅 Evolución de Proyectos por Año")
proyectos_por_año = df_filtrado.groupby('ANIO_INICIO').size().reset_index(name='Cantidad')
fig_temporal = px.line(
    proyectos_por_año,
    x='ANIO_INICIO',
    y='Cantidad',
    title="Cantidad de Proyectos Iniciados por Año",
    markers=True
)
st.plotly_chart(fig_temporal, use_container_width=True)

# Matriz de avance
st.subheader("🎯 Matriz de Avance Físico vs Financiero")
fig_scatter = px.scatter(
    df_filtrado,
    x='AVANCE_FISICO',
    y='AVANCE_FINANCIERO',
    color='ESTATUS',
    size='MONTO_MODIFICADO',
    hover_data=['NOMBRE_PROYECTO', 'INSTITUCION'],
    title="Relación entre Avance Físico y Financiero"
)
fig_scatter.add_trace(
    go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Línea de Referencia',
        line=dict(dash='dash', color='gray')
    )
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Tabla de datos filtrados
st.subheader("📋 Detalle de Proyectos")

# Seleccionar columnas para mostrar
columnas_mostrar = [
    'ID', 'NOMBRE_PROYECTO', 'INSTITUCION', 'TIPO_PROYECTO',
    'DEPARTAMENTO', 'MUNICIPIO', 'AVANCE_FISICO', 'AVANCE_FINANCIERO',
    'ESTATUS', 'MONTO_MODIFICADO', 'EMPRESA'
]

# Añadir barra de búsqueda
busqueda = st.text_input("🔍 Buscar proyecto:", "")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE_PROYECTO'].str.contains(busqueda, case=False)]

# Mostrar tabla
st.dataframe(
    df_filtrado[columnas_mostrar].style.format({
        'AVANCE_FISICO': '{:.1f}%',
        'AVANCE_FINANCIERO': '{:.1f}%',
        'MONTO_MODIFICADO': '${:,.2f}'
    }),
    use_container_width=True,
    height=400
)

# Proyectos con alertas
st.subheader("⚠️ Alertas de Proyectos")

# Proyectos con baja ejecución
proyectos_alerta = df_filtrado[
    (df_filtrado['AVANCE_FISICO'] < 30) & 
    (df_filtrado['ESTATUS'] == 'En ejecución')
]

if len(proyectos_alerta) > 0:
    st.warning(f"🚨 {len(proyectos_alerta)} proyectos con avance físico menor al 30%")
    st.dataframe(
        proyectos_alerta[['NOMBRE_PROYECTO', 'INSTITUCION', 'AVANCE_FISICO', 'AVANCE_FINANCIERO']],
        use_container_width=True
    )
else:
    st.success("✅ No hay proyectos con alertas críticas")

# Exportar datos
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar Datos")

if st.sidebar.button("Exportar a CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="Descargar CSV",
        data=csv,
        file_name=f"dashboard_proyectos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Información adicional
with st.expander("ℹ️ Información del Dashboard"):
    st.markdown(f"""
    **Resumen General:**
    - Total de proyectos: {stats.get('total_proyectos', 0)}
    - Monto total: ${stats.get('total_monto', 0):,.2f}
    - Proyectos completados: {stats.get('proyectos_completados', 0)}
    - Proyectos críticos (<30%): {stats.get('proyectos_criticos', 0)}
    - Empresas contratistas: {stats.get('total_empresas', 0)}
    
    **Cómo usar:**
    1. Utiliza los filtros en el panel izquierdo para seleccionar los proyectos de interés
    2. Explora los diferentes gráficos para obtener insights
    3. Revisa la tabla de detalle para ver información específica
    4. Exporta los datos filtrados si es necesario
    """)

st.markdown("---")
st.markdown(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
