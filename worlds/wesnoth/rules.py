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

    set_rule(
        world.get_location("Tutorial: First Level Up"),
        lambda state: has_any(state, player, {"Recruit: Spearman", "Recruit: Bowman"}),
    )
    set_rule(
        world.get_location("Northern Outpost: Commander Defeated"),
        lambda state: state.has_all({"Recruit: Spearman", "Recruit: Bowman"}, player),
    )
    set_rule(
        world.get_location("Northern Outpost: Hidden Cache"),
        lambda state: has_any(state, player, {"Recruit: Mage", "Recruit: Horseman"}),
    )
    set_rule(
        world.get_location("Forest Pass: Elvish Ally Recruited"),
        lambda state: state.has("Recruit: Bowman", player),
    )
    set_rule(
        world.get_location("Forest Pass: Necromancer Defeated"),
        lambda state: state.has_all({"Recruit: Mage", "Elvish Alliance"}, player),
    )
    set_rule(
        world.get_location("River Crossing: First Merman Recruited"),
        lambda state: state.has("Recruit: Spearman", player),
    )
    set_rule(
        world.get_location("River Crossing: Bridge Secured"),
        lambda state: state.has("Recruit: Merman Fighter", player),
    )
    set_rule(
        world.get_location("Siege Camp: Supplies Captured"),
        lambda state: has_any(state, player, {"Recruit: Horseman", "Veteran Leadership"}),
    )
    set_rule(
        world.get_location("Dwarven Road: Dwarvish Ally Recruited"),
        lambda state: state.has("Dwarvish Alliance", player),
    )
    set_rule(
        world.get_location("Dwarven Road: Mine Cleared"),
        lambda state: state.has_all({"Dwarvish Alliance", "Recruit: Mage"}, player),
    )
    set_rule(
        world.get_location("City Siege: Gate Opened"),
        lambda state: state.has_all({"Dwarvish Alliance", "Veteran Leadership"}, player),
    )
    set_rule(
        world.get_location("City Siege: Enemy Leader Defeated"),
        lambda state: state.has_all({"Recruit: Horseman", "Veteran Leadership"}, player),
    )
    set_rule(
        world.get_location("Crownlands: Three Armies United"),
        lambda state: state.has_all({"Elvish Alliance", "Dwarvish Alliance", "Recruit: Merman Fighter"}, player),
    )
    set_rule(
        world.get_location("Crownlands: Final Enemy Defeated"),
        lambda state: can_finish_campaign(world, state),
    )
    set_rule(
        world.get_location("Challenge: No Leader Deaths"),
        lambda state: state.has("Veteran Leadership", player),
    )
    set_rule(
        world.get_location("Challenge: Par Turn Bonus"),
        lambda state: state.has_all({"Recruit: Horseman", "Veteran Leadership"}, player),
    )

    world.set_completion_rule(lambda state: can_finish_campaign(world, state))


def can_finish_campaign(world: WesnothWorld, state: CollectionState) -> bool:
    player = world.player
    required = {
        "Recruit: Spearman",
        "Recruit: Bowman",
        "Recruit: Mage",
        "Elvish Alliance",
        "Dwarvish Alliance",
        "Veteran Leadership",
    }
    if not state.has_all(required, player):
        return False
    if world.options.goal_requires_challenges:
        return state.can_reach("Challenge: No Leader Deaths", "Location", player) and state.can_reach(
            "Challenge: Par Turn Bonus", "Location", player
        )
    return True
