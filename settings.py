"""Main setttings file."""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

# Base environment variables
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
FILENAME = os.path.join(BASE_DIR, "data/subreddits.json")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
REDDIT_BOT_ID = os.getenv("REDDIT_BOT_ID")
REDDIT_BOT_SECRET = os.getenv("REDDIT_BOT_SECRET")

DISCORD_BOT_ADVANCED_COMMANDS_ROLES = os.getenv(
    "DISCORD_BOT_ADVANCED_COMMANDS_ROLES", default=[]
).split(",")
DISCORD_BOT_NORMAL_COMMANDS_ROLES = os.getenv(
    "DISCORD_BOT_NORMAL_COMMANDS_ROLES", default=[]
).split(",")

# Logging
LOGFILENAME = os.getenv("LOGFILENAME", default="discord_bot")
logger = logging.getLogger(LOGFILENAME)
logger.setLevel(os.getenv("LOGLEVEL", default=logging.DEBUG))
handler = logging.FileHandler(
    filename=os.path.join(BASE_DIR, f"logs/{LOGFILENAME}.log"),
    encoding="utf-8",
    mode="a",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
