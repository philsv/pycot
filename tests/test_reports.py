import pandas as pd
import pytest

from pycot import reports


@pytest.mark.parametrize(
    "report_type,contract_name",
    [
        (
            "legacy_fut",
            (
                "FED FUNDS - CHICAGO BOARD OF TRADE",
                "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE",
            ),
        ),
    ],
)
def test_legacy_report(report_type, contract_name):
    df = reports.legacy_report(report_type, contract_name)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "report_type,contract_name",
    [
        (
            "disaggregated_futopt",
            (
                "BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE",
                "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE",
            ),
        ),
    ],
)
def test_disaggregated_report(report_type, contract_name):
    df = reports.disaggregated_report(report_type, contract_name)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "report_type,contract_name",
    [
        (
            "traders_in_financial_futures_fut",
            (
                "UST 10Y NOTE - CHICAGO BOARD OF TRADE",
                "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",
                "10 YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE",
            ),
        ),
    ],
)
def test_financial_report(report_type, contract_name):
    df = reports.financial_report(report_type, contract_name)
    assert isinstance(df, pd.DataFrame)
