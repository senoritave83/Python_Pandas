# 📊 ConstruData Insights - Análisis de Indicadores Macroeconómicos

🚀 **Automatización del procesamiento de datos macroeconómicos para el sector de la construcción.**

## 📌 Descripción

Este proyecto descarga, procesa y almacena indicadores macroeconómicos del **Ministerio de Economía, Comercio y Empresa de España**, con el objetivo de facilitar el análisis de datos en el sector de la construcción e inversión inmobiliaria.

El sistema se encarga de:
1. **Descargar un archivo ZIP** con más de 10,000 indicadores macroeconómicos.
2. **Extraer y procesar los datos relevantes** con `Pandas`, normalizando y transformando la información.
3. **Guardar los datos en SQLite** para facilitar consultas y análisis futuros.

---

## 📦 Requisitos

### 🔹 **Librerías necesarias**
Antes de ejecutar el proyecto, asegúrate de tener instaladas las siguientes dependencias:

```sh
pip install -r requirements.txt


##########################################%%%%%%%%%%%%%%%%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%%%%%%%%%%%%##############################################################


# Caso Práctico: SQLiteMineco - Gestión de Indicadores Económicos

Este documento describe el script `sqlite_mineco_alumnos.py`, que gestiona indicadores económicos almacenándolos en una base de datos SQLite. El script incluye tres ejercicios: corrección del código original, cálculo de variación mensual con Pandas, y manejo de archivos ZIP sin BytesIO. A continuación, se detalla cada parte.

---

📊## Ejercicio 1: Corrección del Código Base📊

### Objetivo
- Insertar datos desde archivos CSV.
- Mostrar los datos insertados.
- Cerrar la conexión adecuadamente.

### Problemas Originales
- `sqlite3.con` en lugar de `sqlite3.connect`.
- Asignación incompleta de `self.cursor`.
- Uso incorrecto de `sqlExecutor` en lugar de `executemany`.
- Consulta SQL incompleta en `mostrar_datos`.
- Método `close()` sin implementación.

### Solución
El código corregido inicializa correctamente la conexión, crea una tabla, inserta datos desde CSV y los muestra. Aquí está el código base corregido:

---------------------------------------------------------------------------------------------------------------------------------------------------------------

import sqlite3
import os
import csv

class SQLiteMineco:
    def __init__(self, db_name="indicadores.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._crear_tabla()

    def _crear_tabla(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicadores_economicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                valor REAL,
                nombre_indicador TEXT,
                fecha_insercion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insertar_indicadores(self, output_dir="data/indicadores"):
        for csv_file in os.listdir(output_dir):
            if csv_file.endswith(".csv"):
                file_path = os.path.join(output_dir, csv_file)
                nombre_indicador = csv_file.replace("indicadores_economicos_", "").replace(".csv", "")
                with open(file_path, mode="r", encoding="utf-8") as file:
                    reader = csv.reader(file, delimiter="\t")
                    next(reader)  # Omitir encabezados
                    self.cursor.executemany(
                        "INSERT INTO indicadores_economicos (fecha, valor, nombre_indicador) VALUES (?, ?, ?)",
                        [(row[0], float(row[1]), nombre_indicador) for row in reader]
                    )
                self.conn.commit()
                print(f"✅ Datos insertados desde {csv_file}.")

    def mostrar_datos(self, limit=10):
        self.cursor.execute(
            "SELECT fecha, valor, nombre_indicador, fecha_insercion FROM indicadores_economicos "
            "ORDER BY fecha_insercion DESC LIMIT ?",
            (limit,)
        )
        rows = self.cursor.fetchall()
        print("\nÚltimos indicadores económicos insertados:")
        print("-" * 60)
        for row in rows:
            print(f"Fecha: {row[0]} | Valor: {row[1]:.2f} | Indicador: {row[2]} | Insertado: {row[3]}")
        print("-" * 60)

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("🔒 Conexión cerrada.")

if __name__ == "__main__":
    db = SQLiteMineco("indicadores.db")
    db.insertar_indicadores()
    db.mostrar_datos(10)
    db.close()

----------------------------------------------------------------------------------------------------------------------------------------------------------------

📦Funcionamiento
Inicialización: Conecta a SQLite y crea una tabla con columnas id, fecha, valor, nombre_indicador y fecha_insercion.
Inserción: Lee CSV desde data/indicadores, extrae el nombre del indicador del nombre del archivo, e inserta los datos.
Visualización: Muestra los últimos 10 registros ordenados por fecha de inserción.
Cierre: Cierra cursor y conexión

##########################################################%%%%%%%%%%%%%%%%%%&&&&&&&&&&&&&&&&&&&&###################################################################

📊Ejercicio 2: Transformación con Pandas (Variación Mensual)📊
Añadir una columna variacion_mensual que calcule la variación porcentual respecto al mes anterior:

Fórmula: ((Valor Actual - Valor Anterior) / Valor Anterior) * 100.
Primer valor debe ser NaN.
Datos deben ordenarse por fecha antes del cálculo.

🔹Implementación
Se usa Pandas para leer los CSV, ordenar por fecha y calcular la variación. La tabla se actualiza para incluir la nueva columna:

----------------------------------------------------------------------------------------------------------------------------------------------------------------

import pandas as pd

# En _crear_tabla o _crear_o_actualizar_tabla:
self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicadores_economicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        valor REAL,
        nombre_indicador TEXT,
        variacion_mensual REAL,
        fecha_insercion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
# Añadir columna si no existe (para bases existentes):
self.cursor.execute("PRAGMA table_info(indicadores_economicos)")
if 'variacion_mensual' not in [col[1] for col in self.cursor.fetchall()]:
    self.cursor.execute("ALTER TABLE indicadores_economicos ADD COLUMN variacion_mensual REAL")

# Método insertar_indicadores actualizado:
def insertar_indicadores(self, output_dir="data/indicadores"):
    for csv_file in os.listdir(output_dir):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(output_dir, csv_file)
            nombre_indicador = csv_file.replace("indicadores_economicos_", "").replace(".csv", "")
            try:
                df = pd.read_csv(file_path, sep="\t", names=['fecha', 'valor'])
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df = df.sort_values('fecha')
                df['variacion_mensual'] = df['valor'].pct_change() * 100
                df['nombre_indicador'] = nombre_indicador
                datos = [
                    (
                        row['fecha'].strftime('%Y-%m-%d') if pd.notnull(row['fecha']) else None,
                        row['valor'],
                        row['nombre_indicador'],
                        row['variacion_mensual'] if pd.notnull(row['variacion_mensual']) else None
                    )
                    for _, row in df.iterrows()
                ]
                self.cursor.executemany(
                    "INSERT INTO indicadores_economicos (fecha, valor, nombre_indicador, variacion_mensual) "
                    "VALUES (?, ?, ?, ?)",
                    datos
                )
                self.conn.commit()
                print(f"✅ Datos insertados desde {csv_file}")
            except Exception as e:
                print(f"❌ Error procesando {csv_file}: {e}")
                self.conn.rollback()

# Actualizar mostrar_datos:
def mostrar_datos(self, limit=10):
    self.cursor.execute(
        "SELECT fecha, valor, nombre_indicador, variacion_mensual, fecha_insercion "
        "FROM indicadores_economicos ORDER BY fecha_insercion DESC LIMIT ?",
        (limit,)
    )
    rows = self.cursor.fetchall()
    print("\nÚltimos indicadores económicos insertados:")
    print("-" * 80)
    for row in rows:
        var_mensual = f"{row[3]:.2f}%" if row[3] is not None else "NaN"
        print(f"Fecha: {row[0]} | Valor: {row[1]:.2f} | Indicador: {row[2]} | Var. Mensual: {var_mensual} | Insertado: {row[4]}")
    print("-" * 80)

---------------------------------------------------------------------------------------------------------------------------------------------------------------    

📦 Funcionamiento
Tabla: Se añade variacion_mensual REAL. Si la tabla ya existe, se usa ALTER TABLE.
Inserción: Pandas lee el CSV, ordena por fecha, calcula la variación con pct_change(), y mantiene NaN para el primer valor.
Visualización: Muestra la variación como porcentaje o "NaN"

#######################################################&&&&&&&&&&&&&&&&%%%%%%%%%%%%%%%%%%%#######################################################################

📊Ejercicio 3: Manejo de ZIP sin BytesIO📊
Objetivo
Modificar el manejo de archivos ZIP para:

Descargar el ZIP a un archivo físico en lugar de usar BytesIO.
Extraer los CSV desde el archivo guardado.
Eliminar el ZIP tras procesarlo.

🔹Implementación
Se añaden dos métodos para descargar y extraer el ZIP:


---------------------------------------------------------------------------------------------------------------------------------------------------------------
import requests
import zipfile

def download_zip_to_file(self, url, output_path="temp.zip"):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ ZIP descargado en {output_path}")
        return output_path
    except requests.RequestException as e:
        print(f"❌ Error al descargar ZIP: {e}")
        return None

def extract_dataframes_from_zip_file(self, zip_path, output_dir="data/indicadores"):
    if not os.path.exists(zip_path):
        print(f"❌ El archivo ZIP {zip_path} no existe.")
        return False
    try:
        os.makedirs(output_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"✅ Archivos extraídos a {output_dir}")
        return True
    except zipfile.BadZipFile as e:
        print(f"❌ Error al extraer ZIP: {e}")
        return False
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"🗑️ ZIP temporal {zip_path} eliminado")

# Ejemplo en el bloque principal:
if __name__ == "__main__":
    db = SQLiteMineco("indicadores.db")
    zip_file = r"C:\Users\Propietario\OneDrive\Documentos\caso_practico-main\data\bdsicecsv.zip"  # O descargar desde URL
    if db.extract_dataframes_from_zip_file(zip_file):
        db.insertar_indicadores()
        db.mostrar_datos(10)
    db.close()

------------------------------------------------------------------------------------------------------------------------------------------------------------

📦Funcionamiento
Descarga: download_zip_to_file guarda el ZIP en disco (opcional si usas un archivo local).
Extracción: extract_dataframes_from_zip_file extrae los CSV a data/indicadores y elimina el ZIP.
Integración: Los CSV extraídos se procesan con insertar_indicadores.
Código Completo


################################################&&&&&&&&&&&&&&&&&&%%%%%%%%%%%%%%%%################################################################################

📊Aquí está el script final combinando los tres ejercicios:📊

----------------------------------------------------------------------------------------------------------------------------------------------------------------
import sqlite3
import os
import csv
import pandas as pd
import requests
import zipfile

class SQLiteMineco:
    def __init__(self, db_name="indicadores.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._crear_o_actualizar_tabla()

    def _crear_o_actualizar_tabla(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicadores_economicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                valor REAL,
                nombre_indicador TEXT,
                fecha_insercion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("PRAGMA table_info(indicadores_economicos)")
        if 'variacion_mensual' not in [col[1] for col in self.cursor.fetchall()]:
            self.cursor.execute("ALTER TABLE indicadores_economicos ADD COLUMN variacion_mensual REAL")
        self.conn.commit()

    def download_zip_to_file(self, url, output_path="temp.zip"):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ ZIP descargado en {output_path}")
            return output_path
        except requests.RequestException as e:
            print(f"❌ Error al descargar ZIP: {e}")
            return None

    def extract_dataframes_from_zip_file(self, zip_path, output_dir="data/indicadores"):
        if not os.path.exists(zip_path):
            print(f"❌ El archivo ZIP {zip_path} no existe.")
            return False
        try:
            os.makedirs(output_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print(f"✅ Archivos extraídos a {output_dir}")
            return True
        except zipfile.BadZipFile as e:
            print(f"❌ Error al extraer ZIP: {e}")
            return False
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                print(f"🗑️ ZIP temporal {zip_path} eliminado")

    def insertar_indicadores(self, output_dir="data/indicadores"):
        for csv_file in os.listdir(output_dir):
            if csv_file.endswith(".csv"):
                file_path = os.path.join(output_dir, csv_file)
                nombre_indicador = csv_file.replace("indicadores_economicos_", "").replace(".csv", "")
                try:
                    df = pd.read_csv(file_path, sep="\t", names=['fecha', 'valor'])
                    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                    df = df.sort_values('fecha')
                    df['variacion_mensual'] = df['valor'].pct_change() * 100
                    df['nombre_indicador'] = nombre_indicador
                    datos = [
                        (
                            row['fecha'].strftime('%Y-%m-%d') if pd.notnull(row['fecha']) else None,
                            row['valor'],
                            row['nombre_indicador'],
                            row['variacion_mensual'] if pd.notnull(row['variacion_mensual']) else None
                        )
                        for _, row in df.iterrows()
                    ]
                    self.cursor.executemany(
                        "INSERT INTO indicadores_economicos (fecha, valor, nombre_indicador, variacion_mensual) "
                        "VALUES (?, ?, ?, ?)",
                        datos
                    )
                    self.conn.commit()
                    print(f"✅ Datos insertados desde {csv_file}")
                except Exception as e:
                    print(f"❌ Error procesando {csv_file}: {e}")
                    self.conn.rollback()

    def mostrar_datos(self, limit=10):
        try:
            self.cursor.execute(
                "SELECT fecha, valor, nombre_indicador, variacion_mensual, fecha_insercion "
                "FROM indicadores_economicos ORDER BY fecha_insercion DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()
            print("\nÚltimos indicadores económicos insertados:")
            print("-" * 80)
            for row in rows:
                var_mensual = f"{row[3]:.2f}%" if row[3] is not None else "NaN"
                print(f"Fecha: {row[0]} | Valor: {row[1]:.2f} | Indicador: {row[2]} | Var. Mensual: {var_mensual} | Insertado: {row[4]}")
            print("-" * 80)
        except Exception as e:
            print(f"❌ Error al mostrar datos: {e}")

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("🔒 Conexión cerrada.")

if __name__ == "__main__":
    print("Iniciando procesamiento de indicadores económicos...")
    try:
        db = SQLiteMineco("indicadores.db")
        zip_file = r"C:\Users\Propietario\OneDrive\Documentos\caso_practico-main\data\bdsicecsv.zip"
        if db.extract_dataframes_from_zip_file(zip_file):
            db.insertar_indicadores()
            db.mostrar_datos(10)
    except Exception as e:
        print(f"❌ Error en la ejecución principal: {e}")
    finally:
        db.close()
    print("✅ Proceso finalizado.")


---------------------------------------------------------------------------------------------------------------------------------------------------------------

📦Funcionamiento
Coloca un archivo ZIP (ej. bdsicecsv.zip) en la ruta especificada o ajusta la ruta/URL.
Ejecuta el script: python sqlite_mineco_alumnos.py.
El script extraerá los CSV, calculará la variación mensual, insertará los datos y mostrará los últimos 10 registros.