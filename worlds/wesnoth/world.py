from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, options, regions, rules, two_brothers, web


class WesnothWorld(World):
    """Battle for Wesnoth as a campaign-style Archipelago randomizer."""

    game = "Battle for Wesnoth"
    web = web.WesnothWebWorld()
    options_dataclass = options.WesnothOptions
    options: options.WesnothOptions

    item_name_to_id = items.ITEM_NAME_TO_ID
    item_name_groups = {
        "Recruit Unlocks": {
            two_brothers.recruit_item_name(unit.unit_type)
            for unit in two_brothers.LEVEL_ONE_UNITS
        },
        "Attack Unlocks": {
            two_brothers.attack_item_name(unit.unit_type, attack.name, attack.range, attack.damage_type)
            for unit in two_brothers.LEVEL_ONE_UNITS
            for attack in unit.attacks
        },
    }

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    location_name_groups = locations.LOCATION_GROUPS

    origin_region_name = "Menu"

    roster_units: list[str]
    starting_unit: str
    starting_attack: str
    active_item_names: list[str]
    precollected_item_names: list[str]
    active_location_names: list[str]
    two_brothers_chests: list[dict[str, object]]

    def generate_early(self) -> None:
        two_brothers.generate_two_brothers_slot(self)

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
            "campaign": "two_brothers",
            "roster_units": self.roster_units,
            "starting_unit": self.starting_unit,
            "starting_attack": self.starting_attack,
            "active_items": self.active_item_names,
            "precollected_items": self.precollected_item_names,
            "active_locations": self.active_location_names,
            "two_brothers_chests": self.two_brothers_chests,
        }
