from transacciones_service import actualizar_rol_usuario, get_connection

# Pon aquí el mismo usuario exacto que acabas de registrar en la interfaz
USUARIO_REAL = "superadmin" 

conn = get_connection()
cur = conn.cursor()

# Forzamos la actualización del rol en la base de datos
cur.execute("""
    UPDATE usuarios
    SET rol = 'superadministrador'
    WHERE username = ?
""", (USUARIO_REAL,))

conn.commit()
conn.close()

print(f"¡El usuario '{USUARIO_REAL}' ahora es superadministrador oficialmente!")