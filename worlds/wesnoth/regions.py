from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from . import locations

if TYPE_CHECKING:
    from .world import WesnothWorld


REGION_NAMES = [
    "Menu",
    "Campaign Start",
]


CONNECTIONS = [
    ("Menu", "Campaign Start", "Start Campaign"),
]


def create_regions(world: WesnothWorld) -> None:
    regions = [Region(region_name, world.player, world.multiworld) for region_name in REGION_NAMES]
    world.multiworld.regions += regions

    for source, target, entrance_name in CONNECTIONS:
        world.get_region(source).connect(world.get_region(target), entrance_name)

    locations.add_locations(world)
