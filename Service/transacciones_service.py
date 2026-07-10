import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

# ============================================================
# Configuración de la base de datos
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


# ============================================================
# Helpers de conexión
# ============================================================
def _asegurar_directorio_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    _asegurar_directorio_data()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Inicialización de la base
# ============================================================
def init_db():
    """
    Crea las tablas base del sistema si no existen.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            nombre TEXT,
            rol TEXT NOT NULL DEFAULT 'usuario',
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            username TEXT,
            nombre_usuario TEXT,
            rol TEXT,
            modulo TEXT NOT NULL,
            accion TEXT NOT NULL,
            estado TEXT NOT NULL,
            detalle TEXT,
            archivo_1 TEXT,
            archivo_2 TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# Usuarios
# ============================================================
def registrar_usuario_si_no_existe(username: str, nombre: str = "", rol: str = "usuario"):
    """
    Inserta el usuario si no existe. Si ya existe, no falla.
    """
    if not username:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios (username, nombre, rol, activo, fecha_creacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            nombre or username,
            rol or "usuario",
            1,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

    conn.close()


def obtener_usuario(username: str):
    if not username:
        return None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM usuarios
        WHERE username = ?
    """, (username,))
    row = cur.fetchone()
    conn.close()

    return dict(row) if row else None


def actualizar_rol_usuario(username: str, nuevo_rol: str):
    """
    Cambia el rol de un usuario.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE usuarios
        SET rol = ?
        WHERE username = ?
    """, (nuevo_rol, username))

    conn.commit()
    conn.close()


def listar_usuarios() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT id, username, nombre, rol, activo, fecha_creacion
        FROM usuarios
        ORDER BY nombre ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ============================================================
# Transacciones
# ============================================================
def registrar_transaccion(
    modulo: str,
    accion: str,
    estado: str,
    detalle: str = "",
    archivo_1: str = "",
    archivo_2: str = "",
    username: str = "",
    nombre_usuario: str = "",
    rol: str = ""
):
    """
    Registra un evento / transacción del sistema.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transacciones (
            fecha,
            username,
            nombre_usuario,
            rol,
            modulo,
            accion,
            estado,
            detalle,
            archivo_1,
            archivo_2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        username,
        nombre_usuario,
        rol,
        modulo,
        accion,
        estado,
        detalle,
        archivo_1,
        archivo_2
    ))

    conn.commit()
    conn.close()


def listar_transacciones(
    usuario: str | None = None,
    modulo: str | None = None,
    estado: str | None = None
) -> pd.DataFrame:
    """
    Devuelve el historial de transacciones con filtros opcionales.
    """
    conn = get_connection()

    query = """
        SELECT
            id,
            fecha,
            username,
            nombre_usuario,
            rol,
            modulo,
            accion,
            estado,
            detalle,
            archivo_1,
            archivo_2
        FROM transacciones
        WHERE 1=1
    """
    params = []

    if usuario:
        query += " AND username = ?"
        params.append(usuario)

    if modulo:
        query += " AND modulo = ?"
        params.append(modulo)

    if estado:
        query += " AND estado = ?"
        params.append(estado)

    query += " ORDER BY fecha DESC, id DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


# ============================================================
# Métricas admin
# ============================================================
def obtener_resumen_admin() -> dict:
    """
    Devuelve KPIs generales para el panel administrativo.
    """
    conn = get_connection()
    cur = conn.cursor()

    def scalar(query: str):
        cur.execute(query)
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0

    resumen = {
        "usuarios": scalar("SELECT COUNT(*) FROM usuarios WHERE activo = 1"),
        "transacciones": scalar("SELECT COUNT(*) FROM transacciones"),
        "diagnosticos": scalar("""
            SELECT COUNT(*)
            FROM transacciones
            WHERE modulo = 'Diagnóstico'
        """),
        "auditorias": scalar("""
            SELECT COUNT(*)
            FROM transacciones
            WHERE modulo = 'Auditoría'
        """),
        "xml_generados": scalar("""
            SELECT COUNT(*)
            FROM transacciones
            WHERE modulo = 'Generar XML'
        """),
        "errores": scalar("""
            SELECT COUNT(*)
            FROM transacciones
            WHERE estado = 'ERROR'
        """)
    }

    conn.close()
    return resumen


def obtener_uso_por_modulo() -> pd.DataFrame:
    """
    Agrupa cantidad de transacciones por módulo.
    """
    conn = get_connection()
    query = """
        SELECT modulo, COUNT(*) AS cantidad
        FROM transacciones
        GROUP BY modulo
        ORDER BY cantidad DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def obtener_errores_por_modulo() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT modulo, COUNT(*) AS cantidad
        FROM transacciones
        WHERE estado = 'ERROR'
        GROUP BY modulo
        ORDER BY cantidad DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df