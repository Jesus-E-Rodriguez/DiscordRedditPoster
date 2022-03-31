"""Collection of models."""
from typing import Optional, Union

from asyncpraw import Reddit
from asyncpraw.models import ListingGenerator, Subreddit, Submission
from asyncpraw.models.listing.mixins.redditor import SubListing

from client.utils import refined_filter


class RedditHelper:
    """Collection of submissions."""

    def __init__(
        self, reddit: Reddit, method: Optional[str] = "subreddit", *args, **kwargs
    ) -> None:
        """Init method."""
        self._reddit = reddit
        if method.lower() not in ("subreddit", "redditor"):
            raise ValueError("Method must be either subreddit or redditor")
        self._method = method.lower()
        self.sorting_options = ("new", "hot", "top", "rising", "controversial")
        super().__init__(*args, **kwargs)

    async def get(
        self, query: str, fetch: Optional[bool] = True, *args, **kwargs
    ) -> Union[Subreddit, SubListing]:
        response = await getattr(self._reddit, self._method)(
            query,
            fetch=fetch,
            *args,
            **kwargs,
        )
        if self._method != "subreddit":
            response = getattr(response, "submissions")
        return response

    async def filter(
        self,
        query: str,
        search_term: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = 1,
        *args,
        **kwargs,
    ) -> Union[ListingGenerator, Submission]:
        if sort and sort not in self.sorting_options:
            raise ValueError(f"Invalid sort option: {sort}")

        if search_term and sort:
            raise ValueError("Cannot specify both search and sort")

        response = await self.get(query=query, *args, **kwargs)

        if search_term:
            response = refined_filter(search_term=search_term, submissions=response)
        else:
            response = getattr(response, sort)(limit=limit)
        return response
