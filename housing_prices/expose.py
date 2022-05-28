from dataclasses import dataclass
from housing_prices.immowelt_scraper import (
    get_response_from_cache_or_request,
    _parse_to_soup,
)
from housing_prices.plz_to_coordinates import get_coordinates_for
import numpy as np
import logging

import housing_prices.utils.config as config


@dataclass
class Expose:

    id: str
    price: float = None
    area_living: float = None
    rooms: float = None
    area_plot: float = None
    plz: float = None
    latitude: float = None
    longitude: float = None

    # title: str = None
    # category: str = None
    # year: int = None
    # occupation: str = None
    # attributes: list = None

    def set_values(self):
        url = config.URL_EXPOSE + self.id
        response = get_response_from_cache_or_request(url=url, identifier=self.id)
        soup = _parse_to_soup(response)
        self._update_price(soup)
        self._get_areas_and_rooms(soup)
        self._update_plz(response)
        self._update_lat_lon()

    def _update_price(self, soup):
        price_as_str = soup.find_all("strong")[0].text
        try:
            self.price = float(
                price_as_str.replace(".", "").replace(",", ".").replace("€", "")
            )
        except ValueError as error:
            logging.warning(error)
            self.price = np.nan

    def _get_areas_and_rooms(self, soup):
        entries = soup.find_all("span", {"class": "has-font-300"})
        self.area_living = self._extract_item(entries[0])
        self.rooms = self._extract_item(entries[1])
        try:
            self.area_plot = self._extract_item(entries[2])
        except IndexError:  # no additional plot exists
            self.area_plot = 0

    def _extract_item(self, item):
        try:
            return float(item.text.replace("m²", "").replace(".", "").replace(",", "."))
        except ValueError as error:
            logging.warning(error)
            return np.nan

    def _update_plz(self, response):
        try:
            self.plz = int(response.split("zip=")[1].split()[0].replace('"', ""))
            print(self.plz)
        except ValueError as error:
            logging.warning(error)
            self.plz = np.nan
        except IndexError as error:
            logging.warning(error)
            self.plz = np.nan

    def _update_lat_lon(self):
        try:
            self.latitude, self.longitude = get_coordinates_for(self.plz)
        except ValueError as error:
            logging.warning(error)
            self.latitude = np.nan


if __name__ == "__main__":
    expose = Expose(id="25gps5l")
    soup = expose.set_values()
    print(expose.rooms)
    print(expose.area_plot)
    print(expose.area_living)
    print(expose.plz)
