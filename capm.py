import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 400)
pd.set_option("display.width", 50)
pd.set_option("display.max_colwidth", None)

data = pd.read_csv("data/returns_of_stok.csv", index_col="TRADEDATE", parse_dates=["TRADEDATE"])
# print(data)

# data_with_moex = data.copy()
# del data_with_moex["MOEX"]


# fig = go.Figure()
# fig.add_trace(go.Scatter(y=data["MOEX"], x=data.index, mode="lines", name="MOEX"))
# fig.add_trace(go.Scatter(y=data_with_moex.mean(axis=1), x=data.index, mode="lines", name="AVG(all without MOEX)"))
# fig.update_layout(
#     title="Кумулятивная логарифмическая доходность",
#     xaxis_title="время",
#     yaxis_title="Кумулятивная логарифмическая доходность",
#     plot_bgcolor="white",
#     xaxis=dict(showgrid=False),
#     yaxis=dict(showgrid=False),
# )
# fig.show()
