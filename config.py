"""Main configuration file for the application."""
import logging
import os
from logging.config import dictConfig
from dotenv import load_dotenv

from env import EnvMixin

load_dotenv()


ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
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


class BaseConfig(EnvMixin):
    """Base configuration"""

    ENVIRONMENT: str = ENVIRONMENT
    DEBUG: bool = False
    TESTING: bool = False
    DISCORD_BOT_TOKEN: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str
    DISCORD_BOT_ADVANCED_COMMANDS_ROLES: list
    DISCORD_BOT_NORMAL_COMMANDS_ROLES: list
    BASE_DIR: str = BASE_DIR
    FILENAME: str = os.path.join(BASE_DIR, "data/subreddits.json")
    LOGFILENAME: str = LOGFILENAME


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True
    TESTING: bool = True


class ProductionConfig(BaseConfig):
    """Production configuration."""


def get_config(env: str) -> BaseConfig:
    """Get configuration based on environment."""
    if env.lower() == "development":
        return DevelopmentConfig()
    elif env.lower() == "production":
        return ProductionConfig()
    else:
        raise ValueError(f"Invalid environment: {env}")
