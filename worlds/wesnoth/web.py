from worlds.AutoWorld import WebWorld
from BaseClasses import Tutorial

from . import options


class WesnothWebWorld(WebWorld):
    theme = "grass"
    rich_text_options_doc = True
    option_groups = options.option_groups
    options_presets = options.option_presets
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide for setting up the Battle for Wesnoth Archipelago prototype.",
            "English",
            "setup_en.md",
            "setup/en",
            ["KodeeShoo"],
        )
    ]
