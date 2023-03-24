import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from sparrot.logger import Logger

location = Path(__file__).resolve().parent

logger = Logger()


REGISTRARS_URL = "https://www.iana.org/assignments/registrar-ids/registrar-ids.xml"
REGISTRARS_FILE = location / "registrars.txt"


def update_registrars():
    logger.info(f"Downloading list of registrars from {REGISTRARS_URL}")
    response = requests.get(REGISTRARS_URL)

    if response.status_code != 200:
        logger.error("Error while retrieving registrars")
        return

    xml_data = response.text
    root = ET.fromstring(xml_data)

    namespace = {"iana": "http://www.iana.org/assignments"}

    logger.info("Parsing registrars")

    registrars = []
    for record in root.findall(".//iana:record", namespace):
        name = record.find("iana:name", namespace).text
        registrars.append(name)

    logger.info(f"{len(registrars)} total registrars")

    logger.info(f"Writing to file {REGISTRARS_FILE}")
    with open(REGISTRARS_FILE, "w", encoding="utf-8") as fp:
        fp.write("\n".join(registrars))


if __name__ == "__main__":
    update_registrars()
