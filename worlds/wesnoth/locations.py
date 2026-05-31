from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


LOCATION_NAME_TO_ID: dict[str, int] = {
    "Tutorial: First Village": BASE_ID + 1,
    "Tutorial: First Level Up": BASE_ID + 2,
    "Tutorial: Training Chest": BASE_ID + 3,
    "Tutorial: Armory Chest": BASE_ID + 4,
}


LOCATION_GROUPS = {
    "Tutorial": {
        "Tutorial: First Village",
        "Tutorial: First Level Up",
        "Tutorial: Training Chest",
        "Tutorial: Armory Chest",
    },
}


REGION_LOCATIONS = {
    "Campaign Start": [
        "Tutorial: First Village",
        "Tutorial: First Level Up",
        "Tutorial: Training Chest",
        "Tutorial: Armory Chest",
    ],
}


class WesnothLocation(Location):
    game = "Battle for Wesnoth"


def add_locations(world: WesnothWorld) -> None:
    for region_name, location_names in REGION_LOCATIONS.items():
        region = world.get_region(region_name)
        region.add_locations(
            {name: LOCATION_NAME_TO_ID[name] for name in location_names},
            WesnothLocation,
        )
