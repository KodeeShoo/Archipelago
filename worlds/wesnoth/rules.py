from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from .world import WesnothWorld


def set_rules(world: WesnothWorld) -> None:
    player = world.player

    set_rule(world.get_location("Tutorial: First Level Up"), lambda state: state.has("Recruit: Bowman", player))

    world.set_completion_rule(lambda state: can_finish_campaign(world, state))


def can_finish_campaign(world: WesnothWorld, state: CollectionState) -> bool:
    return state.has("Recruit: Mage", world.player)
