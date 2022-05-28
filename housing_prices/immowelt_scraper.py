from os.path import exists
from bs4 import BeautifulSoup
import requests
import numpy as np
import logging
import hashlib
import time
import random

import housing_prices.utils.config as config


def _get_hash(str):
    return hashlib.md5(str.encode("utf-8")).hexdigest()[:6]


def get_links_to_all_offers_of_search_page(search_page_url=None) -> list:
    """return: List of links to offers"""
    response = get_response_from_cache_or_request(search_page_url)
    soup = _parse_to_soup(response)
    return _extract_urls_from(soup)


def _parse_to_soup(response: str):
    return BeautifulSoup(response, "html.parser")


def _extract_urls_from(soup) -> list:
    all_urls = soup.find_all("a", href=True)
    return [url["href"] for url in all_urls if "expose" in url["href"]]


def get_response_from_cache_or_request(url=None, identifier=None) -> str:
    if url is None:
        url = config.URL_SEARCH
    if identifier is None:
        identifier = _get_hash(url)
    path = f"{config.PATH_CACHE}response_{identifier}.txt"
    if not exists(path):
        logging.info(f"Making request at {url}")
        _make_request(url, path)
    response = open(path, "r", encoding="utf-8").read()
    return response


def _make_request(search_page_url, path):
    response = requests.get(search_page_url, headers=config.HEADERS)
    time.sleep(random.randint(1, 3))
    with open(path, "w", encoding="utf-8") as file:
        file.write(response.text)


def get_prices_from_tags(soup) -> list:
    tags = soup.find_all(attrs={"data-test": "prices"})
    return [_extract_price_as_int(tag) for tag in tags]


def get_areas_from_tags(soup) -> list:
    tags = soup.find_all(attrs={"data-test": "area"})
    return [_extract_area_as_float(tag) for tag in tags]


def _extract_price_as_int(tag):
    try:
        return int(tag.text.split(" ")[0].replace(".", ""))
    except ValueError:
        return np.nan


def _extract_area_as_float(tag):
    try:
        return float(tag.text.split(" ")[0])
    except ValueError:
        return np.nan


def get_id_from_url(url):
    return url.split("/")[-1]


if __name__ == "__main__":
    urls = get_links_to_all_offers_of_search_page(config.URL_SEARCH)
    print(urls)
