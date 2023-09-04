from functools import lru_cache

import numpy as np
import pandas as pd
from exceptions import InvalidReportType
from extract_report_data import COT, get_formating_data


def format_dataframe(
    data: pd.DataFrame,
    names: list,
    columns: list,
) -> pd.DataFrame:
    """
    Helper function to format the data retrieved from the CFTC website.
    """
    df = data.reindex(columns=columns)  # Limit the columns to the ones we need (please adjust to your liking in format_columns.json)
    df.rename(columns=dict(zip(columns, names)), inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index(["Date", "Contract Name"], inplace=True)
    df.replace(".", np.nan, inplace=True)
    df = df.astype(float)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    return df


def get_contract(
    df: pd.DataFrame,
    contract_name: str | tuple,
) -> pd.DataFrame:
    """
    Retrieves the Commitment of Traders Reports data for a specific contract or list of contracts.
    """
    if isinstance(contract_name, str):
        return df[df["Contract Name"] == contract_name]

    data = [df[df["Contract Name"] == contract] for contract in contract_name if contract in df["Contract Name"].unique()]
    return pd.concat(data)


@lru_cache
def legacy_report(
    report_type: str,
    contract_name: str | tuple | None = None,
) -> pd.DataFrame:
    """ "
    Retrieves the legacy Commitment of Traders Reports data.

    Args:
        report_type (str): The type of cot report to extract.

    Returns:
        A pandas DataFrame with the legacy futures Commitment of Traders data.
        
    Example:
        >>> from pycot import legacy_report
        >>> legacy_report("legacy_fut", ("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"))
    """
    if report_type not in ["legacy_fut", "legacy_futopt"]:
        raise InvalidReportType("Please use one of the following report types: ['legacy_fut', 'legacy_futopt']")

    cot = COT(report_type)
    data = cot.get_reports()
    names, columns = zip(*get_formating_data()["legacy_format"].items())
    df = format_dataframe(data, names, columns)
    df["Net Position, Large Spec"] = df["Noncommercial Long"] - df["Noncommercial Short"]
    df["Net Change, Large Spec"] = df["Noncommercial Long, Change"] - df["Noncommercial Short, Change"]
    df["Net % of OI, Large Spec"] = df["Noncommercial Long, % of OI"] - df["Noncommercial Short, % of OI"]
    df["Noncommercial Short"] = df["Noncommercial Short"] * -1
    df = df.sort_index()[::-1]
    return get_contract(df, contract_name) if contract_name else df


@lru_cache
def disaggregated_report(
    report_type: str,
    contract_name: str | tuple | None = None,
) -> pd.DataFrame:
    """
    Adjusted disaggregated futures and options report data.

    Returns:
        A pandas DataFrame with the disaggregated futures and options report.
        
    Example:
        >>> from pycot import disaggregated_report
        >>> disaggregated_report("disaggregated_fut", ("BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE", "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE"))
    """
    if report_type not in ["disaggregated_fut", "disaggregated_futopt"]:
        raise InvalidReportType("Please use one of the following report types: ['disaggregated_fut', 'disaggregated_futopt']")

    cot = COT(report_type)
    data = cot.get_reports()
    names, columns = zip(*get_formating_data()["disaggregated_format"].items())
    
    df = format_dataframe(data, names, columns)

    df["Net Position Other Rept"] = df["Other Reportable Long"] - df["Other Reportable Short"]
    df["Net Change Other Rept"] = df["Other Reportable Long, Change"] - df["Other Reportable Short, Change"]
    df["Net % of OI Other Rept"] = df["Other Reportable Long, % of OI"] - df["Other Reportable Short, % of OI"]
    df["Other Reportable Short"] = df["Other Reportable Short"] * -1

    df["Net Position Managed Money"] = df["Managed Money Long"] - df["Managed Money Short"]
    df["Net Change Managed Money"] = df["Managed Money Long, Change"] - df["Managed Money Short, Change"]
    df["Net % of OI Managed Money"] = df["Managed Money Long, % of OI"] - df["Managed Money Short, % of OI"]
    df["Managed Money Short"] = df["Managed Money Short"] * -1
    df = df.sort_index()[::-1]
    return get_contract(df, contract_name) if contract_name else df


@lru_cache
def financial_report(
    report_type: str,
    contract_name: str | tuple | None = None,
) -> pd.DataFrame:
    """
    Adjusted financial futures and options report data.

    Returns:
        A pandas DataFrame with the financial futures and options report.
        
    Example:
        >>> from pycot import financial_report
        >>> financial_report("financial_fut", ("UST 10Y NOTE - CHICAGO BOARD OF TRADE", "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE", "10 YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"))
    """
    if report_type not in ["traders_in_financial_futures_fut", "traders_in_financial_futures_futopt"]:
        raise InvalidReportType("Please use one of the following report types: ['traders_in_financial_futures_fut', 'traders_in_financial_futures_futopt']")
    
    cot = COT(report_type)
    data = cot.get_reports()
    names, columns = zip(*get_formating_data()["traders_in_financial_futures_format"].items())
    
    df = format_dataframe(data, names, columns)
    df["Net Position Asset Mgr"] = df["Asset Manager Long"] - df["Asset Manager Short"]
    df["Net Change Asset Mgr"] = df["Asset Manager Long, Change"] - df["Asset Manager Short, Change"]
    df["Net % of OI Asset Mgr"] = df["Asset Manager Long, % of OI"] - df["Asset Manager Short, % of OI"]
    df["Asset Manager Short"] = df["Asset Manager Short"] * -1

    df["Net Position Lev Money"] = df["Leveraged Money Long"] - df["Leveraged Money Short"]
    df["Net Change Lev Money"] = df["Leveraged Money Long, Change"] - df["Leveraged Money Short, Change"]
    df["Net % of OI Lev Money"] = df["Leveraged Money Long, % of OI"] - df["Leveraged Money Short, % of OI"]
    df["Leveraged Money Short"] = df["Leveraged Money Short"] * -1
    df = df.sort_index()[::-1]
    return get_contract(df, contract_name) if contract_name else df


if __name__ == "__main__":
    contract_name = ("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE")
    df = legacy_report("legacy_fut", contract_name)
    print(df)
    print(df.info())
