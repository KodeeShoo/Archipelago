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


def write_item_state(received_items: list[str], addon_dir: Path | None) -> None:
    if not addon_dir:
        return
    payload = {"received_items": received_items}
    path = addon_dir / ITEM_STATE_FILENAME
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def read_save_text(path: Path) -> str:
    if path.suffix.lower() == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as save_file:
            return save_file.read()
    return path.read_text(encoding="utf-8", errors="replace")


def latest_wesnoth_ap_save(userdir: Path | None) -> Path | None:
    if not userdir:
        return None
    saves_dir = userdir / "saves"
    if not saves_dir.exists():
        return None

    saves = [
        path
        for path in saves_dir.iterdir()
        if path.is_file()
        and path.name.startswith("Wesnoth AP-")
        and (path.suffix.lower() == ".gz" or path.suffix == "")
    ]
    if not saves:
        return None
    return max(saves, key=lambda path: path.stat().st_mtime)


def parse_save_bridge_state(save_text: str) -> BridgeState:
    checked = {
        match.group(1)
        for match in re.finditer(r'\[ap_checked_locations\][\s\S]*?name="([^"]+)"[\s\S]*?\[/ap_checked_locations\]', save_text)
    }
    goal_complete = re.search(r'\bap_goal_complete="?yes"?', save_text) is not None
    return BridgeState(checked_locations=checked, goal_complete=goal_complete)


def read_save_bridge_state(userdir: Path | None) -> BridgeState:
    latest_save = latest_wesnoth_ap_save(userdir)
    if not latest_save:
        return BridgeState()
    return parse_save_bridge_state(read_save_text(latest_save))


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

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "Connected":
            self.slot_data = dict(args.get("slot_data", {}))
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


async def game_watcher(ctx: WesnothContext) -> None:
    write_bridge_state(ctx.build_bridge_state(read_bridge_state(ctx.bridge_path)), ctx.bridge_path)
    write_item_state([], ctx.addon_dir)
    logger.info("Writing Wesnoth client status file at %s", ctx.bridge_path)
    if ctx.wesnoth_userdir:
        logger.info("Watching Wesnoth saves under %s", ctx.wesnoth_userdir / "saves")
    if ctx.addon_dir:
        logger.info("Writing received items for Wesnoth at %s", ctx.addon_dir / ITEM_STATE_FILENAME)
    else:
        logger.warning("Could not detect installed Wesnoth add-on folder. Received items will not reach Wesnoth.")

    while not ctx.exit_event.is_set():
        try:
            bridge_state = read_save_bridge_state(ctx.wesnoth_userdir)
            current_state = ctx.build_bridge_state(bridge_state)
            write_bridge_state(current_state, ctx.bridge_path)

            ids_to_send = {
                LOCATION_NAME_TO_ID[name]
                for name in bridge_state.checked_locations
                if name in LOCATION_NAME_TO_ID
            }
            new_ids = ids_to_send - ctx.locations_checked
            if new_ids:
                ctx.locations_checked |= new_ids
                sent = await ctx.check_locations(new_ids)
                if sent:
                    logger.info("Sent Wesnoth checks: %s", ", ".join(
                        ctx.location_names.lookup_in_game(location_id, ctx.game) for location_id in sorted(sent)
                    ))

            if bridge_state.goal_complete and not ctx.finished_game:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
                logger.info("Sent Wesnoth goal completion.")

            if ctx.sync_requested or len(ctx.items_received) != ctx.highest_processed_item_index:
                ctx.highest_processed_item_index = len(ctx.items_received)
                ctx.sync_requested = False
                current_state = ctx.build_bridge_state(bridge_state)
                write_bridge_state(current_state, ctx.bridge_path)
                write_item_state(current_state.received_items, ctx.addon_dir)
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
