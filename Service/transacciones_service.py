from pathlib import Path
import os
import sqlite3
import pandas as pd
from datetime import datetime

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


if st is not None:
    cache_data = st.cache_data(ttl=20)
else:
    def cache_data(func):
        return func

try:
    import psycopg2
except Exception:  # pragma: no cover
    psycopg2 = None

# ==========================================================
# RUTA DB
# ==========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("EXOGENA_DB_PATH", DATA_DIR / "app.db"))
DB_PATH = DB_PATH if DB_PATH.is_absolute() else (BASE_DIR / DB_PATH)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DB_URL = os.getenv("EXOGENA_DB_URL", "").strip()
DB_HOST = os.getenv("EXOGENA_DB_HOST", "").strip()
DB_PORT = os.getenv("EXOGENA_DB_PORT", "5432").strip()
DB_NAME = os.getenv("EXOGENA_DB_NAME", "").strip()
DB_USER = os.getenv("EXOGENA_DB_USER", "").strip()
DB_PASSWORD = os.getenv("EXOGENA_DB_PASSWORD", "").strip()


def get_db_backend() -> str:
    backend = os.getenv("EXOGENA_DB_BACKEND", "sqlite").strip().lower()
    if st is not None:
        try:
            secrets_db = st.secrets.get("db", {})
            backend_secret = str(secrets_db.get("EXOGENA_DB_BACKEND", backend)).strip().lower()
            if backend_secret:
                backend = backend_secret
        except Exception:
            pass
    return backend


def get_db_url() -> str:
    url = os.getenv("EXOGENA_DB_URL", "").strip()
    if st is not None:
        try:
            secrets_db = st.secrets.get("db", {})
            url_secret = str(secrets_db.get("EXOGENA_DB_URL", url)).strip()
            if url_secret:
                url = url_secret
        except Exception:
            pass
    return url

# ==========================================================
# FUNCIONES DE ADAPTACIÓN SQL
# ==========================================================
def prepare_sql(query: str) -> str:
    if get_db_backend() == "postgres":
        return query.replace("?", "%s")
    return query


# ==========================================================
# CONEXIÓN
# ==========================================================
def get_connection():
    backend = get_db_backend()

    if backend == "postgres":
        if psycopg2 is None:
            raise RuntimeError("psycopg2 no está instalado. Agrega psycopg2-binary al proyecto.")

        db_url = get_db_url()
        if not db_url:
            if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
                raise RuntimeError(
                    "Para PostgreSQL necesitas EXOGENA_DB_URL o las variables "
                    "EXOGENA_DB_HOST, EXOGENA_DB_NAME, EXOGENA_DB_USER y EXOGENA_DB_PASSWORD."
                )
            db_url = (
                f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
                f"user={DB_USER} password={DB_PASSWORD}"
            )
        return psycopg2.connect(db_url)

    return sqlite3.connect(str(DB_PATH))


# ==========================================================
# INIT DB
# ==========================================================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    if get_db_backend() == "postgres":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGSERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                nombre TEXT,
                password_hash TEXT,
                rol TEXT DEFAULT 'usuario',
                activo INTEGER DEFAULT 1,
                creado_en TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id BIGSERIAL PRIMARY KEY,
                username TEXT,
                nombre_usuario TEXT,
                rol TEXT,
                modulo TEXT NOT NULL,
                accion TEXT NOT NULL,
                estado TEXT NOT NULL,
                detalle TEXT,
                archivo_1 TEXT,
                archivo_2 TEXT,
                fecha TEXT NOT NULL
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                nombre TEXT,
                password_hash TEXT,
                rol TEXT DEFAULT 'usuario',
                activo INTEGER DEFAULT 1,
                creado_en TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                nombre_usuario TEXT,
                rol TEXT,
                modulo TEXT NOT NULL,
                accion TEXT NOT NULL,
                estado TEXT NOT NULL,
                detalle TEXT,
                archivo_1 TEXT,
                archivo_2 TEXT,
                fecha TEXT NOT NULL
            )
        """)

    conn.commit()
    conn.close()


# ==========================================================
# USUARIOS
# ==========================================================
def registrar_usuario_si_no_existe(username: str, nombre: str = "", password_hash: str = "", rol: str = "usuario"):
    if not username:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(prepare_sql("SELECT id FROM usuarios WHERE username = ?"), (username,))
    existe = cur.fetchone()

    if not existe:
        cur.execute(
            prepare_sql("""
                INSERT INTO usuarios (username, nombre, password_hash, rol, activo, creado_en)
                VALUES (?, ?, ?, ?, ?, ?)
            """),
            (
                username,
                nombre,
                password_hash,
                rol or "usuario",
                1,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()

    conn.close()


def obtener_usuario(username: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        prepare_sql("""
            SELECT id, username, nombre, rol, activo, creado_en, password_hash
            FROM usuarios
            WHERE username = ?
        """),
        (username,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "nombre": row[2],
        "rol": row[3],
        "activo": row[4],
        "creado_en": row[5],
        "password_hash": row[6],
    }


def actualizar_rol_usuario(username_a_cambiar: str, nuevo_rol: str, username_operador: str):
    """
    Actualiza el rol de un usuario.
    Solo un 'superadministrador' puede promover a alguien a 'administrador' o 'superadministrador'.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(prepare_sql("SELECT rol FROM usuarios WHERE username = ?"), (username_operador,))
    row_operador = cur.fetchone()
    rol_operador = row_operador[0] if row_operador else None

    if nuevo_rol in ["administrador", "superadministrador"]:
        if rol_operador != "superadministrador":
            conn.close()
            raise PermissionError(
                f"Acción denegada: El usuario '{username_operador}' no tiene permisos de "
                f"superadministrador para asignar el rol '{nuevo_rol}'."
            )

    cur.execute(
        prepare_sql("""
            UPDATE usuarios
            SET rol = ?
            WHERE username = ?
        """),
        (nuevo_rol, username_a_cambiar)
    )

    conn.commit()
    conn.close()


@cache_data
def listar_usuarios():
    conn = get_connection()
    df = pd.read_sql_query(
        prepare_sql("""
            SELECT
                username AS "username",
                nombre AS "Nombre",
                rol AS "Rol",
                activo AS "Activo",
                creado_en AS "Creado en"
            FROM usuarios
            ORDER BY creado_en DESC
        """),
        conn
    )
    conn.close()
    return df


# ==========================================================
# TRANSACCIONES
# ==========================================================
def registrar_transaccion(
    modulo: str,
    accion: str,
    estado: str,
    detalle: str = "",
    archivo_1: str = "",
    archivo_2: str = "",
    username: str = "",
    nombre_usuario: str = "",
    rol: str = "usuario"
):
    """
    Registra una transacción del sistema.
    Compatible con Diagnóstico / Auditoría / XML.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        prepare_sql("""
            INSERT INTO transacciones (
                username,
                nombre_usuario,
                rol,
                modulo,
                accion,
                estado,
                detalle,
                archivo_1,
                archivo_2,
                fecha
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """),
        (
            username,
            nombre_usuario,
            rol,
            modulo,
            accion,
            estado,
            detalle,
            archivo_1,
            archivo_2,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


@cache_data
def listar_transacciones(usuario=None, modulo=None, estado=None, fecha_inicio=None, fecha_fin=None, archivo=None):
    conn = get_connection()

    query = """
        SELECT
            fecha AS "Fecha",
            username AS "Usuario",
            nombre_usuario AS "Nombre",
            rol AS "Rol",
            modulo AS "Módulo",
            accion AS "Acción",
            estado AS "Estado",
            detalle AS "Detalle",
            archivo_1 AS "Archivo 1",
            archivo_2 AS "Archivo 2"
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

    if fecha_inicio:
        query += " AND date(fecha) >= date(?)"
        params.append(fecha_inicio)

    if fecha_fin:
        query += " AND date(fecha) <= date(?)"
        params.append(fecha_fin)

    if archivo:
        query += " AND (archivo_1 LIKE ? OR archivo_2 LIKE ?)"
        params.extend([f"%{archivo}%", f"%{archivo}%"])

    query += " ORDER BY fecha DESC"

    df = pd.read_sql_query(prepare_sql(query), conn, params=params)
    conn.close()
    return df


# ==========================================================
# PANEL ADMIN
# ==========================================================
@cache_data
def obtener_resumen_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(prepare_sql("SELECT COUNT(*) FROM usuarios"))
    usuarios = cur.fetchone()[0]

    cur.execute(prepare_sql("SELECT COUNT(*) FROM transacciones"))
    transacciones = cur.fetchone()[0]

    cur.execute(prepare_sql("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Diagnóstico'"))
    diagnosticos = cur.fetchone()[0]

    cur.execute(prepare_sql("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Auditoría'"))
    auditorias = cur.fetchone()[0]

    cur.execute(prepare_sql("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Generar XML'"))
    xml_generados = cur.fetchone()[0]

    cur.execute(prepare_sql("SELECT COUNT(*) FROM transacciones WHERE estado = 'ERROR'"))
    errores = cur.fetchone()[0]

    conn.close()

    return {
        "usuarios": usuarios,
        "transacciones": transacciones,
        "diagnosticos": diagnosticos,
        "auditorias": auditorias,
        "xml_generados": xml_generados,
        "errores": errores,
    }


@cache_data
def obtener_uso_por_modulo():
    conn = get_connection()
    df = pd.read_sql_query(
        prepare_sql("""
            SELECT
                modulo AS "Módulo",
                COUNT(*) AS "Cantidad"
            FROM transacciones
            GROUP BY modulo
            ORDER BY COUNT(*) DESC
        """),
        conn
    )
    conn.close()
    return df


@cache_data
def obtener_errores_por_modulo():
    conn = get_connection()
    df = pd.read_sql_query(
        prepare_sql("""
            SELECT
                modulo AS "Módulo",
                COUNT(*) AS "Errores"
            FROM transacciones
            WHERE estado = 'ERROR'
            GROUP BY modulo
            ORDER BY COUNT(*) DESC
        """),
        conn
    )
    conn.close()
    return df