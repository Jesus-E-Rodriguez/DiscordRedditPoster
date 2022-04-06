"""Collection of discord cogs."""
from discord import Embed
from discord.ext import tasks, commands

from .mixins import Reddit
from .utils import (
    create_table,
    create_discord_embed,
    format_input,
    format_exception,
    from_config,
    EXCEPTIONS,
)

import logging


class RedditCommands(commands.Cog):
    """Main Bot class"""

    def __init__(self, bot: commands.Bot, *args, **kwargs) -> None:
        """Init method."""
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.reddit = Reddit(
            client_id=bot.config.REDDIT_CLIENT_ID,
            client_secret=bot.config.REDDIT_CLIENT_SECRET,
            filename=bot.config.FILENAME,
        )
        self.fetch_subscriptions.start()

    def cog_unload(self) -> None:
        """Unload cog."""
        self.fetch_subscriptions.cancel()

    @commands.command(name="sub", help="Subscribe to a subreddit")
    @from_config(commands.has_any_role, "DISCORD_BOT_ADVANCED_COMMANDS_ROLES")
    async def add_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        """Add a subreddit to subscriptions."""
        commands.has_any_role()
        message = f"Subrredit {subreddit} has been subcribed!"
        if self.reddit.subreddit_is_banned(subreddit=subreddit):
            message = f"Subreddit {subreddit} is banned and cannot be subscribed to!"
        elif self.reddit.subreddit_is_subscribed(
            channel_id=ctx.channel.id, subreddit=subreddit
        ):
            message = f"Subreddit {subreddit} is already subscribed!"
        elif await self.reddit.subreddit_exists(subreddit=subreddit):
            self.reddit.manage_subscription(
                channel_id=ctx.channel.id,
                subreddit=subreddit,
                callback=self.fetch_subscriptions.restart,
            )
        else:
            message = f"Subreddit {subreddit} does not exist!"
        await ctx.send(message)

    @commands.command(name="unsub", help="Unsubscribe from a subreddit")
    @from_config(commands.has_any_role, "DISCORD_BOT_ADVANCED_COMMANDS_ROLES")
    async def remove_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been removed!"
        if self.reddit.subreddit_is_subscribed(
            channel_id=ctx.channel.id, subreddit=subreddit
        ):
            self.reddit.manage_subscription(
                channel_id=ctx.channel.id,
                subreddit=subreddit,
                subscribe=False,
                callback=self.fetch_subscriptions.restart,
            )
        else:
            message = f"Subreddit {subreddit} is not subscribed!"
        await ctx.send(message)

    @commands.command(name="fetch", help="Fetch new posts from a specified subreddit")
    @from_config(
        commands.has_any_role,
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES",
        "DISCORD_BOT_NORMAL_COMMANDS_ROLES",
    )
    async def fetch_from_sub(
        self,
        ctx: commands.context.Context,
        subreddit_or_redditor: format_input,
        *submission_name_args,
    ) -> None:
        """Fetch a post from a subreddit and post to discord."""
        async with ctx.typing():
            if self.reddit.subreddit_is_banned(subreddit=subreddit_or_redditor):
                await ctx.send(
                    f"Subreddit {subreddit_or_redditor} is banned and cannot be fetched!"
                )

            elif submissions := await self.reddit.fetch(
                subreddit_or_redditor=subreddit_or_redditor,
                search_term="+".join(submission_name_args),
            ):
                [
                    await ctx.send(embed=await create_discord_embed(sub))
                    async for sub in submissions
                ]
            else:
                await ctx.send(f"No results found for {subreddit_or_redditor}!")

    @commands.command(name="subbed", help="List all subscribed subreddits")
    @from_config(
        commands.has_any_role,
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES",
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES",
    )
    async def view_subbed(self, ctx: commands.context.Context) -> None:
        """View the list of subscribed subreddits."""
        try:
            channels, subreddits = zip(
                *(
                    (self.bot.get_channel(channel_id).name, subreddit)
                    for channel_id, subreddit in self.reddit.get_subscriptions()
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
    @from_config(commands.has_any_role, "DISCORD_BOT_ADVANCED_COMMANDS_ROLES")
    async def ban_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been banned!"
        self.reddit.manage_moderation(subreddit=subreddit)
        await ctx.send(message)

    @commands.command(name="banned", help="List all banned subreddits")
    @from_config(
        commands.has_any_role,
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES",
        "DISCORD_BOT_NORMAL_COMMANDS_ROLES",
    )
    async def view_banned(self, ctx: commands.context.Context) -> None:
        if banned := self.reddit.subreddits.get("banned", []):
            table = create_table({"Subreddits": banned})
            embed = Embed.from_dict(
                {"title": "Banned Subreddits", "description": f"```\n{table}\n```"}
            )
            await ctx.send(embed=embed)
        await ctx.send("No subreddits are currently banned!")

    @commands.command(name="unban", help="Unban a subreddit")
    @from_config(
        commands.has_any_role,
        "DISCORD_BOT_ADVANCED_COMMANDS_ROLES",
        "DISCORD_BOT_NORMAL_COMMANDS_ROLES",
    )
    async def unban_subreddit(
        self, ctx: commands.context.Context, subreddit: format_input
    ) -> None:
        message = f"Subreddit {subreddit} has been unbanned!"
        self.reddit.manage_moderation(
            subreddit=subreddit, ban=False, callback=self.fetch_subscriptions.restart
        )
        await ctx.send(message)

    @tasks.loop()
    async def fetch_subscriptions(self) -> None:
        """Fetch submissions from subscribed subreddits."""
        if subreddits := {
            subreddit: channel_id
            for channel_id, subreddit in self.reddit.get_subscriptions()
        }:
            subscribed = await self.reddit.request.subreddit(
                "+".join(subreddits.keys())
            )
            try:
                async for submission in subscribed.stream.submissions(
                    skip_existing=True
                ):
                    subreddit = submission.subreddit.display_name
                    channel_id = subreddits.get(subreddit)
                    if channel := self.bot.get_channel(channel_id):
                        async with channel.typing():
                            await channel.send(
                                embed=await create_discord_embed(submission)
                            )
            except (Exception, *EXCEPTIONS) as error:
                if error not in EXCEPTIONS:
                    logger = logging.getLogger(self.bot.config.LOGFILENAME)
                    logger.error(format_exception(error=error))
                self.fetch_subscriptions.restart()


class CommandsErrorHandler(commands.Cog):
    """Error handling for the bot."""

    def __init__(self, bot: commands.Bot) -> None:
        """Init method."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """A global error handler cog."""
        message = "Oh no! Something went wrong while running the command!"

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

        logger = logging.getLogger(self.bot.config.LOGFILENAME)
        logger.error(format_exception(error=error))
        await ctx.send(message)
