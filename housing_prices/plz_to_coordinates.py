import geopandas as gpd
import numpy as np
import warnings
import logging

warnings.simplefilter(action="ignore", category=UserWarning)

zip_codes_germany = gpd.read_file("../data/plz_map/OSM_PLZ.shp")
zip_codes_germany = zip_codes_germany.to_crs(epsg=4326)


def get_coordinates_for(plz):
    try:
        plz_shape = zip_codes_germany[zip_codes_germany["plz"] == str(int(plz))]
        centroids = plz_shape.geometry.centroid
        x, y = 0, 0
        for index, value in centroids.items():
            x += value.x
            y += value.y
        return round(y / len(centroids), 3), round(x / len(centroids), 3)
    except ZeroDivisionError as error:
        logging.warning(f"Error of type {error} at PLZ: {plz}")
        return np.nan, np.nan
