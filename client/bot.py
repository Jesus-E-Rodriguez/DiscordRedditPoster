"""Collection of bots."""

from discord.ext import commands


class Bot(commands.Bot):
    """Main bot class."""

    async def on_ready(self) -> None:
        """Bot ready event."""
        print(f"{self.user.name} has connected to Discord!")
