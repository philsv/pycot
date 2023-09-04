import io
import json
import os
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from exceptions import InvalidReportType

BASE_PATH = Path(__file__).parent.parent


def get_cot_data() -> dict:
    """
    Extracts the Commitment of Traders Reports metadata.
    """
    with open(BASE_PATH / "pycot/data/cot_reports_data.json", "r") as f:
        return json.load(f)


def get_formating_data() -> dict:
    """
    Extracts the column formating data.
    """
    with open(BASE_PATH / "pycot/data/format_columns.json", "r") as f:
        return json.load(f)


@dataclass
class COT:
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

    report_type: str

    def extract_text_file_to_dataframe(
        self,
        response: requests.models.Response,
        text_file: str,
    ) -> pd.DataFrame:
        """
        Unzips the text file from an archive and returns a pandas DataFrame.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.chdir(tmpdirname)  # change working directory to temp directory

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall()
            return pd.read_csv(text_file, low_memory=False)


    def get_legacy_report(self) -> pd.DataFrame:
        """
        Retrieves the Commitment of Traders Report data selected by the report_type argument.

        Returns:
            A pandas DataFrame with the historical Commitment of Traders data.
        """
        report_data = get_cot_data()

        if self.report_type not in report_data.keys():
            raise InvalidReportType(f"Please use one of the following report types: {list(report_data.keys())}")

        metadata = report_data[self.report_type]["legacy"]
        response = requests.get(metadata["url"])
        response.raise_for_status()
        return self.extract_text_file_to_dataframe(response, metadata["text_file"])

    def get_reports_by_year(
        self,
        report_year: int | None = None,
    ) -> pd.DataFrame | None:
        """
        Retrieves the Commitment of Traders Reports data by year.

        Returns:
            A pandas DataFrame with the historical Commitment of Traders data by the specified year.
        """
        report_data = get_cot_data()

        if self.report_type not in report_data.keys():
            raise InvalidReportType(f"Please use one of the following report types: {list(report_data.keys())}")

        metadata = report_data[self.report_type]["current"]
        response = requests.get(f"{metadata['url']}{report_year}.zip")

        if response.status_code == 404:
            # Avoid non-existent data for a given year
            return None
        return self.extract_text_file_to_dataframe(response, metadata["text_file"])

    def get_reports(self) -> pd.DataFrame:
        """
        Retrieves the combined Commitment of Traders Reports data.

        Returns:
            A pandas DataFrame with the legacy and current Commitment of Traders data.
        """
        legacy_data = self.get_legacy_report()
        current_data = [self.get_reports_by_year(year) for year in range(2017, date.today().year + 1)]
        return pd.concat([legacy_data] + current_data, ignore_index=True)
