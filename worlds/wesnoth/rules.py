from __future__ import annotations

from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from .world import WesnothWorld


def has_any(state: CollectionState, player: int, names: set[str]) -> bool:
    return any(state.has(name, player) for name in names)


def set_rules(world: WesnothWorld) -> None:
    player = world.player

    set_rule(world.get_location("Tutorial: First Level Up"), lambda state: state.has("Recruit: Bowman", player))
    set_rule(
        world.get_location("Tutorial: Enemy Leader Defeated"),
        lambda state: state.has("Recruit: Mage", player),
    )

    world.set_completion_rule(lambda state: can_finish_campaign(world, state))


def can_finish_campaign(world: WesnothWorld, state: CollectionState) -> bool:
    return state.can_reach("Tutorial: Enemy Leader Defeated", "Location", world.player)
