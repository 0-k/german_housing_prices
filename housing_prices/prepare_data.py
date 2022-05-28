import logging
import numpy as np
import pandas as pd
import dataclasses
from os.path import exists
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

import housing_prices.utils.config as config
from housing_prices.immowelt_scraper import (
    get_links_to_all_offers_of_search_page,
    get_id_from_url,
)
from housing_prices.expose import Expose


def extract_dataset():
    if exists(config.PATH_CACHE + config.DATASET_NAME):
        return
    data = []
    idx = 0
    while True:
        try:
            print(idx)
            idx += 1
            url = f"{config.URL_SEARCH}&sp={idx}"
            urls = get_links_to_all_offers_of_search_page(url)
            for url in urls:
                id = get_id_from_url(url)
                expose = Expose(id)
                expose.set_values()
                data.append(dataclasses.asdict(expose))
        except IndexError as error:
            logging.error(error)
            break
    df = pd.DataFrame(data)
    df.to_csv(config.PATH_CACHE + config.DATASET_NAME)


def load_dataset():
    df = pd.read_csv(config.PATH_CACHE + config.DATASET_NAME, index_col=0)
    return df


def _remove_missing(data):
    data_rm = data.dropna(subset=["price"])
    # TODO matching with PLZ list of Berlin
    data_rm = data_rm[data_rm["plz"] != np.nan]
    data_rm = data_rm[data_rm["plz"] != 43870]
    data_rm = data_rm[data_rm["plz"] != 16359]
    data_rm = data_rm.dropna(subset=["id"])
    data_rm = data_rm.dropna(thresh=7)
    return data_rm


def _curtail(data):
    # data = data.drop(columns=["plz"])
    data = data[data["price"] >= 300000]
    return data[data["price"] <= 3 * data["price"].median()]


def _visualize(data):
    pd.plotting.scatter_matrix(data)
    plt.show()


def _compartmentalize(data):
    train_set, test_set = train_test_split(
        data, test_size=config.TEST_SIZE, random_state=42
    )
    return train_set, test_set


def _clean_and_scale(data):
    # remove NaN values with median and scale data
    try:
        data_num = data.drop("id", axis=1)
    except AttributeError:
        data_num = data
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            # ("std_scaler", StandardScaler()),
        ]
    )
    return pipeline.fit_transform(data_num)


def run():
    return True


extract_dataset()
data = load_dataset()
data = _remove_missing(data)
data = _curtail(data)

if __name__ == "__main__":
    data.describe().to_csv(config.PATH_CACHE + "describe.csv")
    _visualize(data)

if __name__ != "__main__":
    train_set, test_set = _compartmentalize(data)
    features_train = train_set.drop(["price", "plz"], axis=1)
    features_test = test_set.drop(["price", "plz"], axis=1)

    targets_train = train_set["price"]
    targets_test = test_set["price"]
    features_train = _clean_and_scale(features_train)
    features_test = _clean_and_scale(features_test)
