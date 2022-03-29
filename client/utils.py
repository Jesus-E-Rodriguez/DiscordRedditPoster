"""Collection of utility functions."""

from datetime import datetime
from typing import Any, Union, Dict, Optional, Iterable

import html2text
import tabulate
from asyncpraw.models import Submission
from discord import Embed


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
            attributes[value] = getattr(obj, key)
    if attrs:
        for attribute in attrs:
            attributes[attribute] = getattr(obj, attribute)
    return attributes


async def create_discord_embed(
    submission: Submission, color: Union[int, str] = 0xFF4500
) -> Embed:
    """Create a discord embed from a Reddit submission."""
    embed_dict = {
        "color": color,
        **get_attributes(
            obj=submission,
            remap={"selftext_html": "description", "shortlink": "url"},
            attrs=("title", "created"),
        ),
    }

    embed_dict["timestamp"] = datetime.fromtimestamp(
        embed_dict.get("created")
    ).strftime("%Y-%m-%dT%H:%M:%S")

    if description := embed_dict.get("description"):
        html = html2text.HTML2Text()
        html.ignore_links = True
        embed_dict["description"] = f"{html.handle(description)[:150]}..."

    await submission.author.load()
    if name := getattr(submission.author, "name"):
        embed_dict.setdefault("author", {})["name"] = name
    if icon_url := getattr(submission.author, "icon_img"):
        embed_dict.setdefault("author", {})["icon_url"] = icon_url

    return Embed.from_dict(embed_dict)


def create_table(data: Any, tablefmt: str = "fancy_grid", **kwargs) -> str:
    """Create a str table from data."""
    return tabulate.tabulate(data, headers="keys", tablefmt=tablefmt, **kwargs)


def format_input(string: str) -> str:
    """Format input to be used."""
    return string.replace("r/", "").lower()
