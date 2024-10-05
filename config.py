from dataclasses import dataclass, field
import os
from os import getenv, environ


@dataclass(frozen=True, slots=True, kw_only=True)
class Config:
    base_dir: str = field(
        default=os.path.abspath(os.path.dirname(__file__))
        )
    database_url: str = field(
        default_factory=lambda: environ["DATABASE_URL"]
        )
    sql_alchemy_track_modifications: bool = field(
        default_factory=lambda: bool(environ["SQL_ALCHEMY_TRACK_MODIFICATIONS"])
        )
    telegram_bot_token: str = field(
        default_factory=lambda: environ["TELEGRAM_BOT_TOKEN"]
    )
    upload_folder: str = field(
        default_factory=lambda: environ["UPLOAD_FOLDER"]
    )
    admin_password: str = field(
        default_factory=lambda: environ["ADMIN_PASSWORD"]
    )