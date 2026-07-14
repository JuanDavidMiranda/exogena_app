from pathlib import Path
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================================
# RUTA DB
# ==========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Creamos la carpeta 'data' de forma segura dentro del proyecto
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"
# ==========================================================
# CONEXIÓN
# ==========================================================
def get_connection():
    return sqlite3.connect(str(DB_PATH))


# ==========================================================
# INIT DB
# ==========================================================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # --------------------------
    # Tabla usuarios (Actualizada con password_hash)
    # --------------------------
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

    # --------------------------
    # Tabla transacciones
    # --------------------------
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

    cur.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios (username, nombre, password_hash, rol, activo, creado_en)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            nombre,
            password_hash,
            rol or "usuario",
            1,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

    conn.close()


def obtener_usuario(username: str):
    conn = get_connection()
    cur = conn.cursor()

    # Agregamos password_hash a la consulta select
    cur.execute("""
        SELECT id, username, nombre, rol, activo, creado_en, password_hash
        FROM usuarios
        WHERE username = ?
    """, (username,))
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
        "password_hash": row[6], # Guardamos el hash para validarlo en el login
    }

def actualizar_rol_usuario(username_a_cambiar: str, nuevo_rol: str, username_operador: str):
    """
    Actualiza el rol de un usuario. 
    Solo un 'superadministrador' puede promover a alguien a 'administrador' o 'superadministrador'.
    """
    conn = get_connection()
    cur = conn.cursor()

    # 1. Obtener el rol de la persona que está ejecutando la acción
    cur.execute("SELECT rol FROM usuarios WHERE username = ?", (username_operador,))
    row_operador = cur.fetchone()
    rol_operador = row_operador[0] if row_operador else None

    # 2. Validar restricción: Si el nuevo rol es 'administrador' o 'superadministrador',
    # el operador OBLIGATORIAMENTE debe ser 'superadministrador'.
    if nuevo_rol in ["administrador", "superadministrador"]:
        if rol_operador != "superadministrador":
            conn.close()
            raise PermissionError(
                f"Acción denegada: El usuario '{username_operador}' no tiene permisos de "
                f"superadministrador para asignar el rol '{nuevo_rol}'."
            )

    # 3. Si pasa la validación, se actualiza en la base de datos
    cur.execute("""
        UPDATE usuarios
        SET rol = ?
        WHERE username = ?
    """, (nuevo_rol, username_a_cambiar))

    conn.commit()
    conn.close()

def listar_usuarios():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            username AS "username",
            nombre AS "Nombre",
            rol AS "Rol",
            activo AS "Activo",
            creado_en AS "Creado en"
        FROM usuarios
        ORDER BY creado_en DESC
    """, conn)
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

    cur.execute("""
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
    """, (
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
    ))

    conn.commit()
    conn.close()


def listar_transacciones(usuario=None, modulo=None, estado=None):
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

    query += " ORDER BY fecha DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


# ==========================================================
# PANEL ADMIN
# ==========================================================
def obtener_resumen_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transacciones")
    transacciones = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Diagnóstico'")
    diagnosticos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Auditoría'")
    auditorias = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transacciones WHERE modulo = 'Generar XML'")
    xml_generados = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM transacciones WHERE estado = 'ERROR'")
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


def obtener_uso_por_modulo():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            modulo AS "Módulo",
            COUNT(*) AS "Cantidad"
        FROM transacciones
        GROUP BY modulo
        ORDER BY COUNT(*) DESC
    """, conn)
    conn.close()
    return df


def obtener_errores_por_modulo():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            modulo AS "Módulo",
            COUNT(*) AS "Errores"
        FROM transacciones
        WHERE estado = 'ERROR'
        GROUP BY modulo
        ORDER BY COUNT(*) DESC
    """, conn)
    conn.close()
    return df