from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


LOCATION_NAME_TO_ID: dict[str, int] = {
    "Tutorial: Secure the Keep": BASE_ID + 1,
    "Tutorial: First Village": BASE_ID + 2,
    "Tutorial: First Level Up": BASE_ID + 3,
    "Northern Outpost: Commander Defeated": BASE_ID + 4,
    "Northern Outpost: Hidden Cache": BASE_ID + 5,
    "Forest Pass: Elvish Ally Recruited": BASE_ID + 6,
    "Forest Pass: Necromancer Defeated": BASE_ID + 7,
    "River Crossing: First Merman Recruited": BASE_ID + 8,
    "River Crossing: Bridge Secured": BASE_ID + 9,
    "Siege Camp: Supplies Captured": BASE_ID + 10,
    "Dwarven Road: Dwarvish Ally Recruited": BASE_ID + 11,
    "Dwarven Road: Mine Cleared": BASE_ID + 12,
    "City Siege: Gate Opened": BASE_ID + 13,
    "City Siege: Enemy Leader Defeated": BASE_ID + 14,
    "Crownlands: Three Armies United": BASE_ID + 15,
    "Crownlands: Final Enemy Defeated": BASE_ID + 16,
    "Challenge: No Leader Deaths": BASE_ID + 17,
    "Challenge: Par Turn Bonus": BASE_ID + 18,
}


LOCATION_GROUPS = {
    "Tutorial": {
        "Tutorial: Secure the Keep",
        "Tutorial: First Village",
        "Tutorial: First Level Up",
    },
    "Act 1": {
        "Northern Outpost: Commander Defeated",
        "Northern Outpost: Hidden Cache",
    },
    "Act 2": {
        "Forest Pass: Elvish Ally Recruited",
        "Forest Pass: Necromancer Defeated",
        "River Crossing: First Merman Recruited",
        "River Crossing: Bridge Secured",
        "Siege Camp: Supplies Captured",
    },
    "Act 3": {
        "Dwarven Road: Dwarvish Ally Recruited",
        "Dwarven Road: Mine Cleared",
        "City Siege: Gate Opened",
        "City Siege: Enemy Leader Defeated",
    },
    "Finale": {
        "Crownlands: Three Armies United",
        "Crownlands: Final Enemy Defeated",
    },
    "Challenges": {
        "Challenge: No Leader Deaths",
        "Challenge: Par Turn Bonus",
    },
}


REGION_LOCATIONS = {
    "Campaign Start": [
        "Tutorial: Secure the Keep",
        "Tutorial: First Village",
        "Tutorial: First Level Up",
    ],
    "Northern Outpost": [
        "Northern Outpost: Commander Defeated",
        "Northern Outpost: Hidden Cache",
    ],
    "Forest Pass": [
        "Forest Pass: Elvish Ally Recruited",
        "Forest Pass: Necromancer Defeated",
    ],
    "River Crossing": [
        "River Crossing: First Merman Recruited",
        "River Crossing: Bridge Secured",
    ],
    "Siege Camp": [
        "Siege Camp: Supplies Captured",
    ],
    "Dwarven Road": [
        "Dwarven Road: Dwarvish Ally Recruited",
        "Dwarven Road: Mine Cleared",
    ],
    "City Siege": [
        "City Siege: Gate Opened",
        "City Siege: Enemy Leader Defeated",
    ],
    "Crownlands": [
        "Crownlands: Three Armies United",
        "Crownlands: Final Enemy Defeated",
        "Challenge: No Leader Deaths",
        "Challenge: Par Turn Bonus",
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
