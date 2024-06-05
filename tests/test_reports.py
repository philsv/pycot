import time

import pandas as pd
import pytest

from pycot.reports import CommitmentsOfTraders


@pytest.mark.parametrize(
    "report_type, contract_name",
    [
        (
            "legacy_fut",
            (
                "FED FUNDS - CHICAGO BOARD OF TRADE",
                "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE",
            ),
        ),
        (
            "disaggregated_futopt",
            (
                "BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE",
                "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE",
            ),
        ),
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
def test_individual_reports(report_type, contract_name):
    cot = CommitmentsOfTraders(report_type)
    df = cot.report(contract_name)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "report_type, contract_1, contract_2",
    [
        (
            "legacy_fut",
            ("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"),
            ("BBG COMMODITY - CHICAGO BOARD OF TRADE", "BLOOMBERG COMMODITY INDEX - CHICAGO BOARD OF TRADE"),
        ),
    ],
)
def test_cot_report(report_type, contract_1, contract_2):    
    start_time_1 = time.perf_counter()
    cot =  CommitmentsOfTraders(report_type)
    df_1 =  cot.report(contract_1)
    end_time_1 = time.perf_counter() - start_time_1

    start_time_2 = time.perf_counter()
    df_2 =  cot.report(contract_2)
    end_time_2 = time.perf_counter() - start_time_2
    assert end_time_1 > end_time_2
    assert isinstance(df_1, pd.DataFrame)
    assert isinstance(df_2, pd.DataFrame)
