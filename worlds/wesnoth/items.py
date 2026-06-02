from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from . import two_brothers

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


ITEM_NAME_TO_ID: dict[str, int] = {
    name: BASE_ID + index
    for index, name in enumerate(two_brothers.all_item_names(), start=1)
}

DEFAULT_CLASSIFICATION: dict[str, ItemClassification] = {
    name: ItemClassification.progression
    for name in ITEM_NAME_TO_ID
}
DEFAULT_CLASSIFICATION[two_brothers.FILLER_ITEM_NAME] = ItemClassification.filler


class WesnothItem(Item):
    game = "Battle for Wesnoth"


def create_item(world: WesnothWorld, name: str) -> WesnothItem:
    return WesnothItem(name, DEFAULT_CLASSIFICATION[name], ITEM_NAME_TO_ID[name], world.player)


def get_filler_item_name(world: WesnothWorld) -> str:
    return two_brothers.FILLER_ITEM_NAME


def create_itempool(world: WesnothWorld) -> None:
    active_items = getattr(world, "active_item_names", None)
    precollected = set(getattr(world, "precollected_item_names", []))
    if active_items is None:
        two_brothers.generate_two_brothers_slot(world)
        active_items = world.active_item_names
        precollected = set(world.precollected_item_names)

    for name in sorted(precollected):
        world.multiworld.push_precollected(world.create_item(name))

    itempool = [world.create_item(name) for name in active_items if name not in precollected]
    unfilled_locations = world.multiworld.get_unfilled_locations(world.player)
    filler_count = len(unfilled_locations) - len(itempool)
    itempool.extend(world.create_filler() for _ in range(filler_count))

    world.multiworld.itempool += itempool
