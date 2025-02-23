import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def cum_plot(data: pd.DataFrame) -> go.Figure:
    data_with_moex = data.copy()
    del data_with_moex["MOEX"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data["MOEX"], x=data.index, mode="lines", name="MOEX"))
    fig.add_trace(go.Scatter(y=data_with_moex.mean(axis=1), x=data.index, mode="lines", name="AVG(all without MOEX)"))
    fig.update_layout(
        title="Кумулятивная логарифмическая доходность",
        xaxis_title="время",
        yaxis_title="Кумулятивная логарифмическая доходность",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig
