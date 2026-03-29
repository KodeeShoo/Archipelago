from __future__ import annotations

import os
import sys
import asyncio
import shutil
import zlib
import re
from pathlib import Path
from typing import Set, Dict, Optional

import ModuleUpdate
ModuleUpdate.update()

import Utils

if __name__ == "__main__":
    Utils.init_logging("StellarisClient", exception_logger="Client")

from NetUtils import NetworkItem, ClientStatus
from CommonClient import gui_enabled, logger, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop


class StellarisClientCommandProcessor(ClientCommandProcessor):
    def _cmd_resync(self):
        """Manually trigger a resync."""
        self.output(f"Syncing with Stellaris game state.")
        self.ctx.syncing = True

    def _cmd_game_path(self, path: str = "") -> bool:
        """Set or show the Stellaris game save path."""
        if path:
            self.ctx.game_save_path = path
            self.output(f"Game save path set to: {path}")
        else:
            self.output(f"Current game save path: {self.ctx.game_save_path}")
        return True


class StellarisContext(CommonContext):
    command_processor: int = StellarisClientCommandProcessor
    game = "Stellaris"
    items_handling = 0b111  # full remote

    def __init__(self, server_address, password):
        super(StellarisContext, self).__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.last_save_time: float = 0
        self.known_locations: Set[int] = set()
        self.previous_tech_state: Dict[str, int] = {}  # tech_name -> progress level

        # Detect Stellaris save file path
        if "localappdata" in os.environ:
            # Windows
            documents = os.path.expandvars(r"%USERPROFILE%\Documents")
            self.game_save_path = os.path.join(documents, "Paradox Interactive", "Stellaris", "save games")
        else:
            # Linux/Mac
            if "WINEPREFIX" in os.environ:
                wineprefix = os.environ["WINEPREFIX"]
            elif shutil.which("wine") or shutil.which("wine-stable"):
                wineprefix = os.path.expanduser("~/.wine")
            else:
                msg = "StellarisClient couldn't detect system type. Unable to infer Stellaris save path."
                logger.error("Error: " + msg)
                Utils.messagebox("Error", msg, error=True)
                sys.exit(1)
            self.game_save_path = os.path.join(
                wineprefix,
                "drive_c",
                os.path.expandvars(r"users\$USER\Documents\Paradox Interactive\Stellaris\save games"))

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(StellarisContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(StellarisContext, self).connection_closed()

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(StellarisContext, self).shutdown()

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            logger.info(f"Connected to Archipelago as {self.username}")
        if cmd in {"ReceivedItems"}:
            start_index = args["index"]
            if start_index != len(self.items_received):
                for item in args['items']:
                    network_item = NetworkItem(*item)
                    logger.info(f"Received item: {network_item.item} from player {network_item.player}")

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class StellarisManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Stellaris Client"

        self.ui = StellarisManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


def parse_stellaris_save(save_file_path: str) -> Dict:
    """
    Parse a Stellaris .sav file (binary/compressed format).
    Files are zlib-compressed, so we decompress first, then parse the text.
    
    Returns:
        dict with 'technologies' (tech_name -> progress level) and 'player_empire_key'
    """
    state = {
        "technologies": {},  # tech_name -> progress level
        "player_empire_key": None,
    }

    try:
        # Read and decompress the save file
        with open(save_file_path, 'rb') as f:
            # Stellaris saves start with "SAV" header, skip it
            header = f.read(3)
            if header != b'SAV':
                logger.warning(f"Unexpected save file header: {header}")
            
            # Rest of file is zlib compressed
            compressed_data = f.read()
            decompressed = zlib.decompress(compressed_data)
            content = decompressed.decode('utf-8', errors='ignore')

        # First, find the player empire key by looking for human=yes
        player_match = re.search(r'country={\s*key="([^"]+)"[^}]*human=yes', content)
        if player_match:
            player_key = player_match.group(1)
            state["player_empire_key"] = player_key
            logger.debug(f"Found player empire: {player_key}")
        else:
            logger.warning("Could not find player empire in save file")
            return state

        # Extract tech_status for the player empire
        # tech_status={ ... } contains tech progress for the player
        tech_status_match = re.search(r'tech_status=\{([^}]+)\}', content)
        if tech_status_match:
            tech_block = tech_status_match.group(1)
            
            # Parse individual technologies
            # Format: tech_name=X where X is progress level (0-100)
            tech_pattern = r'(\w+)=(\d+)'
            for match in re.finditer(tech_pattern, tech_block):
                tech_name = match.group(1)
                progress_level = int(match.group(2))
                state["technologies"][tech_name] = progress_level
                
            logger.debug(f"Extracted {len(state['technologies'])} technologies")
        else:
            logger.warning("Could not find tech_status in save file")

    except zlib.error as e:
        logger.error(f"Failed to decompress save file: {e}")
    except Exception as e:
        logger.error(f"Error parsing Stellaris save file: {e}")

    return state


async def game_watcher(ctx: StellarisContext):
    """
    Monitor Stellaris save file for technology progress.
    Detects when technologies reach completion (progress level 100).
    """
    logger.info(f"Starting Stellaris game watcher. Save path: {ctx.game_save_path}")

    while not ctx.exit_event.is_set():
        try:
            if ctx.syncing:
                sync_msg = [{'cmd': 'Sync'}]
                if ctx.locations_checked:
                    sync_msg.append({"cmd": "LocationChecks", "locations": list(ctx.locations_checked)})
                await ctx.send_msgs(sync_msg)
                ctx.syncing = False

            # Find the most recent save file
            if not os.path.exists(ctx.game_save_path):
                await asyncio.sleep(1)
                continue

            save_files = []
            try:
                for file in os.listdir(ctx.game_save_path):
                    if file.endswith('.sav'):
                        full_path = os.path.join(ctx.game_save_path, file)
                        mtime = os.path.getmtime(full_path)
                        save_files.append((mtime, full_path))
            except PermissionError:
                await asyncio.sleep(1)
                continue

            if not save_files:
                await asyncio.sleep(1)
                continue

            # Sort by modification time and get most recent
            save_files.sort(reverse=True)
            most_recent_save = save_files[0][1]
            save_time = save_files[0][0]

            # Only process if save file has been updated
            if save_time <= ctx.last_save_time:
                await asyncio.sleep(1)
                continue

            logger.info(f"Processing save file: {os.path.basename(most_recent_save)}")
            ctx.last_save_time = save_time

            # Parse the save file
            current_state = parse_stellaris_save(most_recent_save)

            # Detect newly completed technologies
            new_checks = []

            # Compare current tech progress with previous state
            for tech_name, progress_level in current_state["technologies"].items():
                prev_progress = ctx.previous_tech_state.get(tech_name, -1)
                
                # Check if technology just completed (reached 100)
                if progress_level == 100 and prev_progress < 100:
                    logger.info(f"Technology completed: {tech_name}")
                    # Map tech name to location ID
                    # Use a consistent hash to generate reproducible location IDs
                    location_id = hash(f"tech_{tech_name}") % 1000000
                    new_checks.append(location_id)

            # Update checked locations
            if new_checks:
                ctx.locations_checked.update(new_checks)
                ctx.known_locations.update(new_checks)
                message = [{"cmd": "LocationChecks", "locations": new_checks}]
                await ctx.send_msgs(message)
                logger.info(f"Sent {len(new_checks)} new location checks to server")

            # Store current tech state for next comparison
            ctx.previous_tech_state = current_state["technologies"].copy()

        except Exception as e:
            logger.exception(f"Error in game watcher: {e}")

        await asyncio.sleep(1)  # Check every second


if __name__ == '__main__':
    async def main(args):
        ctx = StellarisContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        progression_watcher = asyncio.create_task(
            game_watcher(ctx), name="StellarisProgressionWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await progression_watcher

        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Stellaris Archipelago Client")

    args, rest = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()