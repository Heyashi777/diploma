import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 400)
pd.set_option("display.width", 50)
pd.set_option("display.max_colwidth", None)

data = pd.read_csv("data/main_stok_dataset.csv", parse_dates=["TRADEDATE"])
data["TRADEDATE"] = pd.to_datetime(data["TRADEDATE"], errors="coerce")
data = data.set_index("TRADEDATE")
del data["Unnamed: 0"]
# data = data.fillna(0)  # заменяем все пропуски на 0
data.fillna(method="ffill", inplace=True)  # type: ignore


def cumulative_log_return(df: pd.DataFrame) -> pd.DataFrame:
    log_returns = np.log(df / df.shift(1))  # Логарифмическая доходность
    cumulative_log_returns = log_returns.cumsum()  # Кумулятивная логарифмическая доходность
    return cumulative_log_returns


data_returns = np.log(data / data.shift(1))
# print(data_returns)
data_returns.to_csv("data/returns_of_stok.csv")

cum_returns_data = cumulative_log_return(data)
fig = go.Figure()
for col in cum_returns_data.columns:
    fig.add_trace(go.Scatter(y=cum_returns_data[col], x=cum_returns_data.index, mode="lines", name=col))
fig.update_layout(
    title="Кумулятивная логарифмическая доходность",
    xaxis_title="время",
    yaxis_title="Кумулятивная логарифмическая доходность",
    plot_bgcolor="white",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
)
fig.show()
