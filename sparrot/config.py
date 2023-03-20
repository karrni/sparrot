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

        self.registrars = [line.strip().lower() for line in open(location / "registrars.txt", encoding="utf8")]

    @property
    def api_key(self):
        return self.config["whoxy"]["api_key"] or self.args.api_key


settings = Settings()
