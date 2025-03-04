import sqlite3
import os
import csv
from datetime import datetime


class SQLiteMineco:
    """Clase para gestionar la base de datos de indicadores económicos en SQLite."""

    def __init__(self, db_name="indicadores.db"):
        """Inicializa la conexión con la base de datos y crea la tabla si no existe."""
        self.db_name = db_name
        # Corregido 'con' a 'connect'
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()  # Completada la asignación del cursor
        self._crear_tabla()

    def _crear_tabla(self):
        """Crea la tabla de indicadores económicos si no existe."""
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
        """Inserta los datos de los CSV en la base de datos SQLite."""
        if not os.path.exists(output_dir):
            print(f"❌ El directorio {output_dir} no existe.")
            return

        for csv_file in os.listdir(output_dir):
            if csv_file.endswith(".csv"):
                file_path = os.path.join(output_dir, csv_file)
                nombre_indicador = csv_file.replace(
                    "indicadores_economicos_", "").replace(".csv", "")

                try:
                    with open(file_path, mode="r", encoding="utf-8") as file:
                        reader = csv.reader(file, delimiter="\t")
                        next(reader)  # omitir encabezados

                        # Preparar datos para inserción múltiple
                        datos = []
                        for row in reader:
                            try:
                                fecha = row[0]
                                # Convertir a float para asegurar tipo correcto
                                valor = float(row[1])
                                datos.append((fecha, valor, nombre_indicador))
                            except (ValueError, IndexError) as e:
                                print(
                                    f"⚠️ Error procesando fila en {csv_file}: {e}")
                                continue

                        # Ejecutar inserción múltiple
                        if datos:
                            self.cursor.executemany(
                                "INSERT INTO indicadores_economicos (fecha, valor, nombre_indicador) VALUES (?, ?, ?)",
                                datos
                            )
                            self.conn.commit()
                            print(f"✅ Datos insertados desde {csv_file}")

                except Exception as e:
                    print(f"❌ Error procesando {csv_file}: {e}")
                    self.conn.rollback()

    def mostrar_datos(self, limit=10):
        """Muestra los últimos `limit` registros de indicadores económicos."""
        try:
            self.cursor.execute(
                "SELECT fecha, valor, nombre_indicador, fecha_insercion FROM indicadores_economicos "
                "ORDER BY fecha_insercion DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()

            if not rows:
                print("\nNo hay datos para mostrar.")
                return

            print("\nÚltimos indicadores económicos insertados:")
            print("-" * 60)
            for row in rows:
                print(
                    f"Fecha: {row[0]} | Valor: {row[1]:.2f} | Indicador: {row[2]} | Insertado: {row[3]}")
            print("-" * 60)

        except Exception as e:
            print(f"❌ Error al mostrar datos: {e}")

    def close(self):
        """Cierra la conexión con la base de datos."""
        self.cursor.close()
        self.conn.close()
        print("🔒 Conexión con la base de datos cerrada.")


# Script de ejecución
if __name__ == "__main__":
    print("Iniciando procesamiento de indicadores económicos...")
    try:
        db = SQLiteMineco("indicadores.db")
        db.insertar_indicadores()
        db.mostrar_datos(10)
    except Exception as e:
        print(f"❌ Error en la ejecución principal: {e}")
    finally:
        db.close()
    print("✅ Proceso finalizado.")
