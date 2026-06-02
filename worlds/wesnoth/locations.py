from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

from . import two_brothers

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


LOCATION_NAME_TO_ID: dict[str, int] = {
    name: BASE_ID + index
    for index, name in enumerate(two_brothers.all_location_names(), start=1)
}


LOCATION_GROUPS = {
    "Two Brothers": set(LOCATION_NAME_TO_ID),
    "Scenario Completion": set(two_brothers.SCENARIO_COMPLETION_LOCATIONS),
    "Chests": set(two_brothers.CHEST_LOCATION_NAMES),
}


class WesnothLocation(Location):
    game = "Battle for Wesnoth"


def add_locations(world: WesnothWorld) -> None:
    active_locations = getattr(world, "active_location_names", None)
    if active_locations is None:
        two_brothers.generate_two_brothers_slot(world)
        active_locations = world.active_location_names

    region = world.get_region("Campaign Start")
    region.add_locations(
        {name: LOCATION_NAME_TO_ID[name] for name in active_locations},
        WesnothLocation,
    )
