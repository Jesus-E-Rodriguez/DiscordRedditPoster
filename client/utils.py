"""Collection of utility functions."""

from datetime import datetime
from typing import Any, Union

import html2text
from asyncpraw.models import Submission
from discord import Embed
import tabulate


async def create_discord_embed(
    submission: Submission, color: Union[int, str] = 0x00FF00
) -> Embed:
    html = html2text.HTML2Text()
    html.ignore_links = True
    description = f"{html.handle(submission.selftext_html)[:150]}..."
    await submission.author.load()
    return Embed.from_dict(
        {
            "title": submission.title,
            "url": submission.url,
            "description": description,
            "author": {
                "name": submission.author.name,
                "icon_url": submission.author.icon_img,
            },
            "timestamp": datetime.fromtimestamp(submission.created).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "color": color,
        }
    )


def create_table(data: Any, tablefmt: str = "fancy_grid", **kwargs) -> str:
    """Create a str table from data."""
    return tabulate.tabulate(data, headers="keys", tablefmt=tablefmt, **kwargs)


def format_input(string: str) -> str:
    """Format input to be used."""
    return string.replace("r/", "").lower()
