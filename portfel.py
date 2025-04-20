import numpy as np
import scipy.optimize as sco
import pandas as pd
from collections import namedtuple

from utils import generate_half_year_dates


def portfolio_volatility(weights):
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


Portfel = namedtuple("Portfel", ["period", "beta", "future_income", "fact_income", "moex_income"])

capm_data = pd.read_csv("data/capm_data.csv", parse_dates=["year"], index_col="year")
# data_moex = pd.read_csv("data/returns_of_stok.csv", index_col="TRADEDATE", parse_dates=["TRADEDATE"])
data_moex = pd.read_csv("data/MOEX.csv", index_col="TRADEDATE", parse_dates=["TRADEDATE"])
# capm_data = capm_data[(capm_data.index >= "2014-01-01 00:00:00")]
# data_moex = data_moex[data_moex.index >= "2014-01-01 00:00:00"]
capm_data.index = pd.to_datetime(capm_data.index)
# capm_data.index = pd.to_datetime(capm_data.index, format="mixed", dayfirst=True, errors="coerce")

periods = generate_half_year_dates(capm_data)
result = []

i = 0
for per in periods[1:]:
    stop = per + pd.DateOffset(months=6)
    tarin_data = capm_data[(capm_data.index >= per) & (capm_data.index < stop)].copy()
    tarin_data = tarin_data[(tarin_data["returns"] >= 0)]  # (tarin_data["beta"] >= 0) &
    moex = data_moex[
        (data_moex.index >= per + pd.DateOffset(months=6)) & (data_moex.index < stop + pd.DateOffset(months=6))
    ].copy()
    # if i >= 1:
    #     income = pd.merge(weights_data, tarin_data, how="left", on="name")  # noqa: F821
    #     # print(income)
    #     income["income"] = income["returns_y"]
    #     # print(f"Доходность настоящая для периода {i - 1} составила {income['income'].mean() * 100 * 2:.2f}%\n")
    #     sub_result = Portfel(
    #         per,
    #         beta_portfolio,  # noqa: F821
    #         expected_return * 100,  # noqa: F821
    #         income["income"].mean() * 100,
    #         moex["MOEX"].mean() * 100,
    #     )  # noqa: F821
    #     result.append(sub_result)
    cov_matrix = np.cov(tarin_data["returns"], rowvar=False)
    num_assets = len(tarin_data)
    init_guess = num_assets * [1.0 / num_assets]  # Начальные веса (равномерные)
    bounds = tuple((0, 1) for _ in range(num_assets))  # Веса от 0 до 1
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}  # Сумма весов = 1
    opt_result = sco.minimize(portfolio_volatility, init_guess, method="SLSQP", bounds=bounds, constraints=constraints)
    optimal_weights = opt_result.x
    tarin_data["weight"] = optimal_weights

    # Выводим состав портфеля
    # print(tarin_data[["name", "weight", "beta", "returns"]])

    beta_portfolio = (tarin_data["beta"] * tarin_data["weight"]).sum()
    # print(f"Бета портфеля {i} : {beta_portfolio:.2f}")

    # Ожидаемая доходность портфеля
    expected_return = (tarin_data["returns"]).mean()  # * tarin_data["weight"]   .sum()
    # print(f"Ожидаемая доходность портфеля: {expected_return * 2:.2%} годовых")
    income = pd.merge(
        tarin_data,
        capm_data[
            (capm_data.index >= per + pd.DateOffset(months=6)) & (capm_data.index < stop + pd.DateOffset(months=6))
        ],
        how="left",
        on="name",
    )
    income["income"] = income["returns_y"]
    sub_result = Portfel(
        per + pd.DateOffset(months=6),
        beta_portfolio,  # noqa: F821
        (np.exp(income["income"].mean()) - 1) * 100,
        (np.exp(expected_return) - 1) * 100,
        (np.exp(moex["return"].mean()) - 1) * 100,
    )  # noqa: F821
    result.append(sub_result)
    i += 1
    print(len(tarin_data))

for item in result:
    print(item)

portfels = pd.DataFrame(result)
# portfels.to_csv("data/portfels.csv", index=False)
