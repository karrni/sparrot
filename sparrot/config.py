import configparser
import shutil
from argparse import Namespace
from pathlib import Path

# path of the current file
location = Path(__file__).resolve().parent

# the sparrot.conf is stored under ~/.config/
config_dir = Path.home() / ".config"
config_file = config_dir / "sparrot.conf"


class Settings:
    def __init__(self):
        self.args = Namespace()
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.registrars = [line.strip().lower() for line in open(location / "registrars.txt", encoding="utf8")]

    @property
    def api_key(self):
        return self.config.get("whoxy", "api_key") or self.args.api_key


# create ~/.config if it doesn't exist
if not config_dir.exists():
    config_dir.mkdir()

# copy and use example config if it doesn't exist
if not config_file.exists():
    shutil.copy(location / "sparrot.conf.example", config_file)

# instance that stores the settings
settings = Settings()
