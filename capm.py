import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import namedtuple

from utils import generate_half_year_dates

pd.set_option("display.max_columns", 400)
pd.set_option("display.width", 50)
pd.set_option("display.max_colwidth", None)

Model = namedtuple("Model", ["year", "name", "beta", "alfa", "returns"])


def capm_model(data: pd.DataFrame, market_name: str, stock_name: str, plot: bool = False) -> dict:
    capm_data = data[[stock_name, market_name]].copy()
    beta = (capm_data.cov() / capm_data[market_name].var()).iloc[0].iloc[1]  # type: ignore
    capm_data.dropna(inplace=True)
    beta_reg, alpha = np.polyfit(x=capm_data[market_name], y=capm_data[stock_name], deg=1)
    result = {}
    result["stock_name"] = stock_name
    result["beta"] = beta
    result["beta_reg"] = beta_reg
    result["alpha"] = alpha
    moex_returns = capm_data["MOEX"].mean()
    stock_returns = 0.09 + beta_reg * (moex_returns - 0.09)
    result["returns"] = stock_returns
    if plot is True:
        plt.figure(figsize=(13, 9))
        plt.axvline(0, color="grey", alpha=0.5)
        plt.axhline(0, color="grey", alpha=0.5)
        sns.scatterplot(y=stock_name, x=market_name, data=capm_data, label="Returns")
        sns.lineplot(x=capm_data["MOEX"], y=alpha + capm_data["MOEX"] * beta_reg, color="red", label="CAPM Line")
        plt.xlabel("Market Monthly Return: {market_name}")
        plt.ylabel("Investment Monthly Return: {stock_name}")
        plt.legend(bbox_to_anchor=(1.01, 0.8), loc=2, borderaxespad=0.0)
        plt.show()
    return result


def create_data_set_for_period(df: pd.DataFrame, start_date: str) -> pd.DataFrame:
    start_date = pd.to_datetime(start_date)  # type: ignore
    end_date = start_date + pd.DateOffset(months=6)  # type: ignore
    filtered_df = df[(df.index >= start_date) & (df.index <= end_date)]
    return filtered_df


data = pd.read_csv("data/returns_of_stok.csv", index_col="TRADEDATE", parse_dates=["TRADEDATE"])
train_data = data[data.index >= "2014-01-01 00:00:00"]
pred_data = data[data.index < "2014-01-01 00:00:00"]
periods = generate_half_year_dates(train_data)
stocks = data.columns.to_list()[:-1]
step = 0

capm_data = []

for stock in stocks:
    stock_data = pred_data[[stock, "MOEX"]].copy()
    if stock_data[stock].dropna().empty:
        continue
    if stock not in stock_data.columns or "MOEX" not in stock_data.columns:
        continue
    capm = capm_model(data=stock_data, market_name="MOEX", stock_name=stock)
    stock_capm = Model("2013", stock, capm["beta"], capm["alpha"], capm["returns"])
    capm_data.append(stock_capm)

for per in periods:
    stop = per + pd.DateOffset(months=6)
    period_data = train_data[(train_data.index >= per) & (train_data.index < stop)].copy()
    for stock in stocks:
        stock_data = period_data[[stock, "MOEX"]].copy()
        if period_data.empty:
            continue
        if stock not in period_data.columns or "MOEX" not in period_data.columns:
            continue
        if stock_data.dropna().empty:
            print(f"⚠ Период {per} - {stop} пуст, пропускаем.")
            continue
        capm = capm_model(data=stock_data, market_name="MOEX", stock_name=stock)
        stock_capm = Model(per, stock, capm["beta_reg"], capm["alpha"], capm["returns"])
        capm_data.append(stock_capm)

# print(capm_data)
capm_data_frame = pd.DataFrame(capm_data)
capm_data_frame.to_csv("data/capm_data.csv", index=False)
