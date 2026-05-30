from dataclasses import dataclass

from Options import DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range, Toggle


class GoalRequiresChallenges(Toggle):
    """Require optional challenge checks before the campaign can be completed."""

    display_name = "Goal Requires Challenges"


class AmbushTrapChance(Range):
    """Percentage chance for filler rewards to become Ambush traps."""

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
    goal_requires_challenges: GoalRequiresChallenges
    ambush_trap_chance: AmbushTrapChance
    starting_gold: StartingGold
    enable_bridge_file: EnableBridgeFile


option_groups = [
    OptionGroup(
        "Campaign Options",
        [GoalRequiresChallenges, StartingGold],
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
        "goal_requires_challenges": False,
        "ambush_trap_chance": 0,
        "starting_gold": 150,
        "enable_bridge_file": True,
    },
    "campaign": {
        "goal_requires_challenges": False,
        "ambush_trap_chance": 10,
        "starting_gold": 100,
        "enable_bridge_file": True,
    },
}
