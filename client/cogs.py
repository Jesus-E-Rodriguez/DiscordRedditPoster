"""Collection of discord cogs."""

import traceback
from logging import Logger
from typing import Optional

from discord import Embed
from discord.ext import tasks, commands

from settings import (
    DISCORD_BOT_ADVANCED_COMMANDS_ROLES,
    DISCORD_BOT_NORMAL_COMMANDS_ROLES,
)
from .mixins import RedditMixin
from .utils import create_table, create_discord_embed, format_input


class RedditCommands(commands.Cog, RedditMixin):
    """Main Bot class"""

    def __init__(self, bot: commands.Bot, *args, **kwargs) -> None:
        """Init method."""
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.fetch_subcriptions.start()

    def cog_unload(self) -> None:
        """Unload cog."""
        self.fetch_subcriptions.cancel()

    @commands.command(name="sub", help="Subscribe to a subreddit")
    @commands.has_any_role(*DISCORD_BOT_ADVANCED_COMMANDS_ROLES)
    async def add_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        """Add a subreddit to subscriptions."""
        message = f"Subrredit {subreddit} has been subcribed!"
        if self.subreddit_is_banned(subreddit=subreddit):
            message = f"Subreddit {subreddit} is banned and cannot be subscribed to!"
        elif self.subreddit_is_subscribed(
            channel_id=ctx.channel.id, subreddit=subreddit
        ):
            message = f"Subreddit {subreddit} is already subscribed!"
        elif await self.subreddit_exists(subreddit=subreddit):
            self.manage_subscription(
                channel_id=ctx.channel.id,
                subreddit=subreddit,
                callback=self.fetch_subcriptions.restart,
            )
        else:
            message = f"Subreddit {subreddit} does not exist!"
        await ctx.send(message)

    @commands.command(name="unsub", help="Unsubscribe from a subreddit")
    @commands.has_any_role(*DISCORD_BOT_ADVANCED_COMMANDS_ROLES)
    async def remove_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been removed!"
        if self.subreddit_is_subscribed(channel_id=ctx.channel.id, subreddit=subreddit):
            self.manage_subscription(
                channel_id=ctx.channel.id,
                subreddit=subreddit,
                subscribe=False,
                callback=self.fetch_subcriptions.restart,
            )
        else:
            message = f"Subreddit {subreddit} is not subscribed!"
        await ctx.send(message)

    @commands.command(name="fetch", help="Fetch new posts from a specified subreddit")
    @commands.has_any_role(
        *DISCORD_BOT_ADVANCED_COMMANDS_ROLES, *DISCORD_BOT_NORMAL_COMMANDS_ROLES
    )
    async def fetch_from_sub(
        self,
        ctx: commands.context.Context,
        subreddit_or_redditor: format_input,
        limit: Optional[int] = 1,
    ) -> None:
        """Fetch a post from a subreddit and post to discord."""
        async with ctx.typing():
            if not self.subreddit_is_banned(subreddit=subreddit_or_redditor):
                submissions = await self.fetch(
                    subreddit_or_redditor=subreddit_or_redditor, limit=limit
                )
                if submissions:
                    [
                        await ctx.send(embed=await create_discord_embed(sub))
                        async for sub in submissions
                    ]
                else:
                    await ctx.send(f"No results found for {subreddit_or_redditor}!")
            else:
                await ctx.send(
                    f"Subreddit {subreddit_or_redditor} is banned and cannot be fetched!"
                )

    @commands.command(name="subbed", help="List all subscribed subreddits")
    @commands.has_any_role(
        *DISCORD_BOT_ADVANCED_COMMANDS_ROLES, *DISCORD_BOT_NORMAL_COMMANDS_ROLES
    )
    async def view_subbed(self, ctx: commands.context.Context) -> None:
        """View the list of subscribed subreddits."""
        try:
            channels, subreddits = zip(
                *(
                    (self.bot.get_channel(channel_id).name, subreddit)
                    for channel_id, subreddit in self.get_subscriptions()
                )
            )
            table = create_table({"Channel": channels, "Subreddit": subreddits})
            embed = Embed.from_dict(
                {
                    "title": "Subscribed Subreddits",
                    "description": f"```\n{table}\n```",
                }
            )
            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send("No subreddits are currently subscribed!")

    @commands.command(name="ban", help="Ban a subreddit")
    @commands.has_any_role(*DISCORD_BOT_ADVANCED_COMMANDS_ROLES)
    async def ban_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been banned!"
        self.manage_moderation(subreddit=subreddit)
        await ctx.send(message)

    @commands.command(name="banned", help="List all banned subreddits")
    @commands.has_any_role(
        *DISCORD_BOT_ADVANCED_COMMANDS_ROLES, *DISCORD_BOT_NORMAL_COMMANDS_ROLES
    )
    async def view_banned(self, ctx: commands.context.Context) -> None:
        if banned := self.subreddits.get("banned", []):
            table = create_table({"Subreddits": banned})
            embed = Embed.from_dict(
                {"title": "Banned Subreddits", "description": f"```\n{table}\n```"}
            )
            await ctx.send(embed=embed)
        await ctx.send("No subreddits are currently banned!")

    @commands.command(name="unban", help="Unban a subreddit")
    @commands.has_any_role(
        *DISCORD_BOT_ADVANCED_COMMANDS_ROLES, *DISCORD_BOT_NORMAL_COMMANDS_ROLES
    )
    async def unban_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been unbanned!"
        self.manage_moderation(
            subreddit=subreddit, ban=False, callback=self.fetch_subcriptions.restart
        )
        await ctx.send(message)

    @tasks.loop()
    async def fetch_subcriptions(self) -> None:
        """Fetch submissions from subscribed subreddits."""
        if subreddits := {
            subreddit: channel_id for channel_id, subreddit in self.get_subscriptions()
        }:
            subscribed = await self.reddit.subreddit("+".join(subreddits.keys()))
            async for submission in subscribed.stream.submissions(skip_existing=True):
                subreddit = submission.subreddit.display_name
                channel_id = subreddits.get(subreddit)
                async with self.bot.get_channel(channel_id).typing():
                    await self.bot.get_channel(channel_id).send(
                        embed=await create_discord_embed(submission)
                    )

        self.fetch_subcriptions.stop()


class CommandsErrorHandler(commands.Cog):
    """Error handling for the bot."""

    def __init__(self, bot: commands.Bot, logger: Logger) -> None:
        """Init method."""
        self.bot = bot
        self.logger = logger

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """A global error handler cog."""

        if isinstance(error, commands.CommandNotFound):
            return  # Return because we don't want to show an error for every command not found
        elif isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
        elif isinstance(error, commands.MissingPermissions):
            message = "You are missing the required permissions to run this command!"
        elif isinstance(error, commands.MissingRole):
            message = "You are missing the required role to run this command!"
        elif isinstance(error, commands.UserInputError):
            message = "Something about your input was wrong, please check your input and try again!"
        else:
            self.logger.error(
                "In {0.command.qualified_name}:\n{1}".format(
                    ctx,
                    " ".join(
                        traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                    ),
                )
            )
            message = "Oh no! Something went wrong while running the command!"

        await ctx.send(message)
