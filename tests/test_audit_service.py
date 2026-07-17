import pandas as pd

from Service.audit_service import (
    aplicar_formato_monedas,
    preparar_df_para_auditoria,
)


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


def test_aplicar_formato_monedas_formatea_columnas_de_resultado():
    df = pd.DataFrame(
        {
            "Valor DIAN": [1000, 2500.5],
            "Valor Novasoft": [500, None],
            "Diferencia": [500, -1999.5],
        }
    )

    resultado = aplicar_formato_monedas(
        df,
        ["Valor DIAN", "Valor Novasoft", "Diferencia"],
    )

    assert resultado.loc[0, "Valor DIAN"] == "$1,000.00"
    assert resultado.loc[1, "Valor DIAN"] == "$2,500.50"
    assert resultado.loc[0, "Valor Novasoft"] == "$500.00"
    assert resultado.loc[1, "Valor Novasoft"] == "$0.00"
    assert resultado.loc[1, "Diferencia"] == "-$1,999.50"
