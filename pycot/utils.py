import numpy as np
import pandas as pd


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
