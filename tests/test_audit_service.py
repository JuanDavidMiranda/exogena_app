import pandas as pd

from Service.audit_service import preparar_df_para_auditoria


def test_preparar_df_para_auditoria_usa_columnas_seleccionadas():
    df = pd.DataFrame(
        {
            "NIT": ["900123", "900124"],
            "Base": [1000, 2000],
        }
    )

    resultado = preparar_df_para_auditoria(
        df,
        "DIAN",
        col_clave="NIT",
        col_monto="Base",
    )

    assert "__clave__" in resultado.columns
    assert "__monto__" in resultado.columns
    assert resultado["__clave__"].tolist() == ["900123", "900124"]
    assert resultado["__monto__"].tolist() == [1000, 2000]
