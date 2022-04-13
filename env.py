"""Collection of environment variable helper functions."""
import os
from distutils.util import strtobool
from typing import get_type_hints


class EnvMixin:
    """Mixin class for environmental variables."""

    def __init__(self) -> None:
        """Load environmental variables."""
        for field_name, field_type in get_type_hints(self).items():
            value = getattr(self, field_name, None)
            if value is not None:
                continue
            value = os.getenv(field_name)
            if field_type is bool:
                value = strtobool(value)
            elif field_type is list:
                value = [x.strip() for x in value.split(",")]
            setattr(self, field_name, value)

    def get(self, name: str, default: str = None) -> str:
        """Get an environmental variable."""
        return getattr(self, name, default)
