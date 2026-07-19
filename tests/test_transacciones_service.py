import pandas as pd

from Service import transacciones_service as ts


def test_listar_transacciones_filtra_por_usuario(monkeypatch, tmp_path):
    db_path = tmp_path / "test_app.db"
    monkeypatch.setattr(ts, "DB_PATH", db_path)

    ts.init_db()
    ts.registrar_transaccion(
        modulo="Diagnóstico",
        accion="Subir archivo",
        estado="OK",
        detalle="Proceso 1",
        username="ana",
        nombre_usuario="Ana",
        rol="usuario",
    )
    ts.registrar_transaccion(
        modulo="Auditoría",
        accion="Comparar archivos",
        estado="ERROR",
        detalle="Proceso 2",
        username="juan",
        nombre_usuario="Juan",
        rol="usuario",
    )

    historial = ts.listar_transacciones(usuario="ana")

    assert isinstance(historial, pd.DataFrame)
    assert len(historial) == 1
    assert historial.iloc[0]["Usuario"] == "ana"
    assert historial.iloc[0]["Detalle"] == "Proceso 1"


def test_prepare_sql_usa_percent_s_en_postgres(monkeypatch):
    monkeypatch.setenv("EXOGENA_DB_BACKEND", "postgres")
    monkeypatch.setattr(ts, "DB_BACKEND", "postgres", raising=False)

    sql = ts.prepare_sql("SELECT id FROM usuarios WHERE username = ?")

    assert sql == "SELECT id FROM usuarios WHERE username = %s"
