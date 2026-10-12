import os
import csv

def migrar_datos(carpeta_csvs: str, carpeta_sqls: str) -> None:
    """ Función encargada de la migración de datos de csv a sql.
    Se encarga de leer los archivos csv y crear los archivos sql
    para la inserción en la base de datos.
    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
    """
    pass
    
    os.makedirs(carpeta_sqls, exist_ok=True)
    if not os.path.exists(carpeta_csvs):
        print(f"Error: La carpeta {carpeta_csvs} no existe.")
        return

    archivos_csv = [f for f in os.listdir(carpeta_csvs) if f.endswith('.csv')]

    for archivo in archivos_csv:
        ruta_csv = os.path.join(carpeta_csvs, archivo)
        nombre_tabla = os.path.splitext(archivo)[0] 
        ruta_sql = os.path.join(carpeta_sqls, f"{nombre_tabla}.sql")
        
        with open(ruta_csv, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            campos = reader.fieldnames
            if not campos: continue
            
            columnas_str = ", ".join(campos)
            sentencias = []
            
            for fila in reader:
                valores = []
                for campo in campos:
                    valor = fila[campo].strip() if fila[campo] else ""
                    if valor.isdigit():
                        valores.append(valor)
                    else:
                        try:
                            float(valor)
                            # Evita convertir fechas YYYY-MM-DD a floats erróneos
                            if "-" in valor and len(valor) >= 8:
                                raise ValueError
                            valores.append(valor)
                        except ValueError:
                            valor_escapado = valor.replace("'", "''")
                            valores.append(f"'{valor_escapado}'")
                
                valores_str = ", ".join(valores)
                sentencia = f"INSERT INTO {nombre_tabla} ({columnas_str}) VALUES ({valores_str});\n"
                sentencias.append(sentencia)
        
        with open(ruta_sql, mode='w', encoding='utf-8') as f_out:
            f_out.writelines(sentencias)
        print(f"Archivo generado: {ruta_sql} ({len(sentencias)} registros para la tabla '{nombre_tabla}').")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_csv = os.path.join(base_dir, 'csv')
    dir_sql = os.path.join(base_dir, 'sql')
    migrar_datos(dir_csv, dir_sql)