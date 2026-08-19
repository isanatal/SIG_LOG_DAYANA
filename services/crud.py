import pandas as pd

_conn = None


def init(connection):
    global _conn
    _conn = connection


def leer_tabla(nombre_tabla):
    return pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", _conn)


def insertar(nombre_tabla, datos: dict):
    columnas = ", ".join(datos.keys())
    signos = ", ".join(["?"] * len(datos))
    _conn.execute(f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({signos})", list(datos.values()))
    _conn.commit()


def actualizar(nombre_tabla, id_registro, datos: dict):
    set_clause = ", ".join([f"{k}=?" for k in datos.keys()])
    valores = list(datos.values()) + [id_registro]
    _conn.execute(f"UPDATE {nombre_tabla} SET {set_clause} WHERE id=?", valores)
    _conn.commit()


_DEPENDENCIAS = {
    "clientes":   [("entregas", "cliente_id")],
    "vehiculos":  [("entregas", "vehiculo_id"), ("combustible", "vehiculo_id"), ("mantenimiento", "vehiculo_id")],
    "operadores": [("entregas", "operador_id")],
    "rutas":      [("entregas", "ruta_id")],
}


def eliminar(nombre_tabla, id_registro):
    for tabla_hija, col_fk in _DEPENDENCIAS.get(nombre_tabla, []):
        _conn.execute(f"DELETE FROM {tabla_hija} WHERE {col_fk}=?", (id_registro,))
    _conn.execute(f"DELETE FROM {nombre_tabla} WHERE id=?", (id_registro,))
    _conn.commit()
