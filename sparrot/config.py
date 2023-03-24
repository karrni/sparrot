import shutil
from argparse import Namespace
from pathlib import Path

import toml

location = Path(__file__).resolve().parent

config_dir = Path.home() / ".config"
config_file = config_dir / "sparrot.toml"

if not config_dir.exists():
    config_dir.mkdir()

if not config_file.exists():
    shutil.copy(location / "sparrot.toml", config_file)


class Settings:
    def __init__(self):
        self.args = Namespace()
        self.config = toml.load(config_file)

        self.registrars = []
        with open(location / "registrars.txt", encoding="utf-8") as fp:
            for line in fp:
                self.registrars.append(line.strip().lower())

    @property
    def api_key(self):
        return self.config["whoxy"]["api_key"] or self.args.api_key


settings = Settings()
