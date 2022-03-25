"""Collection of utility functions."""

from datetime import datetime
from typing import Any, Union, List, Dict

import html2text
from asyncpraw.models import Submission
from discord import Embed
import tabulate


def get_attributes(obj: Any, attributes: List[str]) -> Dict[str, Any]:
    """Extract a list of attributes from a Reddit object."""
    return {attribute: getattr(obj, attribute) for attribute in attributes}


async def create_discord_embed(
    submission: Submission, color: Union[int, str] = 0xFF4500
) -> Embed:
    """Create a discord embed from a Reddit submission."""
    embed_dict = {
        "color": color,
        **get_attributes(submission, ["title", "url", "selftext_html", "created"]),
    }

    if embed_dict.get("selftext_html"):
        html = html2text.HTML2Text()
        html.ignore_links = True
        embed_dict["description"] = f"{html.handle(submission.selftext_html)[:150]}..."

    if created := embed_dict.get("created"):
        embed_dict["timestamp"] = datetime.fromtimestamp(created).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

    await submission.author.load()
    embed_dict["author"] = {
        "name": submission.author.name,
        "icon_url": submission.author.icon_img,
    }

    return Embed.from_dict(embed_dict)


def create_table(data: Any, tablefmt: str = "fancy_grid", **kwargs) -> str:
    """Create a str table from data."""
    return tabulate.tabulate(data, headers="keys", tablefmt=tablefmt, **kwargs)


def format_input(string: str) -> str:
    """Format input to be used."""
    return string.replace("r/", "").lower()
