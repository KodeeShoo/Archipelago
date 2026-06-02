from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import Utils
from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    gui_enabled,
    handle_url_arg,
    logger,
    server_loop,
)
from NetUtils import ClientStatus

from worlds.wesnoth.items import ITEM_NAME_TO_ID
from worlds.wesnoth.locations import LOCATION_NAME_TO_ID

GAME_NAME = "Battle for Wesnoth"
DEFAULT_BRIDGE_FILE = Path.home() / "Documents" / "My Games" / "WesnothAP" / "bridge_state.json"
BRIDGE_ENV_VAR = "WESNOTH_AP_BRIDGE"
ADDON_ID = "Battle_for_Wesnoth_AP"
ITEM_STATE_FILENAME = "ap_items.json"


@dataclass
class BridgeState:
    checked_locations: set[str] = field(default_factory=set)
    received_items: list[str] = field(default_factory=list)
    goal_complete: bool = False
    connected: bool = False
    status: str = "Not connected"
    slot_data: dict[str, Any] = field(default_factory=dict)
    item_name_to_id: dict[str, int] = field(default_factory=lambda: dict(ITEM_NAME_TO_ID))
    location_name_to_id: dict[str, int] = field(default_factory=lambda: dict(LOCATION_NAME_TO_ID))

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "BridgeState":
        return cls(
            checked_locations=set(data.get("checked_locations", [])),
            received_items=list(data.get("received_items", [])),
            goal_complete=bool(data.get("goal_complete", False)),
            connected=bool(data.get("connected", False)),
            status=str(data.get("status", "Not connected")),
            slot_data=dict(data.get("slot_data", {})),
            item_name_to_id=dict(data.get("item_name_to_id", ITEM_NAME_TO_ID)),
            location_name_to_id=dict(data.get("location_name_to_id", LOCATION_NAME_TO_ID)),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "checked_locations": sorted(self.checked_locations),
            "received_items": self.received_items,
            "goal_complete": self.goal_complete,
            "connected": self.connected,
            "status": self.status,
            "slot_data": self.slot_data,
            "item_name_to_id": self.item_name_to_id,
            "location_name_to_id": self.location_name_to_id,
        }


def get_bridge_path(cli_path: str | None = None) -> Path:
    return Path(cli_path or os.environ.get(BRIDGE_ENV_VAR) or DEFAULT_BRIDGE_FILE).expanduser()


def read_bridge_state(path: Path) -> BridgeState:
    if not path.exists():
        return BridgeState()
    try:
        return BridgeState.from_json(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        logger.warning("Bridge file is not valid JSON yet; keeping previous AP state.")
        return BridgeState(status="Waiting for valid bridge JSON")


def write_bridge_state(state: BridgeState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(state.to_json(), indent=2), encoding="utf-8")
    temp_path.replace(path)


def candidate_wesnoth_userdirs() -> list[Path]:
    candidates = [
        Path.home() / "OneDrive" / "Documents" / "My Games" / "Wesnoth1.18",
        Path.home() / "Documents" / "My Games" / "Wesnoth1.18",
        Path.home() / "OneDrive" / "Documents" / "My Games" / "Wesnoth1.16",
        Path.home() / "Documents" / "My Games" / "Wesnoth1.16",
    ]
    return [path for path in candidates if path.exists()]


def detect_wesnoth_userdir(cli_path: str | None = None) -> Path | None:
    if cli_path:
        path = Path(cli_path).expanduser()
        return path if path.exists() else None

    for path in candidate_wesnoth_userdirs():
        if (path / "data" / "add-ons" / ADDON_ID).exists() or (path / "saves").exists():
            return path
    return None


def find_addon_dir(userdir: Path | None) -> Path | None:
    if not userdir:
        return None
    addon_dir = userdir / "data" / "add-ons" / ADDON_ID
    return addon_dir if addon_dir.exists() else None


def item_state_unlocks(received_items: list[str], slot_data: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    all_items = [*list((slot_data or {}).get("precollected_items", [])), *received_items]
    recruits = []
    attacks = []
    for item in all_items:
        if item.startswith("Recruit: "):
            recruits.append(item.removeprefix("Recruit: "))
        elif item.startswith("Attack: "):
            attacks.append(item.removeprefix("Attack: "))
    return sorted(set(recruits)), sorted(set(attacks))


def slot_chest_strings(slot_data: dict[str, Any] | None = None) -> list[str]:
    chests = []
    for chest in (slot_data or {}).get("two_brothers_chests", []):
        try:
            chests.append(f"{chest['name']}|{chest['scenario']}|{int(chest['x'])}|{int(chest['y'])}")
        except (KeyError, TypeError, ValueError):
            continue
    return chests


def write_item_state(
    received_items: list[str],
    addon_dir: Path | None,
    seed_name: str | None = None,
    slot_data: dict[str, Any] | None = None,
    location_rewards: list[str] | None = None,
) -> None:
    if not addon_dir:
        return
    unlocked_recruits, unlocked_attacks = item_state_unlocks(received_items, slot_data)
    payload = {
        "received_items": received_items,
        "seed_name": seed_name or "",
        "roster_units": list((slot_data or {}).get("roster_units", [])),
        "unlocked_recruits": unlocked_recruits,
        "unlocked_attacks": unlocked_attacks,
        "two_brothers_chests": slot_chest_strings(slot_data),
        "location_rewards": location_rewards or [],
    }
    path = addon_dir / ITEM_STATE_FILENAME
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def clear_item_state(addon_dir: Path | None) -> None:
    if not addon_dir:
        return
    write_item_state([], addon_dir)


def read_save_text(path: Path) -> str:
    if path.suffix.lower() == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as save_file:
            return save_file.read()
    return path.read_text(encoding="utf-8", errors="replace")


def is_replay_save(path: Path) -> bool:
    return "replay" in path.name.lower()


def wesnoth_ap_save_candidates(userdir: Path | None) -> list[Path]:
    if not userdir:
        return []
    saves_dir = userdir / "saves"
    if not saves_dir.exists():
        return []

    return [
        path
        for path in saves_dir.iterdir()
        if path.is_file()
        and path.name.startswith("Wesnoth AP-")
        and (path.suffix.lower() == ".gz" or path.suffix == "")
    ]


def latest_wesnoth_ap_save(userdir: Path | None) -> Path | None:
    saves = [path for path in wesnoth_ap_save_candidates(userdir) if not is_replay_save(path)]
    if not saves:
        return None
    return max(saves, key=lambda path: path.stat().st_mtime)


def latest_wesnoth_ap_replay(userdir: Path | None) -> Path | None:
    replays = [path for path in wesnoth_ap_save_candidates(userdir) if is_replay_save(path)]
    if not replays:
        return None
    return max(replays, key=lambda path: path.stat().st_mtime)


def parse_goal_complete(save_text: str) -> bool:
    matches = re.findall(r'(?m)^\s*ap_goal_complete=("?yes"?|"?no"?)\s*$', save_text)
    return bool(matches) and matches[-1].strip('"') == "yes"


def parse_replay_goal_complete(replay_text: str) -> bool:
    upload_log_match = re.search(r"\[upload_log\]([\s\S]*?)\[/upload_log\]", replay_text)
    if upload_log_match:
        upload_log_text = upload_log_match.group(1)
        if re.search(r"(?m)^\s*end_units2=0\s*$", upload_log_text):
            return True

    replay_start_match = re.search(r"\[replay_start\]([\s\S]*?)\[/replay_start\]", replay_text)
    if not replay_start_match:
        return False

    leader_unit_block = None
    for unit_match in re.finditer(r"\[unit\]([\s\S]*?)\[/unit\]", replay_start_match.group(1)):
        if 'id="RaidLeader"' in unit_match.group(1):
            leader_unit_block = unit_match.group(1)
            break
    if not leader_unit_block:
        return False

    leader_x_match = re.search(r"(?m)^\s*x=(\d+)\s*$", leader_unit_block)
    leader_y_match = re.search(r"(?m)^\s*y=(\d+)\s*$", leader_unit_block)
    if not leader_x_match or not leader_y_match:
        return False

    leader_x, leader_y = leader_x_match.group(1), leader_y_match.group(1)
    for command_match in re.finditer(r"\[command\]([\s\S]*?)\[/command\]", replay_text):
        command = command_match.group(1)
        if "from_side=1" not in command or "[attack]" not in command or "dies=yes" not in command:
            continue
        destination_match = re.search(r"\[destination\]\s*x=(\d+)\s*y=(\d+)\s*\[/destination\]", command)
        if destination_match and destination_match.groups() == (leader_x, leader_y):
            return True

    return False


def parse_save_seed_name(save_text: str) -> str | None:
    seed_match = re.search(r'(?m)^\s*ap_seed_name="([^"]+)"\s*$', save_text)
    return seed_match.group(1) if seed_match else None


def save_matches_seed(save_text: str, seed_name: str | None) -> bool:
    return bool(seed_name) and parse_save_seed_name(save_text) == seed_name


def parse_save_bridge_state(save_text: str) -> BridgeState:
    checked = {
        match.group(1)
        for match in re.finditer(r'\[ap_checked_locations\][\s\S]*?name="([^"]+)"[\s\S]*?\[/ap_checked_locations\]', save_text)
    }
    goal_complete = parse_goal_complete(save_text)
    return BridgeState(checked_locations=checked, goal_complete=goal_complete)


def read_latest_matching_save(userdir: Path | None, seed_name: str | None, replay: bool) -> tuple[Path, str] | None:
    candidates = [
        path
        for path in wesnoth_ap_save_candidates(userdir)
        if is_replay_save(path) == replay
    ]
    for path in sorted(candidates, key=lambda candidate: candidate.stat().st_mtime, reverse=True):
        save_text = read_save_text(path)
        if save_matches_seed(save_text, seed_name):
            return path, save_text
    return None


def read_save_bridge_state(userdir: Path | None, seed_name: str | None = None) -> BridgeState:
    if not seed_name:
        return BridgeState()

    latest_save = read_latest_matching_save(userdir, seed_name, replay=False)
    bridge_state = BridgeState()
    if latest_save:
        latest_save_path, latest_save_text = latest_save
        bridge_state = parse_save_bridge_state(latest_save_text)

        newest_replay = latest_wesnoth_ap_replay(userdir)
        if newest_replay and newest_replay.stat().st_mtime >= latest_save_path.stat().st_mtime:
            bridge_state.goal_complete = bridge_state.goal_complete or parse_replay_goal_complete(read_save_text(newest_replay))

    return bridge_state


class WesnothCommandProcessor(ClientCommandProcessor):
    ctx: "WesnothContext"

    def _cmd_bridge(self) -> None:
        """Show the paths used by the Wesnoth bridge."""
        self.output(f"Wesnoth status file: {self.ctx.bridge_path}")
        self.output(f"Wesnoth user data: {self.ctx.wesnoth_userdir or 'not detected'}")
        self.output(f"Wesnoth add-on dir: {self.ctx.addon_dir or 'not detected'}")

    def _cmd_resync(self) -> None:
        """Resend locally checked locations and rewrite received items to the bridge."""
        self.ctx.sync_requested = True
        self.output("Queued a Wesnoth bridge resync.")


class WesnothContext(CommonContext):
    game = GAME_NAME
    command_processor = WesnothCommandProcessor
    items_handling = 0b111

    def __init__(self, server_address: str | None, password: str | None, bridge_path: Path, wesnoth_userdir: Path | None):
        super().__init__(server_address, password)
        self.bridge_path = bridge_path
        self.wesnoth_userdir = wesnoth_userdir
        self.addon_dir = find_addon_dir(wesnoth_userdir)
        self.slot_data: dict[str, Any] = {}
        self.highest_processed_item_index = 0
        self.sync_requested = False
        self.logged_checks_seen: set[str] = set()
        self.pending_locations: set[int] = set()
        self.last_written_item_state: tuple[list[str], str | None, str, tuple[str, ...]] | None = None
        self.wesnoth_seed_name: str | None = None
        self.requested_location_scouts = False

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "RoomInfo":
            self.wesnoth_seed_name = str(args.get("seed_name") or "")
            self.sync_requested = True
        elif cmd == "Connected":
            self.slot_data = dict(args.get("slot_data", {}))
            self.requested_location_scouts = False
            self.sync_requested = True
        elif cmd in {"ReceivedItems", "RoomUpdate", "LocationInfo"}:
            self.sync_requested = True

    def run_gui(self) -> None:
        from kvui import GameManager

        class WesnothManager(GameManager):
            logging_pairs = [("Client", "Archipelago")]
            base_title = "Archipelago Battle for Wesnoth Client"

        self.ui = WesnothManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    def build_bridge_state(self, current: BridgeState) -> BridgeState:
        received_names = [
            self.item_names.lookup_in_game(item.item, self.game)
            for item in self.items_received
        ]
        return BridgeState(
            checked_locations=current.checked_locations,
            received_items=received_names,
            goal_complete=current.goal_complete,
            connected=self.server is not None,
            status="Connected" if self.server else "Not connected",
            slot_data=self.slot_data,
            item_name_to_id=dict(ITEM_NAME_TO_ID),
            location_name_to_id=dict(LOCATION_NAME_TO_ID),
        )

    def location_reward_strings(self) -> list[str]:
        rewards = []
        for location_name, location_id in LOCATION_NAME_TO_ID.items():
            network_item = self.locations_info.get(location_id)
            if not network_item:
                continue
            item_name = self.item_names.lookup_in_slot(network_item.item, network_item.player)
            player_name = self.player_names.get(network_item.player, f"Player {network_item.player}")
            rewards.append(f"{location_name}|{item_name}|{player_name}")
        return sorted(rewards)

    def write_current_state(self, bridge_state: BridgeState) -> None:
        current_state = self.build_bridge_state(bridge_state)
        write_bridge_state(current_state, self.bridge_path)
        location_rewards = self.location_reward_strings()
        item_state = (
            current_state.received_items,
            self.wesnoth_seed_name,
            json.dumps(self.slot_data, sort_keys=True),
            tuple(location_rewards),
        )
        if item_state != self.last_written_item_state:
            write_item_state(
                current_state.received_items,
                self.addon_dir,
                self.wesnoth_seed_name,
                self.slot_data,
                location_rewards,
            )
            previous_count = len(self.last_written_item_state[0] if self.last_written_item_state else [])
            new_items = current_state.received_items[previous_count:]
            self.last_written_item_state = (
                list(current_state.received_items),
                self.wesnoth_seed_name,
                json.dumps(self.slot_data, sort_keys=True),
                tuple(location_rewards),
            )
            if new_items:
                logger.info("Wrote received Wesnoth items: %s", ", ".join(new_items))


async def game_watcher(ctx: WesnothContext) -> None:
    clear_item_state(ctx.addon_dir)
    logger.info("Cleared stale Wesnoth received items.")
    ctx.write_current_state(BridgeState())
    logger.info("Writing Wesnoth client status file at %s", ctx.bridge_path)
    if ctx.wesnoth_userdir:
        logger.info("Watching Wesnoth saves under %s", ctx.wesnoth_userdir / "saves")
        logger.info("Ignoring Wesnoth saves that do not match the connected AP seed.")
    if ctx.addon_dir:
        logger.info("Writing received items for Wesnoth at %s", ctx.addon_dir / ITEM_STATE_FILENAME)
    else:
        logger.warning("Could not detect installed Wesnoth add-on folder. Received items will not reach Wesnoth.")

    while not ctx.exit_event.is_set():
        try:
            bridge_state = read_save_bridge_state(ctx.wesnoth_userdir, ctx.wesnoth_seed_name)
            ctx.write_current_state(bridge_state)

            if ctx.server and not ctx.requested_location_scouts:
                scout_locations = set(LOCATION_NAME_TO_ID.values())
                ctx.locations_scouted |= scout_locations
                await ctx.send_msgs([{"cmd": "LocationScouts", "locations": sorted(scout_locations)}])
                ctx.requested_location_scouts = True

            newly_seen_names = bridge_state.checked_locations - ctx.logged_checks_seen
            if newly_seen_names:
                ctx.logged_checks_seen |= newly_seen_names
                logger.info("Saw Wesnoth checks in save: %s", ", ".join(sorted(newly_seen_names)))

            ids_to_send = {
                LOCATION_NAME_TO_ID[name]
                for name in bridge_state.checked_locations
                if name in LOCATION_NAME_TO_ID
            }
            ctx.pending_locations |= ids_to_send - ctx.locations_checked - ctx.checked_locations
            if ctx.pending_locations:
                sent = await ctx.check_locations(ctx.pending_locations)
                if sent:
                    ctx.locations_checked |= sent
                    ctx.pending_locations -= sent
                    logger.info("Sent Wesnoth checks: %s", ", ".join(
                        ctx.location_names.lookup_in_game(location_id, ctx.game) for location_id in sorted(sent)
                    ))
                    await ctx.send_msgs([{"cmd": "Sync"}])
                elif ctx.server:
                    await ctx.send_msgs([{"cmd": "Sync"}])

            if bridge_state.goal_complete and not ctx.finished_game:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
                logger.info("Sent Wesnoth goal completion.")

            if ctx.sync_requested or len(ctx.items_received) != ctx.highest_processed_item_index:
                ctx.highest_processed_item_index = len(ctx.items_received)
                ctx.sync_requested = False
                ctx.write_current_state(bridge_state)
        except Exception as exc:
            logger.exception("Error while syncing Wesnoth bridge: %s", exc)

        await asyncio.sleep(0.5)


async def async_main(args: argparse.Namespace) -> None:
    Utils.init_logging("WesnothClient", exception_logger="Client")
    ctx = WesnothContext(
        args.connect,
        args.password,
        get_bridge_path(args.bridge_file),
        detect_wesnoth_userdir(args.wesnoth_userdir),
    )
    ctx.auth = getattr(args, "name", None)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    watcher = asyncio.create_task(game_watcher(ctx), name="WesnothBridgeWatcher")
    await ctx.exit_event.wait()
    ctx.server_address = None
    await watcher
    await ctx.shutdown()


def build_parser() -> argparse.ArgumentParser:
    parser = get_base_parser(description="Battle for Wesnoth Archipelago Client")
    parser.add_argument("url", nargs="?", help="Optional archipelago:// launch URI.")
    parser.add_argument(
        "--bridge-file",
        default=None,
        help=f"Path to client status JSON. Defaults to the {BRIDGE_ENV_VAR} environment variable or {DEFAULT_BRIDGE_FILE}.",
    )
    parser.add_argument(
        "--wesnoth-userdir",
        default=None,
        help="Path to the Wesnoth user data folder, such as Documents\\My Games\\Wesnoth1.18.",
    )
    return parser


def launch(*args: str) -> None:
    parser = build_parser()
    parsed_args = handle_url_arg(parser.parse_args(list(args)), parser)
    asyncio.run(async_main(parsed_args))


def main() -> None:
    parser = build_parser()
    args = handle_url_arg(parser.parse_args(), parser)
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
