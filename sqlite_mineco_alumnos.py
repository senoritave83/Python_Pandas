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