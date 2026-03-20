import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Proyectos",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Seguimiento de Proyectos")
st.markdown("---")

# Función para cargar datos (simulando carga desde CSV/Excel)
@st.cache_data
def load_data():
    """
    Aquí debes cargar tus datos reales.
    Puedes usar: pd.read_csv('tu_archivo.csv') o pd.read_excel('tu_archivo.xlsx')
    """
    # Datos de ejemplo - REEMPLAZAR CON TUS DATOS REALES
    data = {
        'No.': range(1, 101),
        'AÑO DE INICIO': np.random.randint(2015, 2024, 100),
        'INSTITUCIÓN': np.random.choice(['Ministerio de Salud', 'Ministerio de Educación', 'Ministerio de Transporte', 'Gobernación'], 100),
        'TIPO DE PROYECTO': np.random.choice(['Infraestructura', 'Tecnología', 'Social', 'Ambiental'], 100),
        'NOMBRE DEL PROYECTO': [f'Proyecto {i}' for i in range(1, 101)],
        'MUNICIPIO': np.random.choice(['Ciudad A', 'Ciudad B', 'Ciudad C', 'Ciudad D'], 100),
        'DEPARTAMENTO': np.random.choice(['Departamento 1', 'Departamento 2', 'Departamento 3'], 100),
        '% AVANCE FISICO REAL': np.random.uniform(0, 100, 100),
        '% AVANCE FINANCIERO': np.random.uniform(0, 100, 100),
        'ESTATUS DEL PROYECTO': np.random.choice(['En ejecución', 'Finalizado', 'Suspendido', 'En planificación'], 100),
        'ACCIONES REALIZADAS': ['Acción 1, Acción 2' for _ in range(100)],
        'SUPERVISOR INTERNO UCEE ACTUAL': np.random.choice(['Juan Pérez', 'María García', 'Carlos López'], 100),
        'SNIP': [f'SNIP-{i}' for i in range(1, 101)],
        'NOG': [f'NOG-{i}' for i in range(1, 101)],
        'CONTRATO': [f'CONT-{i}' for i in range(1, 101)],
        'LATITUD': np.random.uniform(-25, -15, 100),
        'LONGITUD': np.random.uniform(-65, -55, 100),
        'FECHA DE INICIO': pd.date_range('2020-01-01', periods=100, freq='M'),
        'FECHA FINALIZACION': pd.date_range('2020-12-01', periods=100, freq='M'),
        'PLAZO CONTRACTUAL': np.random.randint(90, 365, 100),
        'PRORROGA': np.random.choice(['Sí', 'No'], 100),
        'EMPRESA': np.random.choice(['Empresa A', 'Empresa B', 'Empresa C'], 100),
        'NIT': [f'{np.random.randint(1000000, 9999999)}-{np.random.randint(0, 9)}' for _ in range(100)],
        'MONTO DE CONTRATO ORIGINAL': np.random.uniform(100000, 5000000, 100),
        'DOCUMENTOS DE CAMBIO': ['Documento 1' for _ in range(100)],
        'MONTO DE CONTRATO MODIFICADO': np.random.uniform(100000, 6000000, 100),
        'MONTO PAGADO': np.random.uniform(50000, 4000000, 100),
        'SALDO PENDIENTE POR PAGAR': np.random.uniform(0, 2000000, 100),
    }
    
    df = pd.DataFrame(data)
    
    # Calcular algunas métricas adicionales
    df['EJECUCION_FISICA'] = df['% AVANCE FISICO REAL']
    df['EJECUCION_FINANCIERA'] = df['% AVANCE FINANCIERO']
    df['BRECHA_EJECUCION'] = df['EJECUCION_FINANCIERA'] - df['EJECUCION_FISICA']
    df['ESTADO_EJECUCION'] = np.where(df['EJECUCION_FISICA'] >= 95, 'Completado',
                               np.where(df['EJECUCION_FISICA'] >= 50, 'En progreso', 'Inicio'))
    
    return df

# Cargar datos
try:
    df = load_data()
    st.success("✅ Datos cargados correctamente")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.stop()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtros en el sidebar
instituciones = st.sidebar.multiselect(
    "Institución",
    options=df['INSTITUCIÓN'].unique(),
    default=df['INSTITUCIÓN'].unique()
)

tipos_proyecto = st.sidebar.multiselect(
    "Tipo de Proyecto",
    options=df['TIPO DE PROYECTO'].unique(),
    default=df['TIPO DE PROYECTO'].unique()
)

departamentos = st.sidebar.multiselect(
    "Departamento",
    options=df['DEPARTAMENTO'].unique(),
    default=df['DEPARTAMENTO'].unique()
)

estatus = st.sidebar.multiselect(
    "Estatus del Proyecto",
    options=df['ESTATUS DEL PROYECTO'].unique(),
    default=df['ESTATUS DEL PROYECTO'].unique()
)

rango_avance = st.sidebar.slider(
    "Rango de Avance Físico (%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Aplicar filtros
df_filtrado = df[
    (df['INSTITUCIÓN'].isin(instituciones)) &
    (df['TIPO DE PROYECTO'].isin(tipos_proyecto)) &
    (df['DEPARTAMENTO'].isin(departamentos)) &
    (df['ESTATUS DEL PROYECTO'].isin(estatus)) &
    (df['% AVANCE FISICO REAL'].between(rango_avance[0], rango_avance[1]))
]

# Métricas principales
st.header("📈 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_proyectos = len(df_filtrado)
    st.metric("Total Proyectos", total_proyectos)

with col2:
    avance_fisico_promedio = df_filtrado['% AVANCE FISICO REAL'].mean()
    st.metric("Avance Físico Promedio", f"{avance_fisico_promedio:.1f}%")

with col3:
    avance_financiero_promedio = df_filtrado['% AVANCE FINANCIERO'].mean()
    st.metric("Avance Financiero Promedio", f"{avance_financiero_promedio:.1f}%")

with col4:
    monto_total = df_filtrado['MONTO DE CONTRATO MODIFICADO'].sum()
    st.metric("Monto Total de Contratos", f"${monto_total:,.2f}")

st.markdown("---")

# Gráficos principales
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Avance por Tipo de Proyecto")
    fig_avance_tipo = px.bar(
        df_filtrado.groupby('TIPO DE PROYECTO')[['% AVANCE FISICO REAL', '% AVANCE FINANCIERO']].mean().reset_index(),
        x='TIPO DE PROYECTO',
        y=['% AVANCE FISICO REAL', '% AVANCE FINANCIERO'],
        barmode='group',
        title="Avance Promedio por Tipo de Proyecto"
    )
    st.plotly_chart(fig_avance_tipo, use_container_width=True)

with col2:
    st.subheader("💰 Montos por Institución")
    montos_inst = df_filtrado.groupby('INSTITUCIÓN')['MONTO DE CONTRATO MODIFICADO'].sum().reset_index()
    fig_montos = px.pie(
        montos_inst,
        values='MONTO DE CONTRATO MODIFICADO',
        names='INSTITUCIÓN',
        title="Distribución de Montos por Institución"
    )
    st.plotly_chart(fig_montos, use_container_width=True)

# Gráfico de evolución temporal
st.subheader("📅 Evolución de Proyectos por Año")
proyectos_por_año = df_filtrado.groupby('AÑO DE INICIO').size().reset_index(name='Cantidad')
fig_temporal = px.line(
    proyectos_por_año,
    x='AÑO DE INICIO',
    y='Cantidad',
    title="Cantidad de Proyectos Iniciados por Año",
    markers=True
)
st.plotly_chart(fig_temporal, use_container_width=True)

# Matriz de avance
st.subheader("🎯 Matriz de Avance Físico vs Financiero")
fig_scatter = px.scatter(
    df_filtrado,
    x='% AVANCE FISICO REAL',
    y='% AVANCE FINANCIERO',
    color='ESTATUS DEL PROYECTO',
    size='MONTO DE CONTRATO MODIFICADO',
    hover_data=['NOMBRE DEL PROYECTO', 'INSTITUCIÓN'],
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
    'No.', 'NOMBRE DEL PROYECTO', 'INSTITUCIÓN', 'TIPO DE PROYECTO',
    'DEPARTAMENTO', 'MUNICIPIO', '% AVANCE FISICO REAL', '% AVANCE FINANCIERO',
    'ESTATUS DEL PROYECTO', 'MONTO DE CONTRATO MODIFICADO', 'EMPRESA'
]

# Añadir barra de búsqueda
busqueda = st.text_input("🔍 Buscar proyecto:", "")
if busqueda:
    df_filtrado = df_filtrado[df_filtrado['NOMBRE DEL PROYECTO'].str.contains(busqueda, case=False)]

# Mostrar tabla
st.dataframe(
    df_filtrado[columnas_mostrar].style.format({
        '% AVANCE FISICO REAL': '{:.1f}%',
        '% AVANCE FINANCIERO': '{:.1f}%',
        'MONTO DE CONTRATO MODIFICADO': '${:,.2f}'
    }),
    use_container_width=True,
    height=400
)

# Proyectos con alertas
st.subheader("⚠️ Alertas de Proyectos")

# Proyectos con baja ejecución
proyectos_alerta = df_filtrado[
    (df_filtrado['% AVANCE FISICO REAL'] < 30) & 
    (df_filtrado['ESTATUS DEL PROYECTO'] == 'En ejecución')
]

if len(proyectos_alerta) > 0:
    st.warning(f"🚨 {len(proyectos_alerta)} proyectos con avance físico menor al 30%")
    st.dataframe(
        proyectos_alerta[['NOMBRE DEL PROYECTO', 'INSTITUCIÓN', '% AVANCE FISICO REAL', '% AVANCE FINANCIERO']],
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
    st.markdown("""
    **Descripción del Dashboard:**
    - Este dashboard permite visualizar y analizar el estado de los proyectos
    - Utiliza filtros interactivos para segmentar la información
    - Muestra métricas clave y gráficos de tendencias
    - Permite identificar proyectos con bajo avance
    
    **Cómo usar:**
    1. Utiliza los filtros en el panel izquierdo para seleccionar los proyectos de interés
    2. Explora los diferentes gráficos para obtener insights
    3. Revisa la tabla de detalle para ver información específica
    4. Exporta los datos filtrados si es necesario
    """)

st.markdown("---")
st.markdown("📅 Dashboard actualizado automáticamente con los datos más recientes")
