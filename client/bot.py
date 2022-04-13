"""Collection of bots."""

from discord.ext import commands

from config import BaseConfig


class Bot(commands.Bot):
    """Main bot class."""

    config: BaseConfig

    async def on_ready(self) -> None:
        """Bot ready event."""
        print(f"{self.user.name} has connected to Discord!")
