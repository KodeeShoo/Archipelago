from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, options, regions, rules, web


class WesnothWorld(World):
    """Battle for Wesnoth as a campaign-style Archipelago randomizer."""

    game = "Battle for Wesnoth"
    web = web.WesnothWebWorld()
    options_dataclass = options.WesnothOptions
    options: options.WesnothOptions

    item_name_to_id = items.ITEM_NAME_TO_ID
    item_name_groups = {
        "Recruit Unlocks": {
            "Recruit: Bowman",
            "Recruit: Mage",
        },
        "Attack Unlocks": {"Attack: Javelin"},
        "Support": {"Extra Gold"},
    }

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    location_name_groups = locations.LOCATION_GROUPS

    origin_region_name = "Menu"

    def create_regions(self) -> None:
        regions.create_regions(self)

    def create_items(self) -> None:
        items.create_itempool(self)

    def set_rules(self) -> None:
        rules.set_rules(self)

    def create_item(self, name: str) -> items.WesnothItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "item_name_to_id": self.item_name_to_id,
            "location_name_to_id": self.location_name_to_id,
            "starting_gold": self.options.starting_gold.value,
            "enable_bridge_file": bool(self.options.enable_bridge_file),
        }
