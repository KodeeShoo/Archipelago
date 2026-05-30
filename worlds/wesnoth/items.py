from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


ITEM_NAME_TO_ID: dict[str, int] = {
    "Recruit: Bowman": BASE_ID + 1,
    "Recruit: Mage": BASE_ID + 2,
    "Extra Gold": BASE_ID + 3,
}


DEFAULT_CLASSIFICATION: dict[str, ItemClassification] = {
    "Recruit: Bowman": ItemClassification.progression,
    "Recruit: Mage": ItemClassification.progression,
    "Extra Gold": ItemClassification.useful,
}


PROGRESSION_ITEMS = ["Recruit: Bowman", "Recruit: Mage"]
USEFUL_ITEMS = ["Extra Gold"]
FILLER_ITEMS = ["Extra Gold"]


class WesnothItem(Item):
    game = "Battle for Wesnoth"


def create_item(world: WesnothWorld, name: str) -> WesnothItem:
    return WesnothItem(name, DEFAULT_CLASSIFICATION[name], ITEM_NAME_TO_ID[name], world.player)


def get_filler_item_name(world: WesnothWorld) -> str:
    return world.random.choice(FILLER_ITEMS)


def create_itempool(world: WesnothWorld) -> None:
    item_names = [*PROGRESSION_ITEMS, *USEFUL_ITEMS]
    itempool = [world.create_item(name) for name in item_names]

    unfilled_locations = world.multiworld.get_unfilled_locations(world.player)
    filler_count = len(unfilled_locations) - len(itempool)
    itempool.extend(world.create_filler() for _ in range(filler_count))

    world.multiworld.itempool += itempool
