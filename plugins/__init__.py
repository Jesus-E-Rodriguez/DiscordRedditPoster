import importlib
import inspect
import os

from discord.ext import commands

Cogs = []
for module in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if module == "__init__.py" or module[-3:] != ".py":
        continue
    mdl = importlib.import_module(f"plugins.{module[:-3]}")
    Cogs.extend(
        obj
        for name, obj in inspect.getmembers(object=mdl, predicate=inspect.isclass)
        if issubclass(obj, commands.Cog)
    )
del module
