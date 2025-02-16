import pandas as pd
import os
import plotly.graph_objects as go
import matplotlib.cm as cm
import matplotlib.colors as mcolors


def merge_csv_files(folder_path: str, main_file_name: str) -> pd.DataFrame:
    """
    Функция, которая считывает всё с папки с данными по котировкам MOEX
    и записывает в отдельный дата-сет, беря только данные в диапазоне
    базового файла (в данном случае, подразумевается MOEX)

    Parameters
    ----------
    folder_path : str
        путь к папке с файлами
    main_file_name : str
        название основного файле

    Returns
    -------
    pd.DataFrame
        дата-сет со всеми данными из папки
    """
    main_file_path = os.path.join(folder_path, main_file_name)
    main_df = pd.read_csv(
        main_file_path, usecols=["TRADEDATE", "SHORTNAME", "SECID", "OPEN"], parse_dates=["TRADEDATE"]
    )
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv") and file_name != main_file_name:
            file_path = os.path.join(folder_path, file_name)
            temp_df = pd.read_csv(file_path, usecols=["TRADEDATE", "OPEN"], parse_dates=["TRADEDATE"])
            # print(f"{file_name[:-4]}: {min(temp_df['TRADEDATE'])}")
            temp_df = temp_df.rename(columns={"OPEN": f"{file_name[:-4]}"})
            main_df = main_df.merge(temp_df, on="TRADEDATE", how="left", suffixes=("", f"_{file_name[:-4]}"))
    return main_df


FOLDER_PATH = "data/stoks_data/"
MAIN_FILE_NAME = "MOEX.csv"

merged_df = merge_csv_files(FOLDER_PATH, MAIN_FILE_NAME)

merged_df["MOEX"] = merged_df["OPEN"]
merged_df = merged_df[merged_df["TRADEDATE"] < "2025-01-01"].drop(columns=["SHORTNAME", "SECID", "OPEN"])

# Немного статистики о данных
print(merged_df.head(1))
print("\nМинимальная дата", min(merged_df["TRADEDATE"]))
print("\nМаксимальная дата", max(merged_df["TRADEDATE"]))
print(merged_df.describe())
# print("\nУникальнные колонки", merged_df.columns.unique().to_list())
# merged_df.to_csv("data/main_stok_dataset.csv")

"""Строим график"""
non_empty_counts = merged_df.iloc[:, 1:].count()
norm = mcolors.Normalize(vmin=min(non_empty_counts.values), vmax=max(non_empty_counts.values))
colormap = cm.get_cmap("viridis")
colors = [
    "red" if ticker == "MOEX" else mcolors.rgb2hex(colormap(norm(count))[:3])
    for ticker, count in zip(non_empty_counts.index, non_empty_counts.values)
]
fig = go.Figure(
    data=[
        go.Bar(
            x=non_empty_counts.index,
            y=non_empty_counts.values,
            marker=dict(color=colors),
        )
    ]
)
fig.update_layout(
    title="Кол-во торговых дней",
    xaxis_title="Котировка",
    yaxis_title="Кол-во торговых дней для котировки",
    plot_bgcolor="white",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
)
# fig.show()
# fig.write_image("images/trading_days_chart.png", scale=2)
