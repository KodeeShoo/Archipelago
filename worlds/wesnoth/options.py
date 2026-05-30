from dataclasses import dataclass

from Options import DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range


class AmbushTrapChance(Range):
    """Unused in the smoke-test item pool. Reserved for later trap support."""

    display_name = "Ambush Trap Chance"
    range_start = 0
    range_end = 100
    default = 10


class StartingGold(Range):
    """Extra gold the Wesnoth add-on should grant when the campaign starts."""

    display_name = "Starting Gold"
    range_start = 0
    range_end = 500
    default = 100


class EnableBridgeFile(DefaultOnToggle):
    """Write bridge state for an external client to read."""

    display_name = "Enable Bridge File"


@dataclass
class WesnothOptions(PerGameCommonOptions):
    ambush_trap_chance: AmbushTrapChance
    starting_gold: StartingGold
    enable_bridge_file: EnableBridgeFile


option_groups = [
    OptionGroup(
        "Campaign Options",
        [StartingGold],
    ),
    OptionGroup(
        "Bridge Options",
        [EnableBridgeFile],
    ),
    OptionGroup(
        "Item Pool Options",
        [AmbushTrapChance],
    ),
]


option_presets = {
    "starter": {
        "ambush_trap_chance": 0,
        "starting_gold": 150,
        "enable_bridge_file": True,
    },
    "campaign": {
        "ambush_trap_chance": 10,
        "starting_gold": 100,
        "enable_bridge_file": True,
    },
}
