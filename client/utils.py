"""Collection of utility functions."""
import traceback
from datetime import datetime
from typing import Any, Union, Dict, Optional, Iterable, Generator

import html2text
import tabulate
from asyncpraw.models import Submission, Subreddit
from asyncpraw.models.listing.mixins.redditor import SubListing
from discord import Embed

# fix issue with fetching the latest submission


async def refined_filter(
    search_term: str,
    submissions: Union[Subreddit, SubListing],
    find_closest_match: Optional[bool] = True,
    *args,
    **kwargs,
) -> Generator[Submission, None, None]:
    """Filter submissions by keyword."""
    iteration_count = 0
    async for submission in submissions.search(
        search_term,
        time_filter="all",
        *args,
        **kwargs,
    ):
        q = " ".join(search_term.split("+")).lower()
        if q in submission.title.lower():
            if find_closest_match and iteration_count > 0:
                break
            iteration_count += 1
            yield submission


def get_attributes(
    obj: Any,
    remap: Optional[
        Dict[
            str,
            str,
        ]
    ] = None,
    attrs: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Extract a list of attributes from a Reddit object."""
    if not remap and not attrs:
        raise ValueError("Must provide remap or attributes.")
    attributes = {}
    if remap:
        for key, value in remap.items():
            if a := getattr(obj, key):
                attributes[value] = a

    if attrs:
        for attribute in attrs:
            if a := getattr(obj, attribute):
                attributes[attribute] = a
    return attributes


async def create_discord_embed(
    submission: Submission,
    color: Union[int, str] = 0xFF4500,
    max_title_length: Optional[int] = 256,
    max_description_length: Optional[int] = 150,
) -> Embed:
    """Create a discord embed from a Reddit submission."""
    embed_dict = {
        "color": color,
        **get_attributes(
            obj=submission,
            remap={
                "selftext_html": "description",
                "shortlink": "url",
                "created": "timestamp",
            },
            attrs=["title"],
        ),
    }

    if timestamp := embed_dict.get("timestamp"):
        embed_dict["timestamp"] = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

    if title := embed_dict.get("title"):
        if len(title) > max_title_length:
            embed_dict["title"] = title[:max_title_length]

    if description := embed_dict.get("description"):
        html = html2text.HTML2Text()
        html.ignore_links = True
        description = html.handle(description)
        if len(description) > max_description_length:
            description = f"{description[:max_description_length]}..."
        embed_dict["description"] = description

    await submission.author.load()
    if name := getattr(submission.author, "name"):
        embed_dict.setdefault("author", {})["name"] = name
    if icon_url := getattr(submission.author, "icon_img"):
        embed_dict.setdefault("author", {})["icon_url"] = icon_url

    return Embed.from_dict(embed_dict)


def format_exception(error: Exception) -> str:
    """Format an exception."""
    return "In {0}:\n{1}".format(
        {traceback.extract_stack(None, 2)[0][2]},
        " ".join(traceback.format_exception(type(error), error, error.__traceback__)),
    )


def create_table(data: Any, tablefmt: str = "fancy_grid", **kwargs) -> str:
    """Create a str table from data."""
    return tabulate.tabulate(data, headers="keys", tablefmt=tablefmt, **kwargs)


def format_input(string: str) -> str:
    """Format input to be used."""
    return string.replace("r/", "").lower()
