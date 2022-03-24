"""Collection of mixins."""

import json
from typing import Any, Dict, List, Union, Generator, Optional, Callable

import asyncpraw
import asyncprawcore
from asyncpraw.models import ListingGenerator, Redditor


class StorageMixin:
    """Mixin for storing data."""

    def __init__(self, filename: str = "data.json", *args, **kwargs) -> None:
        """Initialize the mixin."""
        self.filename = filename
        self.data = {}

    def set_data(
        self, data: Dict[str, Any], callback: Optional[Callable] = None
    ) -> None:
        """Saves the given data to the given filename in json format."""
        with open(self.filename, "w") as file:
            json.dump(data, file)
        if callback:
            callback()

    def get_data(
        self,
        default: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
    ) -> dict:
        """Retrieves data from the given filename as a serialized json object.
        Or creates a file with the default if it doesn't exist.
        """
        data = default or {}
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.set_data(data)
        if callback:
            callback()
        return data


class RedditMixin(StorageMixin):
    """Base mixin for reddit functionality."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        callback: Optional[Callable] = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the mixin."""
        super().__init__(*args, **kwargs)
        self.subreddits = self.get_data(
            default={"subscribed": [], "banned": []}, callback=callback
        )
        self.reddit = asyncpraw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=f"DISCORD_BOT:{client_id}:1.0",
        )
        self.sorting_options = ("new", "hot", "top", "rising", "controversial")

    async def subreddit_exists(self, subreddit: str) -> bool:
        """Check if a subreddit exists."""
        subreddit_exists = False
        try:
            _ = [
                sub
                async for sub in self.reddit.subreddits.search_by_name(
                    query=subreddit, exact=True
                )
            ]
            subreddit_exists = True
        except (asyncprawcore.NotFound, asyncprawcore.exceptions.Redirect):
            pass
        return subreddit_exists

    async def fetch(
        self,
        subreddit_or_redditor: str,
        search_type: Optional[str] = "subreddit",
        fetch: Optional[bool] = True,
        sort: Optional[str] = "new",
        limit: Optional[int] = None,
        *args,
        **kwargs,
    ) -> Union[ListingGenerator, List]:
        """Fetch posts from a subreddit or a redditor."""
        if sort not in self.sorting_options:
            raise ValueError(
                "Sort must be one of new, hot, top, rising or controversial."
            )

        if search_type not in ("subreddit", "redditor"):
            raise ValueError("Search type must be either subreddit or redditor.")

        if not await self.subreddit_exists(subreddit=subreddit_or_redditor):
            search_type = "redditor"

        results = []
        try:
            response = await getattr(self.reddit, search_type)(
                subreddit_or_redditor,
                fetch=fetch,
                *args,
                **kwargs,
            )
            if isinstance(response, Redditor):
                response = getattr(response, "submissions")
            results = getattr(response, sort)(limit=limit)
        except asyncprawcore.exceptions.Redirect:
            pass
        return results

    def manage_subscription(
        self,
        channel_id: int,
        subreddit: str,
        subscribe: bool = True,
        callback: Optional[Callable] = None,
    ) -> None:
        """Store the channel id and subreddit to subscribe to. Subscribes by default."""
        subscription = {"channel_id": channel_id, "subreddit": subreddit}
        if subscribe:
            self.subreddits.setdefault("subscribed", []).append(subscription)
        else:
            try:
                self.subreddits.get("subscribed", []).remove(subscription)
            except ValueError:
                pass
        self.set_data(self.subreddits, callback=callback)

    def manage_moderation(
        self,
        subreddit: str,
        ban: bool = True,
        callback: Optional[Callable] = None,
    ) -> None:
        """Manages bans. Bans by default."""
        if ban:
            [
                self.manage_subscription(**sub, subscribe=False)
                for sub in self.subreddits.get("subscribed", [])
                if sub.get("subreddit") == subreddit
            ]
            self.subreddits.setdefault("banned", []).append(subreddit)
        else:
            try:
                self.subreddits.get("banned", []).remove(subreddit)
            except ValueError:
                pass
        self.set_data(self.subreddits, callback=callback)

    def subreddit_is_banned(self, subreddit: str) -> bool:
        """Checks if the given subreddit is banned."""
        return subreddit in self.subreddits.get("banned", [])

    def subreddit_is_subscribed(self, channel_id: str, subreddit: str) -> bool:
        """Checks if the given subreddit is subscribed."""
        return any(
            channel_id == sub.get("channel_id") and subreddit == sub.get("subreddit")
            for sub in self.subreddits.get("subscribed", [])
        )

    def get_subscriptions(self) -> Generator:
        """Returns a generator with subscribed subreddits."""
        return (sub.values() for sub in self.subreddits.get("subscribed", []))
