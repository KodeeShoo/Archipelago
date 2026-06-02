from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from .world import WesnothWorld


def set_rules(world: WesnothWorld) -> None:
    world.set_completion_rule(lambda state: can_finish_campaign(world, state))


def can_finish_campaign(world: WesnothWorld, state: CollectionState) -> bool:
    return True
