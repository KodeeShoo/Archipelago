from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import WesnothWorld


ROSTER_SIZE = 8
CHESTS_PER_SCENARIO = 15
FILLER_ITEM_NAME = "AP Supply Cache"

SCENARIO_COMPLETION_LOCATIONS = [
    "Two Brothers: Rooting Out a Mage Complete",
    "Two Brothers: The Chase Complete",
    "Two Brothers: Guarded Castle Complete",
]

FINAL_SCENARIO_ID = "04_Return_to_the_Village"

SCENARIO_MAPS = {
    "01_Rooting_Out_a_Mage": "01_Rooting_Out_a_Mage.map",
    "02_The_Chase": "02_The_Chase.map",
    "03_Guarded_Castle": "03_Guarded_Castle.map",
    "04_Return_to_the_Village": "04_Return_to_the_Village.map",
}

SCENARIO_DISPLAY_NAMES = {
    "01_Rooting_Out_a_Mage": "Rooting Out a Mage",
    "02_The_Chase": "The Chase",
    "03_Guarded_Castle": "Guarded Castle",
    "04_Return_to_the_Village": "Return to the Village",
}

SCENARIO_IDS = tuple(SCENARIO_MAPS)

CHEST_LOCATION_NAMES = [
    f"Two Brothers: {SCENARIO_DISPLAY_NAMES[scenario_id]} Chest {index:02d}"
    for scenario_id in SCENARIO_IDS
    for index in range(1, CHESTS_PER_SCENARIO + 1)
]


@dataclass(frozen=True)
class AttackData:
    name: str
    description: str
    damage_type: str
    range: str
    damage: int
    number: int
    icon: str = ""

    @property
    def item_name(self) -> str:
        return attack_item_name("", self.name, self.range, self.damage_type).replace("Attack:  - ", "Attack: ")


@dataclass(frozen=True)
class UnitData:
    unit_type: str
    attacks: tuple[AttackData, ...]

    @property
    def recruit_item_name(self) -> str:
        return recruit_item_name(self.unit_type)


LEVEL_ONE_UNITS: tuple[UnitData, ...] = (
    UnitData("Bowman", (AttackData("short sword", "short sword", "blade", "melee", 5, 2, "attacks/sword-human-short.png"), AttackData("bow", "bow", "pierce", "ranged", 6, 3))),
    UnitData("Cavalryman", (AttackData("sword", "sword", "blade", "melee", 6, 3, "attacks/sword-human.png"),)),
    UnitData("Dark Adept", (AttackData("chill wave", "chill wave", "cold", "ranged", 10, 2, "attacks/iceball.png"), AttackData("shadow wave", "shadow wave", "arcane", "ranged", 7, 2, "attacks/dark-missile.png"))),
    UnitData("Drake Burner", (AttackData("claws", "claws", "blade", "melee", 7, 2, "attacks/claws-drake.png"), AttackData("fire breath", "fire breath", "fire", "ranged", 6, 4, "attacks/fire-breath-drake.png"))),
    UnitData("Drake Clasher", (AttackData("war talon", "war talon", "blade", "melee", 5, 4, "attacks/scimitar.png"), AttackData("spear", "spear", "pierce", "melee", 6, 4, "attacks/spear.png"))),
    UnitData("Drake Fighter", (AttackData("war blade", "war blade", "blade", "melee", 7, 3, "attacks/warblade.png"), AttackData("fire breath", "fire breath", "fire", "ranged", 3, 3, "attacks/fire-breath-drake.png"))),
    UnitData("Drake Glider", (AttackData("slam", "slam", "impact", "melee", 6, 2, "attacks/slam-drake.png"), AttackData("fire breath", "fire breath", "fire", "ranged", 3, 3, "attacks/fire-breath-drake.png"))),
    UnitData("Dwarvish Fighter", (AttackData("axe", "axe", "blade", "melee", 7, 3), AttackData("hammer", "hammer", "impact", "melee", 8, 2, "attacks/hammer-dwarven.png"))),
    UnitData("Dwarvish Guardsman", (AttackData("spear", "spear", "pierce", "melee", 5, 3, "attacks/spear.png"), AttackData("javelin", "javelin", "pierce", "ranged", 6, 1, "attacks/javelin-human.png"))),
    UnitData("Dwarvish Scout", (AttackData("axe", "axe", "blade", "melee", 6, 3), AttackData("axe", "axe", "blade", "ranged", 8, 2))),
    UnitData("Dwarvish Thunderer", (AttackData("dagger", "dagger", "blade", "melee", 6, 2, "attacks/dagger-human.png"), AttackData("thunderstick", "thunderstick", "pierce", "ranged", 18, 1))),
    UnitData("Elvish Archer", (AttackData("sword", "sword", "blade", "melee", 5, 2, "attacks/sword-elven.png"), AttackData("bow", "bow", "pierce", "ranged", 5, 4, "attacks/bow-elven.png"))),
    UnitData("Elvish Fighter", (AttackData("sword", "sword", "blade", "melee", 5, 4, "attacks/sword-elven.png"), AttackData("bow", "bow", "pierce", "ranged", 3, 3, "attacks/bow-elven.png"))),
    UnitData("Elvish Scout", (AttackData("sword", "sword", "blade", "melee", 4, 3, "attacks/sword-elven.png"), AttackData("bow", "bow", "pierce", "ranged", 6, 2, "attacks/bow-elven.png"))),
    UnitData("Elvish Shaman", (AttackData("staff", "staff", "impact", "melee", 3, 2, "attacks/druidstaff.png"), AttackData("entangle", "entangle", "impact", "ranged", 4, 2))),
    UnitData("Fencer", (AttackData("saber", "saber", "blade", "melee", 4, 4, "attacks/saber-human.png"),)),
    UnitData("Footpad", (AttackData("club", "club", "impact", "melee", 4, 2, "attacks/club-small.png"), AttackData("sling", "sling", "impact", "ranged", 5, 2))),
    UnitData("Ghoul", (AttackData("claws", "claws", "blade", "melee", 4, 3, "attacks/claws-undead.png"),)),
    UnitData("Heavy Infantryman", (AttackData("mace", "mace", "impact", "melee", 11, 2, "attacks/mace-spiked.png"),)),
    UnitData("Horseman", (AttackData("spear", "spear", "pierce", "melee", 9, 2),)),
    UnitData("Mage", (AttackData("staff", "staff", "impact", "melee", 5, 1, "attacks/staff-magic.png"), AttackData("missile", "missile", "fire", "ranged", 7, 3, "attacks/magic-missile.png"))),
    UnitData("Merman Fighter", (AttackData("trident", "trident", "pierce", "melee", 6, 3),)),
    UnitData("Merman Hunter", (AttackData("spear", "spear", "pierce", "melee", 4, 2), AttackData("spear", "spear", "pierce", "ranged", 5, 3))),
    UnitData("Naga Fighter", (AttackData("sword", "sword", "blade", "melee", 4, 4, "attacks/sword-orcish.png"),)),
    UnitData("Orcish Archer", (AttackData("dagger", "dagger", "blade", "melee", 3, 2, "attacks/dagger-orcish.png"), AttackData("bow", "bow", "pierce", "ranged", 6, 3, "attacks/bow-orcish.png"), AttackData("bow", "bow", "fire", "ranged", 7, 2, "attacks/bow-orcish.png"))),
    UnitData("Orcish Assassin", (AttackData("dagger", "dagger", "blade", "melee", 7, 1, "attacks/dagger-orcish.png"), AttackData("throwing knives", "throwing knives", "blade", "ranged", 3, 3, "attacks/dagger-thrown-poison-orcish.png"))),
    UnitData("Orcish Grunt", (AttackData("sword", "sword", "blade", "melee", 9, 2, "attacks/sword-orcish.png"),)),
    UnitData("Poacher", (AttackData("dagger", "dagger", "blade", "melee", 3, 2, "attacks/dagger-human.png"), AttackData("bow", "bow", "pierce", "ranged", 4, 4))),
    UnitData("Saurian Augur", (AttackData("staff", "staff", "impact", "melee", 4, 2, "attacks/staff-magic.png"), AttackData("curse", "curse", "cold", "ranged", 5, 3, "attacks/curse.png"))),
    UnitData("Saurian Skirmisher", (AttackData("spear", "spear", "pierce", "melee", 4, 4, "attacks/spear.png"), AttackData("spear", "spear", "pierce", "ranged", 4, 2, "attacks/spear-thrown.png"))),
    UnitData("Skeleton", (AttackData("axe", "axe", "blade", "melee", 7, 3, "attacks/axe-undead.png"),)),
    UnitData("Skeleton Archer", (AttackData("fist", "fist", "impact", "melee", 3, 2, "attacks/fist-skeletal.png"), AttackData("bow", "bow", "pierce", "ranged", 6, 3, "attacks/bow-orcish.png"))),
    UnitData("Spearman", (AttackData("spear", "spear", "pierce", "melee", 7, 3, "attacks/spear.png"), AttackData("javelin", "javelin", "pierce", "ranged", 6, 1, "attacks/javelin-human.png"))),
    UnitData("Thief", (AttackData("dagger", "dagger", "blade", "melee", 4, 3, "attacks/dagger-human.png"),)),
    UnitData("Thug", (AttackData("club", "club", "impact", "melee", 5, 4),)),
    UnitData("Troll Whelp", (AttackData("fist", "fist", "impact", "melee", 7, 2, "attacks/fist-troll.png"),)),
    UnitData("Wolf Rider", (AttackData("fangs", "fangs", "blade", "melee", 5, 3, "attacks/fangs-animal.png"),)),
    UnitData("Wose", (AttackData("crush", "crush", "impact", "melee", 13, 2, "attacks/crush-wose.png"),)),
)

UNIT_DATA_BY_TYPE = {unit.unit_type: unit for unit in LEVEL_ONE_UNITS}


def recruit_item_name(unit_type: str) -> str:
    return f"Recruit: {unit_type}"


def attack_item_name(unit_type: str, attack_name: str, attack_range: str, damage_type: str) -> str:
    return f"Attack: {unit_type} - {attack_name} ({attack_range} {damage_type})"


def all_item_names() -> list[str]:
    names = [FILLER_ITEM_NAME]
    for unit in LEVEL_ONE_UNITS:
        names.append(recruit_item_name(unit.unit_type))
        names.extend(attack_item_name(unit.unit_type, attack.name, attack.range, attack.damage_type) for attack in unit.attacks)
    return names


def all_location_names() -> list[str]:
    return [*SCENARIO_COMPLETION_LOCATIONS, *CHEST_LOCATION_NAMES]


def generate_two_brothers_slot(world: WesnothWorld) -> None:
    roster = sorted(world.random.sample(list(LEVEL_ONE_UNITS), ROSTER_SIZE), key=lambda unit: unit.unit_type)
    starting_unit = world.random.choice(roster)
    starting_attack = world.random.choice(list(starting_unit.attacks))

    active_items = []
    for unit in roster:
        active_items.append(recruit_item_name(unit.unit_type))
        active_items.extend(attack_item_name(unit.unit_type, attack.name, attack.range, attack.damage_type) for attack in unit.attacks)

    precollected_items = {
        recruit_item_name(starting_unit.unit_type),
        attack_item_name(starting_unit.unit_type, starting_attack.name, starting_attack.range, starting_attack.damage_type),
    }
    itempool_count = len(active_items) - len(precollected_items)
    chest_count = itempool_count - len(SCENARIO_COMPLETION_LOCATIONS)
    if chest_count < 0:
        raise ValueError("Two Brothers item pool is smaller than its fixed scenario checks.")

    active_chests = active_chest_locations(chest_count)
    active_locations = [*SCENARIO_COMPLETION_LOCATIONS, *[chest["name"] for chest in active_chests]]
    chests = generate_chests(world, active_chests)

    world.roster_units = [unit.unit_type for unit in roster]
    world.starting_unit = starting_unit.unit_type
    world.starting_attack = attack_item_name(starting_unit.unit_type, starting_attack.name, starting_attack.range, starting_attack.damage_type)
    world.active_item_names = active_items
    world.precollected_item_names = sorted(precollected_items)
    world.active_location_names = active_locations
    world.two_brothers_chests = chests


def active_chest_locations(chest_count: int) -> list[dict[str, object]]:
    chests = []
    scenario_counts = {scenario_id: 0 for scenario_id in SCENARIO_IDS}
    for index in range(chest_count):
        scenario_id = SCENARIO_IDS[index % len(SCENARIO_IDS)]
        scenario_counts[scenario_id] += 1
        chests.append({
            "name": f"Two Brothers: {SCENARIO_DISPLAY_NAMES[scenario_id]} Chest {scenario_counts[scenario_id]:02d}",
            "scenario": scenario_id,
        })
    return chests


def generate_chests(world: WesnothWorld, chest_specs: list[dict[str, object]]) -> list[dict[str, object]]:
    chests = []
    specs_by_scenario: dict[str, list[dict[str, object]]] = {scenario_id: [] for scenario_id in SCENARIO_IDS}
    for chest in chest_specs:
        specs_by_scenario[str(chest["scenario"])].append(chest)

    for scenario_id, specs in specs_by_scenario.items():
        candidates = walkable_land_positions(SCENARIO_MAPS[scenario_id])
        if len(specs) > len(candidates):
            raise ValueError(f"Not enough walkable Two Brothers map positions for {scenario_id}.")

        chosen = world.random.sample(candidates, len(specs))
        for chest, (x, y) in zip(specs, chosen):
            chests.append({"name": chest["name"], "scenario": scenario_id, "x": x, "y": y})
    return chests


def walkable_land_positions(map_name: str) -> list[tuple[int, int]]:
    map_path = Path(__file__).parent / "wesnoth_addon" / "Battle_for_Wesnoth_AP" / "maps" / map_name
    if not map_path.exists():
        return fallback_positions()

    positions = []
    map_rows = [
        line
        for line in map_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("border_size=") and not line.startswith("usage=")
    ]
    playable_rows = map_rows[1:-1]
    for y, line in enumerate(playable_rows, start=1):
        terrains = line.split(",")
        for x, terrain in enumerate(terrains[1:-1], start=1):
            base = terrain.strip().split()[0]
            if is_walkable_land(base):
                positions.append((x, y))
    return positions


def is_walkable_land(terrain: str) -> bool:
    blocked_prefixes = ("W", "Q", "X", "_", "M")
    if terrain.startswith(blocked_prefixes):
        return False
    return "X" not in terrain and terrain not in {"Mm", "Md"}


def fallback_positions() -> list[tuple[int, int]]:
    return [(x, y) for y in range(4, 30) for x in range(4, 30)]
