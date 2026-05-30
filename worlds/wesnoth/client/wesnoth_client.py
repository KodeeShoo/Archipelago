from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BRIDGE_FILE = Path.home() / "Documents" / "My Games" / "WesnothAP" / "bridge_state.json"


@dataclass
class BridgeState:
    checked_locations: set[str] = field(default_factory=set)
    received_items: list[str] = field(default_factory=list)
    goal_complete: bool = False

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "BridgeState":
        return cls(
            checked_locations=set(data.get("checked_locations", [])),
            received_items=list(data.get("received_items", [])),
            goal_complete=bool(data.get("goal_complete", False)),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "checked_locations": sorted(self.checked_locations),
            "received_items": self.received_items,
            "goal_complete": self.goal_complete,
        }


def read_bridge_state(path: Path = BRIDGE_FILE) -> BridgeState:
    if not path.exists():
        return BridgeState()
    return BridgeState.from_json(json.loads(path.read_text(encoding="utf-8")))


def write_bridge_state(state: BridgeState, path: Path = BRIDGE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_json(), indent=2), encoding="utf-8")


def main() -> None:
    state = read_bridge_state()
    print("Wesnoth AP bridge skeleton")
    print(f"Bridge file: {BRIDGE_FILE}")
    print(f"Checked locations: {len(state.checked_locations)}")
    print(f"Received items: {len(state.received_items)}")
    print("TODO: subclass CommonClient.CommonContext and sync this state with Archipelago.")


if __name__ == "__main__":
    main()
