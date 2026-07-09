from pathlib import Path
from datetime import datetime
import pandas as pd


LOG_DIR = Path("Data")
LOG_FILE = LOG_DIR / "historial_procesos.csv"


COLUMNAS_LOG = [
    "fecha_hora",
    "usuario",
    "rol",
    "modulo",
    "accion",
    "archivo",
    "formato",
    "resultado",
    "detalle"
]


def inicializar_log():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not LOG_FILE.exists():
        df = pd.DataFrame(columns=COLUMNAS_LOG)
        df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def registrar_evento(
    usuario="Sin usuario",
    rol="usuario",
    modulo="Sin módulo",
    accion="Sin acción",
    archivo="",
    formato="",
    resultado="OK",
    detalle=""
):
    inicializar_log()

    nuevo_registro = {
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": usuario,
        "rol": rol,
        "modulo": modulo,
        "accion": accion,
        "archivo": archivo,
        "formato": formato,
        "resultado": resultado,
        "detalle": detalle
    }

    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def obtener_historial():
    inicializar_log()
    df = pd.read_csv(LOG_FILE)

    if df.empty:
        return df

    return df.sort_values(by="fecha_hora", ascending=False)