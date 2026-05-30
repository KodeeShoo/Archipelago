from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import WesnothWorld


BASE_ID = 875_000


ITEM_NAME_TO_ID: dict[str, int] = {
    "Recruit: Spearman": BASE_ID + 1,
    "Recruit: Bowman": BASE_ID + 2,
    "Recruit: Mage": BASE_ID + 3,
    "Recruit: Horseman": BASE_ID + 4,
    "Recruit: Merman Fighter": BASE_ID + 5,
    "Elvish Alliance": BASE_ID + 6,
    "Dwarvish Alliance": BASE_ID + 7,
    "Veteran Leadership": BASE_ID + 8,
    "Extra Gold": BASE_ID + 20,
    "Recall Slot": BASE_ID + 21,
    "Healing Draught": BASE_ID + 22,
    "Supply Cache": BASE_ID + 40,
    "Scout Report": BASE_ID + 41,
    "Ambush": BASE_ID + 60,
}


DEFAULT_CLASSIFICATION: dict[str, ItemClassification] = {
    "Recruit: Spearman": ItemClassification.progression,
    "Recruit: Bowman": ItemClassification.progression,
    "Recruit: Mage": ItemClassification.progression,
    "Recruit: Horseman": ItemClassification.progression,
    "Recruit: Merman Fighter": ItemClassification.progression,
    "Elvish Alliance": ItemClassification.progression,
    "Dwarvish Alliance": ItemClassification.progression,
    "Veteran Leadership": ItemClassification.progression,
    "Extra Gold": ItemClassification.useful,
    "Recall Slot": ItemClassification.useful,
    "Healing Draught": ItemClassification.useful,
    "Supply Cache": ItemClassification.filler,
    "Scout Report": ItemClassification.filler,
    "Ambush": ItemClassification.trap,
}


PROGRESSION_ITEMS = [
    "Recruit: Spearman",
    "Recruit: Bowman",
    "Recruit: Mage",
    "Recruit: Horseman",
    "Recruit: Merman Fighter",
    "Elvish Alliance",
    "Dwarvish Alliance",
    "Veteran Leadership",
]

USEFUL_ITEMS = [
    "Extra Gold",
    "Extra Gold",
    "Recall Slot",
    "Healing Draught",
]

FILLER_ITEMS = ["Supply Cache", "Scout Report"]
TRAP_ITEMS = ["Ambush"]


class WesnothItem(Item):
    game = "Battle for Wesnoth"


def create_item(world: WesnothWorld, name: str) -> WesnothItem:
    return WesnothItem(name, DEFAULT_CLASSIFICATION[name], ITEM_NAME_TO_ID[name], world.player)


def get_filler_item_name(world: WesnothWorld) -> str:
    if world.random.randint(1, 100) <= world.options.ambush_trap_chance.value:
        return world.random.choice(TRAP_ITEMS)
    return world.random.choice(FILLER_ITEMS)


def create_itempool(world: WesnothWorld) -> None:
    item_names = [*PROGRESSION_ITEMS, *USEFUL_ITEMS]
    itempool = [world.create_item(name) for name in item_names]

    unfilled_locations = world.multiworld.get_unfilled_locations(world.player)
    filler_count = len(unfilled_locations) - len(itempool)
    itempool.extend(world.create_filler() for _ in range(filler_count))

    world.multiworld.itempool += itempool
