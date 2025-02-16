import pandas as pd
from pathlib import Path
import logging

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 50)
pd.set_option("display.max_colwidth", None)


def get_unique_names_stoks() -> list[str]:
    """
    Функция, которая берёт файл с данными о доступных котировках с биржи MOEX и возвращает лист с уникальными тикерами

    Returns
    -------
    list[str] : лист с котировками
    """
    data = pd.read_csv("data/Export_ru_securities-list_20250126.csv", sep=";", encoding="UTF-8")
    data = data[data["SUPERTYPE"] == "Акции"]
    return data["TRADE_CODE"].to_list()


def save_csv(df: pd.DataFrame, dir: str | Path) -> None:
    df.to_csv(dir)


def setup_logger_writer(log_path: str | Path) -> logging.Logger:
    """
    Функция, для создания логера для пред-ETL-процесса

    Parameters
    ----------
    log_path: путь к директории лог файла

    Returns
    -------
    logger : logging. Logger логер к функции сбора данных через API MOEX
    """
    logger = logging.getLogger("API_MOEX_Logger")
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_path, mode="a")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(file_handler)

    return logger
