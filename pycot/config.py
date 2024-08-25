import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


def open_json(path: Path) -> dict:
    """Opens a json file."""
    with open(path, "r") as f:
        data = json.load(f)
    return data


class Settings(BaseSettings):
    """Settings for the pycot package."""

    BASE_PATH: Path = Path(__file__).parent.parent
    FORMAT_COLUMNS_PATH: Path = BASE_PATH / "pycot" / "store" / "format_columns.json"
    COT_REPORTS_DATA_PATH: Path = (
        BASE_PATH / "pycot" / "store" / "cot_reports_data.json"
    )
    CONTRACT_NAMES_PATH: Path = BASE_PATH / "pycot" / "store" / "contract_names.json"

    FORMAT_COLUMNS: dict = open_json(FORMAT_COLUMNS_PATH)
    COT_REPORTS_DATA: dict = open_json(COT_REPORTS_DATA_PATH)
    CONTRACT_NAMES: dict = open_json(CONTRACT_NAMES_PATH)


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings object to avoid reading the environment variables."""
    return Settings()


settings = get_settings()
