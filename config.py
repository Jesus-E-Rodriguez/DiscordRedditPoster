"""Main configuration file for the application."""
import logging
import os
from logging.config import dictConfig
from typing import List

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOGFILENAME = os.getenv("LOGFILENAME", default="discord_bot")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            f"{LOGFILENAME}": {
                "class": "logging.FileHandler",
                "filename": os.path.join(BASE_DIR, f"logs/{LOGFILENAME}.log"),
                "encoding": "utf-8",
                "mode": "a",
                "formatter": "default",
            }
        },
        "root": {
            "level": os.getenv("LOGLEVEL", default=logging.DEBUG),
            "handlers": [f"{LOGFILENAME}"],
        },
    }
)


class BaseConfig:
    """Base configuration"""

    DEBUG: bool = False
    TESTING: bool = False
    BASE_DIR: str = BASE_DIR
    FILENAME: bytes = os.path.join(BASE_DIR, "data/subreddits.json")
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    DISCORD_BOT_ADVANCED_COMMANDS_ROLES: List[str] = os.getenv(
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES", default=[]
    ).split(",")
    DISCORD_BOT_NORMAL_COMMANDS_ROLES: List[str] = os.getenv(
        "DISCORD_BOT_NORMAL_COMMANDS_ROLES", default=[]
    ).split(",")
    LOGFILENAME: str = LOGFILENAME


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True
    TESTING: bool = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
