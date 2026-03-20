# matrix.py
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

def load_project_data(excel_file='followingmatrix.xlsx'):
    """
    Carga los datos del archivo Excel y realiza el preprocesamiento
    """
    try:
        # Cargar datos desde Excel
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # Limpiar nombres de columnas (eliminar espacios y caracteres especiales)
        df.columns = df.columns.str.strip()
        
        # Mostrar columnas para depuración (opcional)
        print("Columnas encontradas:", df.columns.tolist())
        
        # Verificar si las columnas existen
        columnas_requeridas = ['No.', '% AVANCE FISICO REAL', '% AVANCE FINANCIERO']
        for col in columnas_requeridas:
            if col not in df.columns:
                raise KeyError(f"Columna '{col}' no encontrada. Columnas disponibles: {df.columns.tolist()}")
        
        # Renombrar columnas para facilitar el manejo
        mapeo_columnas = {
            'No.': 'ID',
            'AÑO DE INICIO': 'ANIO_INICIO',
            'INSTITUCIÓN': 'INSTITUCION',
            'TIPO DE PROYECTO': 'TIPO_PROYECTO',
            'NOMBRE  DEL  PROYECTO': 'NOMBRE_PROYECTO',
            'MUNICIPIO': 'MUNICIPIO',
            'DEPARTAMENTO': 'DEPARTAMENTO',
            '% AVANCE FISICO REAL': 'AVANCE_FISICO',
            '% AVANCE FINANCIERO': 'AVANCE_FINANCIERO',
            'ESTATUS DEL PROYECTO': 'ESTATUS',
            'ACCIONES REALIZADAS': 'ACCIONES',
            'SUPERVISOR INTERNO UCEE ACTUAL': 'SUPERVISOR',
            'SNIP': 'SNIP',
            'NOG': 'NOG',
            'CONTRATO': 'CONTRATO',
            'LATITUD': 'LATITUD',
            'LONGITUD': 'LONGITUD',
            'FECHA DE INICIO': 'FECHA_INICIO',
            'FECHA FINALIZACION': 'FECHA_FIN',
            'PLAZO CONTRACTUAL': 'PLAZO_CONTRACTUAL',
            'PRORROGA': 'PRORROGA',
            'EMPRESA': 'EMPRESA',
            'NIT': 'NIT',
            'MONTO DE CONTRATO ORIGINAL': 'MONTO_ORIGINAL',
            'DOCUMENTOS DE CAMBIO': 'DOCUMENTOS_CAMBIO',
            'MONTO DE CONTRATO MODIFICADO': 'MONTO_MODIFICADO',
            'MONTO PAGADO': 'MONTO_PAGADO',
            'SALDO PENDIENTE POR PAGAR': 'SALDO_PENDIENTE'
        }
        
        # Solo renombrar columnas que existen
        columnas_existentes = {k: v for k, v in mapeo_columnas.items() if k in df.columns}
        df.rename(columns=columnas_existentes, inplace=True)
        
        # Convertir columnas numéricas
        numeric_columns = ['AVANCE_FISICO', 'AVANCE_FINANCIERO', 'MONTO_ORIGINAL', 
                          'MONTO_MODIFICADO', 'MONTO_PAGADO', 'SALDO_PENDIENTE', 
                          'PLAZO_CONTRACTUAL']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convertir fechas
        date_columns = ['FECHA_INICIO', 'FECHA_FIN']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calcular métricas adicionales solo si las columnas existen
        if 'AVANCE_FISICO' in df.columns and 'AVANCE_FINANCIERO' in df.columns:
            df['EJECUCION_FISICA'] = df['AVANCE_FISICO']
            df['EJECUCION_FINANCIERA'] = df['AVANCE_FINANCIERO']
            df['BRECHA_EJECUCION'] = df['AVANCE_FINANCIERO'] - df['AVANCE_FISICO']
            
            # Clasificar estado de ejecución
            df['ESTADO_EJECUCION'] = np.where(
                df['AVANCE_FISICO'] >= 95, 'Completado',
                np.where(df['AVANCE_FISICO'] >= 50, 'En progreso', 'Inicio')
            )
        
        # Calcular días restantes si hay fecha de fin
        if 'FECHA_FIN' in df.columns:
            df['DIAS_RESTANTES'] = (df['FECHA_FIN'] - datetime.now()).dt.days
        
        # Calcular eficiencia de ejecución
        if 'MONTO_PAGADO' in df.columns and 'MONTO_MODIFICADO' in df.columns and 'AVANCE_FISICO' in df.columns:
            df['EFICIENCIA'] = np.where(
                (df['AVANCE_FISICO'] > 0) & (df['MONTO_MODIFICADO'] > 0),
                (df['MONTO_PAGADO'] / df['MONTO_MODIFICADO']) / (df['AVANCE_FISICO'] / 100),
                0
            )
        
        return df
        
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_summary_statistics(df):
    """
    Genera estadísticas resumidas del dataframe
    """
    if df is None or df.empty:
        return {}
    
    stats = {
        'total_proyectos': len(df),
        'total_monto': df['MONTO_MODIFICADO'].sum() if 'MONTO_MODIFICADO' in df.columns else 0,
        'avance_fisico_promedio': df['AVANCE_FISICO'].mean() if 'AVANCE_FISICO' in df.columns else 0,
        'avance_financiero_promedio': df['AVANCE_FINANCIERO'].mean() if 'AVANCE_FINANCIERO' in df.columns else 0,
        'proyectos_completados': len(df[df['AVANCE_FISICO'] >= 95]) if 'AVANCE_FISICO' in df.columns else 0,
        'proyectos_criticos': len(df[df['AVANCE_FISICO'] < 30]) if 'AVANCE_FISICO' in df.columns else 0,
        'total_empresas': df['EMPRESA'].nunique() if 'EMPRESA' in df.columns else 0,
        'total_instituciones': df['INSTITUCION'].nunique() if 'INSTITUCION' in df.columns else 0,
        'monto_pagado_total': df['MONTO_PAGADO'].sum() if 'MONTO_PAGADO' in df.columns else 0,
        'saldo_pendiente_total': df['SALDO_PENDIENTE'].sum() if 'SALDO_PENDIENTE' in df.columns else 0
    }
    
    return stats

def get_projects_by_status(df):
    """
    Agrupa proyectos por estado
    """
    if df is None or df.empty or 'ESTATUS' not in df.columns:
        return pd.DataFrame()
    
    return df.groupby('ESTATUS').agg({
        'ID': 'count',
        'MONTO_MODIFICADO': 'sum' if 'MONTO_MODIFICADO' in df.columns else 'ID',
        'AVANCE_FISICO': 'mean' if 'AVANCE_FISICO' in df.columns else 'ID'
    }).reset_index()

def get_projects_by_department(df):
    """
    Agrupa proyectos por departamento
    """
    if df is None or df.empty or 'DEPARTAMENTO' not in df.columns:
        return pd.DataFrame()
    
    return df.groupby('DEPARTAMENTO').agg({
        'ID': 'count',
        'MONTO_MODIFICADO': 'sum' if 'MONTO_MODIFICADO' in df.columns else 'ID',
        'AVANCE_FISICO': 'mean' if 'AVANCE_FISICO' in df.columns else 'ID'
    }).reset_index()

# Si ejecutas este archivo directamente, prueba la carga
if __name__ == "__main__":
    print("Cargando datos de followingmatrix.xlsx...")
    df = load_project_data()
    
    if df is not None:
        print(f"✅ Datos cargados: {len(df)} registros")
        print(f"\n📊 Columnas disponibles:")
        for col in df.columns:
            print(f"  - {col}: {df[col].dtype}")
        
        stats = get_summary_statistics(df)
        print(f"\n📈 Estadísticas básicas:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ Error al cargar los datos")
