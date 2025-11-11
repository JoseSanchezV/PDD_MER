import pandas as pd
import numpy as np
import os
import shutil
from typing import Optional

# --- CONSTANTES ---
# Cambiamos el nombre del archivo de entrada a data.xlsx (PDD_EXCEL_FILENAME)
PDD_EXCEL_FILENAME = "data.xlsx" 
SHEET_COEH = "COEH" # Nombre de la hoja dentro de data.xlsx

def run_ncp_coeh(archivo_principal_path: str, ruta_salida_dat: str, dest_date: Optional[str] = None,):
    """
    Procesa la hoja COEH del archivo data.xlsx (ubicado en 'data_path_comun') 
    a una resolución por hora (24 periodos), y genera el archivo hydro_cost.dat en 'ruta_salida_dat'.
    
    Parámetros:
    data_path_comun (str): La ruta al directorio que contiene el archivo data.xlsx.
    ruta_salida_dat (str): La ruta al directorio donde se guardará hydro_cost.dat.
    dest_date (str, opcional): La fecha de destino (no usada actualmente).
    """
    # --- CONFIGURACIÓN CON PARÁMETROS DE ENTRADA ---
    # Usamos la constante del archivo Excel
    output_file_name = 'hydro_cost.dat' 
    
    # Construcción de rutas de entrada y salida
    full_input_path = os.path.join(archivo_principal_path) 
    full_output_path = os.path.join(ruta_salida_dat, output_file_name)

    print(f"Buscando archivo de ENTRADA en: {full_input_path}")
    print(f"Buscando HOJA de ENTRADA: '{SHEET_COEH}'")
    print(f"Ruta de SALIDA esperada: {full_output_path}")

    chunk_size = 10000 
    DEFAULT_LEVEL = 1  
    NA_REPLACEMENT_VALUE = '0' 

    print(f"--- INICIO DEL PROCESO DE CONVERSIÓN (Archivo_NCP_COEH - Fuente: {PDD_EXCEL_FILENAME} - Hoja: {SHEET_COEH}) ---")
    print(f"Archivo de entrada: {full_input_path}")
    print(f"Archivo de salida: {full_output_path}")


    # 1. Lectura de la HOJA COEH desde data.xlsx
    print(f"\n1. Intentando leer la hoja '{SHEET_COEH}' del archivo '{PDD_EXCEL_FILENAME}'...")
    try:
        # Leemos la hoja COEH. Asumimos que la fila 3 (índice 2) contiene los encabezados.
        # En el script anterior, la fila 3 es el encabezado de las columnas de datos
        # Si data.xlsx-COEH tiene 2 filas de encabezado (Nemo y Hora), usamos header=2 (la tercera fila)
        df = pd.read_excel(full_input_path, sheet_name=SHEET_COEH, header=1)
        print(f"   -> Lectura exitosa de la hoja '{SHEET_COEH}'.")
    
    # --- Se elimina el fallback a CSV/delimitadores ya que ahora es Excel ---
    except FileNotFoundError:
        print(f"   -> ERROR: Archivo Excel '{full_input_path}' no encontrado.")
        raise FileNotFoundError(f"Archivo Excel '{full_input_path}' no encontrado.")
    except ValueError as ve:
        print(f"   -> ERROR: Hoja '{SHEET_COEH}' no encontrada o problema de formato. {ve}")
        raise ValueError(f"Hoja '{SHEET_COEH}' no encontrada o problema de formato.")
    except Exception as e:
        print(f"   -> ERROR al leer el archivo Excel: {e}")
        raise Exception(f"Error al leer el archivo Excel: {e}")

    print(f"   -> Filas leídas: {len(df):,}")


    # 2. Limpieza de columnas y preparación para output (NO HAY DESAGREGACIÓN)
    # ... El resto de la lógica de limpieza y formato permanece igual ...
    
    # Mapeo de los nombres de columna del nuevo archivo a nombres estándar
    NEW_COLUMN_MAPPING = {
        '!dd': 'DIA', 
        'mm': 'MES', 
        'aaaa': 'ANIO', 
        'hh': 'HORA', 
        'mm.1': 'MINUTO_ELIMINADO', # Columna eliminada
        'level': 'NIVEL' # Nivel de output
    }
    
    # Columnas de tiempo para el output final
    time_cols_base = ['DIA', 'MES', 'ANIO', 'HORA', 'NIVEL']

    # --- MEJORA EN LA LIMPIEZA DE ENCABEZADOS (para manejar '!dd' sin problemas) ---
    # Asumimos que la lectura con header=2 capturó los encabezados correctos ('!dd', 'mm', 'aaaa', 'hh', etc.)
    df.columns = (df.columns
                    .astype(str) # Asegurar que los nombres sean strings
                    .str.strip('\'"') 
                    .str.strip()) 
    
    # Renombrar columnas
    df.rename(columns=NEW_COLUMN_MAPPING, inplace=True)
    
    # Eliminamos la columna de minutos si existe
    if 'MINUTO_ELIMINADO' in df.columns:
        df.drop(columns=['MINUTO_ELIMINADO'], inplace=True)
    # Eliminamos la columna 'mm.1' si no se renombró (a veces Pandas mantiene el original si el renombrado es parcial)
    if 'mm.1' in df.columns: 
        df.drop(columns=['mm.1'], inplace=True)


    # Conversión y limpieza de las columnas de tiempo base
    for col in time_cols_base:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    df.dropna(subset=time_cols_base, inplace=True)
    
    # Identificar columnas de datos
    all_known_cols = set(['DIA', 'MES', 'ANIO', 'HORA', 'NIVEL', 'MINUTO_ELIMINADO', 'mm.1'])
    data_cols = [col for col in df.columns if col not in all_known_cols]
    
    # Convertir columnas de datos a numérico
    for col in data_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

   
    df['MINUTO'] = 0 
    df['NIVEL'] = DEFAULT_LEVEL

    df_final = df.copy()

    time_cols_final = ['DIA', 'MES', 'ANIO', 'HORA', 'MINUTO', 'NIVEL']
    output_cols_order = time_cols_final + data_cols
    df_final = df_final[output_cols_order].copy()
    print(f"   -> Filas totales (24 periodos por día): {len(df_final):,}")


    # 3. Creación de las líneas de salida en formato Archivo_NCP_COEH (60 Minutos)
    print("\n3. Dando formato a las líneas de salida con estructura Archivo_NCP_COEH...")

    def format_final_line_ncp(row, data_cols):
        # Parte de tiempo: dd,mm,aaaa,hh,mm,level
        time_part = f"{int(row['DIA']):02d},{int(row['MES']):02d},{int(row['ANIO'])},{int(row['HORA']):02d},{int(row['MINUTO']):02d},{int(row['NIVEL'])}"
        
        # Parte de datos
        data_parts = []
        for col in data_cols:
            val = row[col]
            if pd.isna(val):
                data_parts.append(NA_REPLACEMENT_VALUE)
            else:
                data_string = f"{val:.4f}".rstrip('0').rstrip('.')
                data_parts.append(data_string)

        data_part = ",".join(data_parts)
        return f"{time_part},{data_part}"

    df_final['DAT_LINE'] = df_final.apply(lambda row: format_final_line_ncp(row, data_cols), axis=1)

    total_lines = len(df_final)
    print(f"   -> Líneas de datos listas para escribir: {total_lines:,}")


    # 4. Guardar en el archivo hydro_cost.dat
    print(f"\n4. Iniciando la escritura en '{full_output_path}'...")
    
    # Preparar el encabezado
    official_header_time_cols = ['!dd', 'mm', 'aaaa', 'hh', 'mm', 'level']
    header_cols = official_header_time_cols + data_cols
    header = [",".join(header_cols)]

    data_lines = df_final['DAT_LINE'].tolist()

    try:
        # Asegurarse de que el directorio de salida exista
        os.makedirs(ruta_salida_dat, exist_ok=True)
        
        # Escribir usando la ruta de salida completa
        with open(full_output_path, 'w') as f:
            f.write(header[0] + '\n')
            lines_written = 0

            for i in range(0, total_lines, chunk_size):
                chunk = data_lines[i:i + chunk_size]
                # Aquí se quita la nueva línea al final del archivo si está al final
                f.write('\n'.join(chunk))
                if i + chunk_size < total_lines:
                    f.write('\n') # Añadir salto de línea solo entre chunks
                
                lines_written += len(chunk)

    except Exception as e:
        print(f"   -> ERROR al escribir el archivo '{full_output_path}': {e}")
        raise Exception(f"Error al escribir el archivo de salida: {e}")

    print(f"\n--- PROCESO Archivo_NCP_COEH COMPLETADO ---")
    print(f"El archivo '{output_file_name}' ha sido creado con éxito en: {ruta_salida_dat}")

if __name__ == "__main__":
    # --- CONFIGURACIÓN DE PRUEBA ---
    print("Ejecutando en modo independiente (Prueba). Creando archivo data.xlsx simulado...")
    
    # Definición de rutas relativas
    TEST_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    TEST_DATA_DIR = os.path.join(TEST_BASE_PATH, "test_data_in_ncp")
    TEST_OUTPUT_DIR = os.path.join(TEST_BASE_PATH, "test_data_out_ncp")
    
    # Ruta completa del archivo de entrada simulado
    TEST_PDD_EXCEL_PATH = os.path.join(TEST_DATA_DIR, PDD_EXCEL_FILENAME)
    
    # 1. Limpiar y Crear Directorios
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    
    # 2. Creación de datos de prueba
    test_data = {
        '!dd': [17] * 24, 'mm': [10] * 24, 'aaaa': [2025] * 24, 'hh': list(range(24)), 
        'mm.1': [0] * 24, 'level': [1] * 24, 
        "Unidad_A": [10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 
                     20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 30.0, 10.5, 10.5], 
        "Unidad_B": [5.0] * 24
    }
    
    # 3. Escribir el archivo Excel simulado
    df_test = pd.DataFrame(test_data)
    
    try:
        from openpyxl import Workbook # Necesario para escribir las filas dummy
        
        with pd.ExcelWriter(TEST_PDD_EXCEL_PATH, engine='openpyxl') as writer:
            # Crea un libro de trabajo (workbook) si no existe
            if not writer.book:
                writer.book = Workbook()
                writer.book.remove(writer.book.active) # Quitar la hoja por defecto

            # Añade la hoja 'COEH'
            writer.book.create_sheet(SHEET_COEH)
            writer.sheets[SHEET_COEH] = writer.book[SHEET_COEH]
            
            # Escribir las dos filas dummy que el lector de Excel se saltará (header=2)
            pd.DataFrame([['DUMMY_1', 'DUMMY_2', 'COL_A', 'COL_B', '...', '...']]).to_excel(writer, sheet_name=SHEET_COEH, startrow=0, header=False, index=False)
            pd.DataFrame([['DUMMY_A', 'DUMMY_B', 'COL_C', 'COL_D', '...', '...']]).to_excel(writer, sheet_name=SHEET_COEH, startrow=1, header=False, index=False)
            
            # Escribimos los datos (df_test) que serán leídos con header=2, comenzando en la fila 3 (índice 2)
            df_test.to_excel(writer, sheet_name=SHEET_COEH, startrow=2, header=True, index=False)
        
        print(f"\nArchivo de prueba '{PDD_EXCEL_FILENAME}' (Hoja '{SHEET_COEH}') creado con éxito en: {TEST_DATA_DIR}")

    except Exception as e:
        print(f"ERROR al crear el archivo de prueba: {e}")
        exit()

    # 4. Ejecutar la función principal
    try:
        print("\n--- INICIO DE LA PRUEBA DE run_ncp_coeh ---")
        # Se pasa la ruta ABSOLUTA del archivo de prueba
        run_ncp_coeh(TEST_PDD_EXCEL_PATH, TEST_OUTPUT_DIR, "17/10/2025")
        print("\nPrueba de ejecución finalizada con éxito.")
    except Exception as e:
        print(f"\nERROR durante la ejecución del módulo: {e}")
        
    # 5. Verificación (Opcional)
    if os.path.exists(os.path.join(TEST_OUTPUT_DIR, 'hydro_cost.dat')):
        print(f"Verificación: El archivo 'hydro_cost.dat' se creó en: {TEST_OUTPUT_DIR}")
    else:
        print("Verificación: El archivo 'hydro_cost.dat' NO se encontró.")
