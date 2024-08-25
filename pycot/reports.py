import logging
import os
import tempfile
import zipfile
from datetime import date
from functools import lru_cache
from typing import Union

import numpy as np
import pandas as pd
import requests

from pycot.config import settings
from pycot.exceptions import InvalidReportType

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)


def format_dataframe(
    data: pd.DataFrame,
    names: Union[list, tuple],
    columns: Union[list, tuple],
) -> pd.DataFrame:
    """Helper function to format the data retrieved from the CFTC website."""
    # Limit the columns to the ones we need (can be adjusted in format_columns.json)
    df = data.reindex(columns=columns)
    df = df.rename(columns=dict(zip(columns, names)))
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index(["Date", "Contract Name"])
    df = df.replace(".", np.nan)
    df = df.astype(float)
    df = df.reset_index()
    df = df.set_index("Date")
    return df


def get_contract(
    df: pd.DataFrame,
    contract_name: Union[str, tuple],
) -> pd.DataFrame:
    """Retrieves the Commitment of Traders Reports data for a specific contract or list of contracts."""
    if isinstance(contract_name, str):
        return df[df["Contract Name"] == contract_name]

    data = [
        df[df["Contract Name"] == contract]
        for contract in contract_name
        if contract in df["Contract Name"].unique()
    ]
    return pd.concat(data)


class CommitmentsOfTraders:
    """
    The Commodity Futures Trading Commission (Commission or CFTC) publishes the Commitments of Traders (COT) reports to help the public understand market dynamics.
    Specifically, the COT reports provide a breakdown of each Tuesdays open interest for futures and options on futures markets
    in which 20 or more traders hold positions equal to or above the reporting levels established by the CFTC.

    The COT reports are based on position data supplied by reporting firms (FCMs, clearing members, foreign brokers and exchanges).
    While the position data is supplied by reporting firms, the actual trader category or classification is based on the predominant business purpose self-reported
    by traders on the CFTC Form 40 and is subject to review by CFTC staff for reasonableness.

    CFTC staff does not know specific reasons for traders positions and hence this information does not factor in determining trader classifications.
    In practice this means, for example, that the position data for a trader classified in the `producer/merchant/processor/user` category for a particular commodity will include all of its positions in that commodity,
    regardless of whether the position is for hedging or speculation.

    More Information:
        https://www.cftc.gov/sites/default/files/idc/groups/public/@commitmentsoftraders/documents/file/executivesummaryofcotnotice.pdf


    Args:
        report_type (str): The type of cot report to extract. Can be one of the following:

            - `legacy_fut`: Legacy Disaggregated (All data broken down by exchange) Futures Only Report
            - `legacy_futopt`: Legacy Disaggregated (All data broken down by exchange) Futures & Options Combined Report
            - `disaggregated_fut`: Disaggregated (Commodity) Futures Only Report
            - `disaggregated_futopt`: Disaggregated (Commodity) Futures & Options Combined Report
            - `traders_in_financial_futures_fut`: Financial Markets (Financial) Futures Only Report
            - `traders_in_financial_futures_futopt`: Financial Markets (Financial) Futures & Options Combined Report
    """

    def __init__(
        self,
        report_type: Union[str, None] = None,
    ) -> None:
        self.report_type = report_type

    def extract_text_file_to_dataframe(
        self,
        response: requests.models.Response,
        text_file: str,
    ) -> pd.DataFrame:
        """Unzips the text file from an archive and returns a pandas DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_path = os.path.join(tmpdirname, "archive.zip")

            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmpdirname)

            extracted_file_path = os.path.join(tmpdirname, text_file)
            df = pd.read_csv(extracted_file_path, low_memory=False)
        return df

    @property
    @lru_cache
    def get_legacy_report(self) -> pd.DataFrame:
        """
        Retrieves the Commitment of Traders Report data selected by the report_type argument.

        Returns:
            A pandas DataFrame with the historical Commitment of Traders data.
        """
        report_data = settings.COT_REPORTS_DATA

        if self.report_type not in report_data.keys():
            raise InvalidReportType(
                f"Please use one of the following report types: {list(report_data.keys())}"
            )

        metadata = report_data[self.report_type]["legacy"]
        response = requests.get(metadata["url"])
        response.raise_for_status()
        return self.extract_text_file_to_dataframe(response, metadata["text_file"])

    @lru_cache
    def get_reports_by_year(
        self,
        report_year: int | None = None,
    ) -> pd.DataFrame | None:
        """
        Retrieves the Commitment of Traders Reports data by year.

        Returns:
            A pandas DataFrame with the historical Commitment of Traders data by the specified year.
        """
        report_data = settings.COT_REPORTS_DATA

        if self.report_type not in report_data.keys():
            raise InvalidReportType(
                f"Please use one of the following report types: {list(report_data.keys())}"
            )

        metadata = report_data[self.report_type]["current"]
        response = requests.get(f"{metadata['url']}{report_year}.zip")

        if response.status_code == 404:
            # Avoid non-existent data for a given year
            return None
        return self.extract_text_file_to_dataframe(response, metadata["text_file"])

    @property
    @lru_cache
    def get_reports(self) -> pd.DataFrame:
        """
        Retrieves the combined Commitment of Traders Reports data.

        Returns:
            A pandas DataFrame with the legacy and current Commitment of Traders data.
        """
        legacy_data = self.get_legacy_report
        current_data = [
            self.get_reports_by_year(year)
            for year in range(2017, date.today().year + 1)
        ]
        return pd.concat([legacy_data] + current_data, ignore_index=True)  # type: ignore

    @property
    @lru_cache
    def legacy_report(
        self,
    ) -> pd.DataFrame:
        """ "
        Retrieves the legacy Commitment of Traders Reports data.

        Args:
            report_type (str): The type of cot report to extract.
            Defaults to "legacy_futopt".

        Returns:
            A pandas DataFrame with the legacy futures Commitment of Traders data.

        Example:
            >>> from pycot.reports import CommitmentsOfTraders
            >>> cot = CommitmentsOfTraders("legacy_fut")
            >>> cot.legacy_report(("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"))
        """
        report_type = "legacy_futopt" if self.report_type is None else self.report_type

        if report_type not in ["legacy_fut", "legacy_futopt"]:
            raise InvalidReportType(
                "Please use one of the following report types: ['legacy_fut', 'legacy_futopt']"
            )

        logging.info(f"Extracting data for the {report_type} report type")
        data_df = CommitmentsOfTraders(report_type).get_reports

        if data_df.empty:
            raise ValueError(
                f"No data found for the selected report type: {report_type}"
            )

        names, columns = zip(*settings.FORMAT_COLUMNS["legacy_format"].items())
        df = format_dataframe(data_df, names, columns)

        df["Net Position, Large Spec"] = (
            df["Noncommercial Long"] - df["Noncommercial Short"]
        )
        df["Net Change, Large Spec"] = (
            df["Noncommercial Long, Change"] - df["Noncommercial Short, Change"]
        )
        df["Net % of OI, Large Spec"] = (
            df["Noncommercial Long, % of OI"] - df["Noncommercial Short, % of OI"]
        )
        df["Noncommercial Short"] = df["Noncommercial Short"] * -1
        df = df.sort_index()[::-1]
        return df

    @property
    @lru_cache
    def disaggregated_report(
        self,
    ) -> pd.DataFrame:
        """
        Adjusted disaggregated futures and options report data.

        Args:
            report_type (str): The type of cot report to extract.
            Defaults to "disaggregated_futopt".

        Returns:
            A pandas DataFrame with the disaggregated futures and options report.

        Example:
            >>> from pycot.reports import CommitmentsOfTraders
            >>> cot = CommitmentsOfTraders("disaggregated_fut")
            >>> cot.disaggregated_report(("BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE", "BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE"))
        """
        report_type = (
            "disaggregated_futopt" if self.report_type is None else self.report_type
        )

        if report_type not in ["disaggregated_fut", "disaggregated_futopt"]:
            raise InvalidReportType(
                "Please use one of the following report types: ['disaggregated_fut', 'disaggregated_futopt']"
            )

        logging.info(f"Extracting data for the {report_type} report type")
        data_df = CommitmentsOfTraders(report_type).get_reports

        if data_df.empty:
            raise ValueError(
                f"No data found for the selected report type: {report_type}"
            )

        names, columns = zip(*settings.FORMAT_COLUMNS["disaggregated_format"].items())
        df = format_dataframe(data_df, names, columns)

        df["Net Position Other Rept"] = (
            df["Other Reportable Long"] - df["Other Reportable Short"]
        )
        df["Net Change Other Rept"] = (
            df["Other Reportable Long, Change"] - df["Other Reportable Short, Change"]
        )
        df["Net % of OI Other Rept"] = (
            df["Other Reportable Long, % of OI"] - df["Other Reportable Short, % of OI"]
        )
        df["Other Reportable Short"] = df["Other Reportable Short"] * -1

        df["Net Position Managed Money"] = (
            df["Managed Money Long"] - df["Managed Money Short"]
        )
        df["Net Change Managed Money"] = (
            df["Managed Money Long, Change"] - df["Managed Money Short, Change"]
        )
        df["Net % of OI Managed Money"] = (
            df["Managed Money Long, % of OI"] - df["Managed Money Short, % of OI"]
        )
        df["Managed Money Short"] = df["Managed Money Short"] * -1
        df = df.sort_index()[::-1]
        return df

    @property
    @lru_cache
    def financial_report(
        self,
    ) -> pd.DataFrame:
        """
        Adjusted financial futures and options report data.

        Args:
            report_type (str): The type of cot report to extract.
            Defaults to "traders_in_financial_futures_futopt".

        Returns:
            A pandas DataFrame with the financial futures and options report.

        Example:
            >>> from pycot.reports import CommitmentsOfTraders
            >>> cot = CommitmentsOfTraders("financial_fut")
            >>> cot.financial_report(("UST 10Y NOTE - CHICAGO BOARD OF TRADE", "10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE", "10 YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE"))
        """
        report_type = (
            "traders_in_financial_futures_futopt"
            if self.report_type is None
            else self.report_type
        )

        if report_type not in [
            "traders_in_financial_futures_fut",
            "traders_in_financial_futures_futopt",
        ]:
            raise InvalidReportType(
                "Please use one of the following report types: ['traders_in_financial_futures_fut', 'traders_in_financial_futures_futopt']"
            )

        logging.info(f"Extracting data for the {report_type} report type")
        data_df = CommitmentsOfTraders(report_type).get_reports

        if data_df.empty:
            raise ValueError(
                f"No data found for the selected report type: {report_type}"
            )

        names, columns = zip(
            *settings.FORMAT_COLUMNS["traders_in_financial_futures_format"].items()
        )
        df = format_dataframe(data_df, names, columns)

        df["Net Position Asset Mgr"] = (
            df["Asset Manager Long"] - df["Asset Manager Short"]
        )
        df["Net Change Asset Mgr"] = (
            df["Asset Manager Long, Change"] - df["Asset Manager Short, Change"]
        )
        df["Net % of OI Asset Mgr"] = (
            df["Asset Manager Long, % of OI"] - df["Asset Manager Short, % of OI"]
        )
        df["Asset Manager Short"] = df["Asset Manager Short"] * -1

        df["Net Position Lev Money"] = (
            df["Leveraged Money Long"] - df["Leveraged Money Short"]
        )
        df["Net Change Lev Money"] = (
            df["Leveraged Money Long, Change"] - df["Leveraged Money Short, Change"]
        )
        df["Net % of OI Lev Money"] = (
            df["Leveraged Money Long, % of OI"] - df["Leveraged Money Short, % of OI"]
        )
        df["Leveraged Money Short"] = df["Leveraged Money Short"] * -1
        df = df.sort_index()[::-1]
        return df

    def list_available_contracts(
        self,
    ) -> np.ndarray:
        """
        Lists all available contracts for a selected Commitment of Traders report.

        Returns:
            A pandas DataFrame with the available contracts for the selected report.

        Example:
            >>> from pycot.reports import CommitmentsOfTraders
            >>> cot = CommitmentsOfTraders("legacy_fut")
            >>> cot.list_available_contracts()
            >>> ...
            >>> cot.report(contract_name)
        """
        if self.report_type is None:
            raise ValueError("Please select a report type to list available contracts")

        if self.report_type in [
            "legacy_fut",
            "legacy_futopt",
        ]:
            df = self.legacy_report
        elif self.report_type in [
            "disaggregated_fut",
            "disaggregated_futopt",
        ]:
            df = self.disaggregated_report
        elif self.report_type in [
            "traders_in_financial_futures_fut",
            "traders_in_financial_futures_futopt",
        ]:
            df = self.financial_report

        available_contracts = df["Contract Name"].unique()
        return np.sort(available_contracts)

    def report(
        self,
        contract_name: Union[str, tuple, None] = None,
    ) -> pd.DataFrame:
        """
        Retrieves data from a selected Commitment of Traders report.
        Results will be cached after the first call.

        Args:
            report (pd.DataFrame): The report to extract data from. Must be one of the following:

                - `legacy_report()`
                - `disaggregated_report()`
                - `financial_report()`

            contract_name (str | tuple): The name of the contract to extract data from.

        Returns:
            A pandas DataFrame with the Commitment of Traders data.

        Example:
            >>> from pycot.reports import CommitmentsOfTraders
            >>> cot = CommitmentsOfTraders("legacy_fut")
            >>> df_1 = cot.report(("FED FUNDS - CHICAGO BOARD OF TRADE", "30-DAY FEDERAL FUNDS - CHICAGO BOARD OF TRADE"))
            >>> df_2 = cot.report(("BBG COMMODITY - CHICAGO BOARD OF TRADE", "BLOOMBERG COMMODITY INDEX - CHICAGO BOARD OF TRADE"))
            >>> ...
        """
        if self.report_type is None:
            raise ValueError("Please select a report type to extract data from")

        if not isinstance(contract_name, (str, tuple)):
            raise TypeError("contract_name must be a string or a tuple")

        if self.report_type in [
            "legacy_fut",
            "legacy_futopt",
        ]:
            df = self.legacy_report
        elif self.report_type in [
            "disaggregated_fut",
            "disaggregated_futopt",
        ]:
            df = self.disaggregated_report
        elif self.report_type in [
            "traders_in_financial_futures_fut",
            "traders_in_financial_futures_futopt",
        ]:
            df = self.financial_report
        return get_contract(df, contract_name)
