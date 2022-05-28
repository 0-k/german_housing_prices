import os
import logging
import yaml


try:
    with open(os.environ["CONFIG_PATH"]) as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logging.error(f"No such file or directory: {os.environ['CONFIG_PATH']})")
    raise BrokenPipeError(f"No such file or directory: {os.environ['CONFIG_PATH']})")
except KeyError:
    logging.error("No directory for utils (CONFIG_PATH) in environment given.")
    raise BrokenPipeError("No directory for utils (CONFIG_PATH) in environment given.")


HEADERS = config["HEADERS"]
URL_SEARCH = config["URL_SEARCH"]
URL_EXPOSE = config["URL_EXPOSE"]
PATH_CACHE = config["PATH_CACHE"]
TEST_SIZE = config["TEST_SIZE"]
DO_PLOTS = config["DO_PLOTS"]
DATASET_NAME = config["DATASET_NAME"]
