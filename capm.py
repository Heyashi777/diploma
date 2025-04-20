import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import namedtuple
import statsmodels.api as sm

from utils import generate_half_year_dates

pd.set_option("display.max_columns", 400)
pd.set_option("display.width", 50)
pd.set_option("display.max_colwidth", None)

Model = namedtuple("Model", ["year", "name", "beta", "alfa", "returns"])


def capm_model(data: pd.DataFrame, MOEX: pd.DataFrame, stock_name: str, rf: float, plot: bool = False) -> dict:
    N = 252
    Rf_daily = np.log(1 + rf) / N
    capm_data = data[[stock_name, "MOEX"]].copy()
    capm_data.dropna(inplace=True)
    capm_data["X"] = MOEX["return"] - Rf_daily
    capm_data["Y"] = capm_data[stock_name] - Rf_daily
    X = sm.add_constant(capm_data["X"])
    X = X.fillna(0)  # type: ignore
    y = capm_data["Y"]
    capm_model = sm.OLS(y, X).fit()
    result = {}
    result["stock_name"] = stock_name
    result["beta_reg"] = capm_model.params.iloc[1]
    result["alpha"] = capm_model.params.iloc[0]
    moex_returns = MOEX["return"].mean()
    stock_returns = 0.09 + capm_model.params.iloc[1] * (moex_returns - 0.09)
    result["returns"] = stock_returns
    result["capm_model"] = capm_model
    if plot is True:
        plt.figure(figsize=(13, 9))
        plt.axvline(0, color="grey", alpha=0.5)
        plt.axhline(0, color="grey", alpha=0.5)
        sns.scatterplot(y=stock_name, x="MOEX", data=capm_data, label="Returns")
        sns.lineplot(
            x=MOEX["return"],
            y=capm_model.params.iloc[0] + MOEX["return"] * capm_model.params.iloc[1],
            color="red",
            label="CAPM Line",
        )
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
MOEX = pd.read_csv("data/MOEX.csv", index_col="TRADEDATE", parse_dates=["TRADEDATE"])

train_data = data[data.index >= "2014-01-01 00:00:00"]
pred_data = data[data.index < "2014-01-01 00:00:00"]

train_data_MOEX = MOEX[MOEX.index >= "2014-01-01 00:00:00"]
pred_data_MOEX = MOEX[MOEX.index < "2014-01-01 00:00:00"]

periods = generate_half_year_dates(train_data)
stocks = data.columns.to_list()[:-1]
step = 0

central_bank_rf = [
    5.5,
    8,
    17,
    11.5,
    11,
    10.5,
    10,
    9,
    7.75,
    7.25,
    7.75,
    7.5,
    6.25,
    4.25,
    4.25,
    5.5,
    8.5,
    9.5,
    8.5,
    12,
    16,
    16,
]
for i in range(len(central_bank_rf)):
    central_bank_rf[i] = central_bank_rf[i] / 100

capm_data = []

for stock in stocks:
    stock_data = pred_data[[stock, "MOEX"]].copy()
    MOEX_ = pred_data_MOEX
    if stock_data[stock].dropna().empty:
        continue
    if stock not in stock_data.columns:
        continue
    capm = capm_model(data=stock_data, MOEX=MOEX_, stock_name=stock, rf=0.09)
    stock_capm = Model("2013", stock, capm["beta_reg"], capm["alpha"], capm["returns"])
    capm_data.append(stock_capm)

i = -1
for per in periods:
    i += 1
    stop = per + pd.DateOffset(months=6)
    period_data = train_data[(train_data.index >= per) & (train_data.index < stop)].copy()
    period_data_MOEX = train_data_MOEX[(train_data_MOEX.index >= per) & (train_data_MOEX.index < stop)].copy()
    for stock in stocks:
        stock_data = period_data[[stock, "MOEX"]].copy()
        if period_data.empty:
            continue
        if stock not in period_data.columns or "MOEX" not in period_data.columns:
            continue
        if stock_data.dropna().empty:
            print(f"⚠ Период {per} - {stop} пуст, пропускаем.")
            continue
        capm = capm_model(data=stock_data, MOEX=period_data_MOEX, stock_name=stock, rf=central_bank_rf[i])
        # print(stock)
        # print("Parameters: ", capm["capm_model"].params.iloc[1])
        # print("R2: ", capm["capm_model"].rsquared)
        stock_capm = Model(per, stock, capm["beta_reg"], capm["alpha"], capm["returns"])
        capm_data.append(stock_capm)

# print(capm_data)
capm_data_frame = pd.DataFrame(capm_data)
capm_data_frame.to_csv("data/capm_data.csv", index=False)
# print(capm_data_frame[capm_data_frame["beta"] > 0.8])
