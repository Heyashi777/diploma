from utils import get_unique_names_stocks, save_csv, setup_logger_writer
import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "stoks_data"
LOG_DIR = BASE_DIR / "loggers"


def get_stocks_data() -> str | None:
    logger = setup_logger_writer(LOG_DIR / "get_stonks.log")
    logger.info("#" * 20)
    try:
        list_names = get_unique_names_stocks()
        logger.info("Successfully fetched unique stock names")
    except Exception as e:
        logger.error(f"ERROR: {e}")
        return
    for stok in tqdm(list_names, desc="Processing stocks", unit="stock"):
        data_parts = []
        start = 0
        index = 1
        while index == 1:
            base_url = f"http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{stok}.json?start={start}&interval=24"
            logger.info(f"START Fetching data for {stok} part {start}-{start + 100}")
            try:
                j = requests.get(base_url).json()
                data = [{k: r[i] for i, k in enumerate(j["history"]["columns"])} for r in j["history"]["data"]]
                frame = pd.DataFrame(data)
                data_parts.append(frame)
                if len(frame) == 100:
                    start += 100
                else:
                    index = -1
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data for {stok}: {e}")
                continue
        name = DATA_DIR / f"{stok}.csv"
        insert_data = pd.concat(data_parts, axis=0)
        save_csv(insert_data, name)
        logger.info(f"END Fetching data for {stok}")
        logger.info(f"{len(frame)} rows fetched")
    logger.info("END ETL PROC")


get_stocks_data()
