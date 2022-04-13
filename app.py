"""Main app."""
from typing import Optional, Iterable

from client.bot import Bot
from client.cogs import RedditCommands, CommandsErrorHandler
import plugins
import config


def create_bot(
    configuration: object, cogs: Optional[Iterable] = None, command_prefix: str = "!"
) -> Bot:
    """Create bot."""
    bot = Bot(command_prefix=command_prefix)
    bot.config = configuration
    if cogs:
        [bot.add_cog(cog(bot=bot)) for cog in cogs]
    return bot


if __name__ == "__main__":
    """Main function."""
    commands = (
        RedditCommands,
        CommandsErrorHandler,
        *plugins.Cogs,
    )
    discord_bot = create_bot(
        configuration=config.get_config(config.ENVIRONMENT), cogs=commands
    )
    discord_bot.run(discord_bot.config.DISCORD_BOT_TOKEN)
