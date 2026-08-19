"""
SIG-LOG - Módulo de base de datos
Crea la base de datos SQLite con las tablas requeridas y datos de ejemplo.
Ejecuta este archivo una sola vez (o bórralo y vuelve a correrlo) para
reiniciar la base de datos: python database.py
"""
import sqlite3
import random
import hashlib
from datetime import datetime, timedelta

DB_PATH = "data/sig_log.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_tablas(conn):
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        contacto TEXT,
        direccion TEXT
    );

    CREATE TABLE IF NOT EXISTS vehiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placas TEXT NOT NULL,
        modelo TEXT,
        capacidad_kg REAL,
        estatus TEXT DEFAULT 'Activo'
    );

    CREATE TABLE IF NOT EXISTS operadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        licencia TEXT,
        telefono TEXT
    );

    CREATE TABLE IF NOT EXISTS rutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origen TEXT NOT NULL,
        destino TEXT NOT NULL,
        distancia_km REAL
    );

    CREATE TABLE IF NOT EXISTS entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        vehiculo_id INTEGER,
        operador_id INTEGER,
        ruta_id INTEGER,
        fecha TEXT,
        hora_salida TEXT,
        minutos_estimados REAL,
        minutos_reales REAL,
        estatus TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
        FOREIGN KEY (operador_id) REFERENCES operadores(id),
        FOREIGN KEY (ruta_id) REFERENCES rutas(id)
    );

    CREATE TABLE IF NOT EXISTS combustible (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehiculo_id INTEGER,
        fecha TEXT,
        litros REAL,
        costo REAL,
        km_recorridos REAL,
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
    );

    CREATE TABLE IF NOT EXISTS mantenimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehiculo_id INTEGER,
        fecha TEXT,
        tipo TEXT,
        costo REAL,
        descripcion TEXT,
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)
    );

    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT,
        rol TEXT DEFAULT 'operador',
        activo INTEGER DEFAULT 1,
        fecha_creacion TEXT
    );
    """)
    conn.commit()


def hay_datos(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM clientes")
    return cur.fetchone()[0] > 0


def cargar_datos_ejemplo(conn):
    """Inserta datos de ejemplo SOLO si las tablas están vacías."""
    if hay_datos(conn):
        return

    cur = conn.cursor()
    random.seed(42)

    clientes = [
        ("Grupo Alfa", "555-1001", "Av. Reforma 100, CDMX"),
        ("Comercial Beta", "555-1002", "Blvd. Toluca 45, Toluca"),
        ("Distribuidora Gama", "555-1003", "Calle 5 de Mayo 12, Puebla"),
        ("Tiendas Delta", "555-1004", "Av. Industrias 300, Querétaro"),
        ("Farmacias Épsilon", "555-1005", "Periférico Sur 900, CDMX"),
        ("Refaccionaria Zeta", "555-1006", "Av. Morelos 55, Cuernavaca"),
        ("Ferretería Omega", "555-1007", "Av. Hidalgo 210, Toluca"),
        ("Supermercados Sigma", "555-1008", "Blvd. Manuel Ávila Camacho 800, Toluca"),
        ("Textiles Kappa", "555-1009", "Av. Tecnológico 120, Metepec"),
        ("Electrónica Theta", "555-1010", "Circuito Exterior 40, Naucalpan"),
    ]
    cur.executemany("INSERT INTO clientes (nombre, contacto, direccion) VALUES (?,?,?)", clientes)

    vehiculos = [
        ("TOL-101-A", "Nissan NP300", 1500, "Activo"),
        ("TOL-102-A", "Ford Transit", 2000, "Activo"),
        ("TOL-103-A", "Isuzu NPR", 3500, "Activo"),
        ("TOL-104-A", "Chevrolet 3500", 2800, "Mantenimiento"),
        ("TOL-105-A", "Nissan Urvan", 1200, "Activo"),
        ("TOL-106-A", "Freightliner M2", 5000, "Activo"),
        ("TOL-107-A", "Hino 300", 3000, "Activo"),
        ("TOL-108-A", "Ford F-350", 2500, "Mantenimiento"),
    ]
    cur.executemany(
        "INSERT INTO vehiculos (placas, modelo, capacidad_kg, estatus) VALUES (?,?,?,?)", vehiculos
    )

    operadores = [
        ("Juan Pérez", "LIC-001", "722-111-0001"),
        ("María López", "LIC-002", "722-111-0002"),
        ("Carlos Ramírez", "LIC-003", "722-111-0003"),
        ("Ana Torres", "LIC-004", "722-111-0004"),
        ("Luis Hernández", "LIC-005", "722-111-0005"),
        ("Sofía Jiménez", "LIC-006", "722-111-0006"),
    ]
    cur.executemany("INSERT INTO operadores (nombre, licencia, telefono) VALUES (?,?,?)", operadores)

    rutas = [
        ("Toluca", "CDMX", 65),
        ("Toluca", "Querétaro", 160),
        ("Toluca", "Puebla", 190),
        ("Toluca", "Cuernavaca", 95),
        ("CDMX", "Puebla", 130),
        ("Toluca", "Metepec", 12),
        ("Toluca", "Naucalpan", 55),
        ("CDMX", "Querétaro", 210),
        ("Toluca", "Morelia", 250),
        ("CDMX", "Pachuca", 105),
    ]
    cur.executemany("INSERT INTO rutas (origen, destino, distancia_km) VALUES (?,?,?)", rutas)

    conn.commit()

    # ------------------------------------------------------------------
    # Entregas simuladas (últimos 90 días) — suficientes por ruta para
    # que las métricas de los modelos (regresión, clasificación,
    # clustering) sean representativas.
    # ------------------------------------------------------------------
    hoy = datetime.now()
    rutas_dist = {i + 1: rutas[i][2] for i in range(len(rutas))}

    for i in range(400):
        fecha = hoy - timedelta(days=random.randint(0, 90))
        cliente_id = random.randint(1, len(clientes))
        vehiculo_id = random.randint(1, len(vehiculos))
        operador_id = random.randint(1, len(operadores))
        ruta_id = random.randint(1, len(rutas))
        distancia = rutas_dist[ruta_id]

        hora_salida = f"{random.randint(6,16):02d}:{random.choice(['00','15','30','45'])}"

        # Tiempo estimado realista: proporcional a la distancia (~1.1 min/km)
        # más una parte fija de carga/descarga.
        estimado = round(distancia * random.uniform(0.9, 1.3) + random.uniform(15, 40), 1)

        # La probabilidad de retraso aumenta con la distancia y con salidas
        # en horas pico (7-9 y 13-15).
        hora_num = int(hora_salida[:2])
        prob_retraso = 0.15 + (distancia / 500) * 0.35
        if hora_num in (7, 8, 13, 14):
            prob_retraso += 0.15
        prob_retraso = min(prob_retraso, 0.85)

        r = random.random()
        if r < 0.05:
            estatus = "Cancelado"
            real = None
        elif r < 0.05 + prob_retraso:
            estatus = "Retrasado"
            real = round(estimado + random.uniform(20, 100), 1)
        else:
            estatus = "Entregado"
            real = round(estimado + random.uniform(-15, 15), 1)

        cur.execute(
            """INSERT INTO entregas
               (cliente_id, vehiculo_id, operador_id, ruta_id, fecha, hora_salida,
                minutos_estimados, minutos_reales, estatus)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (cliente_id, vehiculo_id, operador_id, ruta_id, fecha.strftime("%Y-%m-%d"),
             hora_salida, estimado, real, estatus),
        )

    # Combustible
    for i in range(150):
        fecha = hoy - timedelta(days=random.randint(0, 90))
        vehiculo_id = random.randint(1, len(vehiculos))
        litros = round(random.uniform(20, 80), 1)
        costo = round(litros * random.uniform(22, 25), 2)
        km = round(random.uniform(50, 300), 1)
        cur.execute(
            """INSERT INTO combustible (vehiculo_id, fecha, litros, costo, km_recorridos)
               VALUES (?,?,?,?,?)""",
            (vehiculo_id, fecha.strftime("%Y-%m-%d"), litros, costo, km),
        )

    # Mantenimiento
    tipos = ["Preventivo", "Correctivo"]
    for i in range(45):
        fecha = hoy - timedelta(days=random.randint(0, 120))
        vehiculo_id = random.randint(1, len(vehiculos))
        tipo = random.choice(tipos)
        costo = round(random.uniform(500, 6000), 2)
        cur.execute(
            """INSERT INTO mantenimiento (vehiculo_id, fecha, tipo, costo, descripcion)
               VALUES (?,?,?,?,?)""",
            (vehiculo_id, fecha.strftime("%Y-%m-%d"), tipo, costo,
             "Servicio " + tipo.lower() + " de rutina"),
        )

    conn.commit()


def inicializar():
    conn = get_connection()
    crear_tablas(conn)
    ensure_usuarios_table(conn)
    cargar_datos_ejemplo(conn)
    crear_usuario_default(conn)
    return conn


def ensure_usuarios_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT,
            rol TEXT DEFAULT 'operador',
            activo INTEGER DEFAULT 1,
            fecha_creacion TEXT
        )
    """)
    conn.commit()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def crear_usuario_default(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] > 0:
        return
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuarios_default = [
        ("admin", hash_password("admin123"), "Administrador", "admin", ahora),
        ("operador", hash_password("operador123"), "Operador General", "operador", ahora),
    ]
    cur.executemany(
        "INSERT INTO usuarios (usuario, password_hash, nombre_completo, rol, fecha_creacion) "
        "VALUES (?,?,?,?,?)", usuarios_default
    )
    conn.commit()


def verificar_usuario(usuario, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, usuario, nombre_completo, rol FROM usuarios "
                    "WHERE usuario=? AND password_hash=? AND activo=1",
                    (usuario, hash_password(password)))
        resultado = cur.fetchone()
    except Exception:
        resultado = None
    finally:
        conn.close()
    if resultado:
        return {"id": resultado[0], "usuario": resultado[1],
                "nombre": resultado[2], "rol": resultado[3]}
    return None


def crear_usuario(usuario, password, nombre_completo):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios (usuario, password_hash, nombre_completo, rol, fecha_creacion) "
                    "VALUES (?,?,?,?,?)",
                    (usuario, hash_password(password), nombre_completo, "operador",
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    inicializar()
    print("Base de datos creada/actualizada en", DB_PATH)
