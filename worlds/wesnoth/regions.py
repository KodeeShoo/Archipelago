from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from . import locations

if TYPE_CHECKING:
    from .world import WesnothWorld


REGION_NAMES = [
    "Menu",
    "Campaign Start",
    "Northern Outpost",
    "Forest Pass",
    "River Crossing",
    "Siege Camp",
    "Dwarven Road",
    "City Siege",
    "Crownlands",
]


CONNECTIONS = [
    ("Menu", "Campaign Start", "Start Campaign"),
    ("Campaign Start", "Northern Outpost", "March to Northern Outpost"),
    ("Northern Outpost", "Forest Pass", "Enter Forest Pass"),
    ("Forest Pass", "River Crossing", "Reach River Crossing"),
    ("River Crossing", "Siege Camp", "Reach Siege Camp"),
    ("Siege Camp", "Dwarven Road", "Take Dwarven Road"),
    ("Dwarven Road", "City Siege", "Begin City Siege"),
    ("City Siege", "Crownlands", "Enter Crownlands"),
]


def create_regions(world: WesnothWorld) -> None:
    regions = [Region(region_name, world.player, world.multiworld) for region_name in REGION_NAMES]
    world.multiworld.regions += regions

    for source, target, entrance_name in CONNECTIONS:
        world.get_region(source).connect(world.get_region(target), entrance_name)

    locations.add_locations(world)
