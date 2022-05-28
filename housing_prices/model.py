import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_squared_error as rsme
from sklearn.model_selection import cross_val_score
import numpy as np
import matplotlib.pyplot as plt

from housing_prices.plz_to_coordinates import get_coordinates_for, zip_codes_germany
import housing_prices.utils.config as config
from housing_prices.prepare_data import (
    data,
    _clean_and_scale,
    features_train,
    features_test,
    targets_train,
    targets_test,
)


def cross_validate(model):
    scores = cross_val_score(
        model, features_train, targets_train, scoring="neg_mean_squared_error", cv=10
    )
    scores = np.sqrt(-scores)
    print(f"RMSE Training: {round(scores.mean(), 3)} +- {round(scores.std(), 3)}")


def predict(model, features_test, targets_test):
    predictions = model.predict(features_test)
    if targets_test is not None:
        print(f"RSME Test: {round(np.sqrt(rsme(predictions, targets_test)), 3)}")
        print(f"MAE Test: {round(mae(predictions, targets_test), 3)}")
        if config.DO_PLOTS:
            _plot(predictions)
    else:
        print(predictions)


def _plot(predictions):
    plt.scatter(predictions, targets_test, alpha=0.1)
    plt.show()


def create_and_train_model():
    model = GradientBoostingRegressor()
    model.fit(features_train, targets_train)
    cross_validate(model)
    return model


def test_model():
    model = create_and_train_model()
    predict(model, features_test, targets_test)


model = create_and_train_model()
plzs = data.plz.unique().tolist()
plzs_str = [str(int(plz)) for plz in plzs]
predictions = []

for plz in plzs:
    lat, lon = get_coordinates_for(plz)
    house = [[100, 5, 0, lat, lon]]
    prediction = model.predict(house)
    predictions.append(prediction[0])


df = pd.DataFrame({"market_value": predictions, "plz": plzs_str})
zip_codes_germany = zip_codes_germany.merge(df, how="inner", on="plz")
print(zip_codes_germany["bundesland"])
zip_codes_germany.plot(column="market_value", legend=True)
plt.show()
