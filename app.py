"""Main app."""

from client.bot import Bot
from client.cogs import RedditCommands, CommandsErrorHandler
from settings import (
    FILENAME,
    DISCORD_BOT_TOKEN,
    REDDIT_BOT_ID,
    REDDIT_BOT_SECRET,
    logger,
)


def main():
    """Main function."""
    bot = Bot(command_prefix="!")
    bot.add_cog(
        RedditCommands(
            bot=bot,
            filename=FILENAME,
            client_id=REDDIT_BOT_ID,
            client_secret=REDDIT_BOT_SECRET,
        )
    )
    bot.add_cog(CommandsErrorHandler(bot=bot, logger=logger))
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
