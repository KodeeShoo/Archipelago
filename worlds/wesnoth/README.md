# Battle for Wesnoth Archipelago Framework

This is a starter framework for a Battle for Wesnoth Archipelago implementation.
It is split into three pieces:

- `worlds/wesnoth/`: the Archipelago world package that defines items, locations, options, rules, and slot data.
- `wesnoth_addon/Battle_for_Wesnoth_AP/`: a Wesnoth add-on skeleton for a custom AP-aware campaign.
- `client/`: a Python bridge/client sketch for syncing the AP server with Wesnoth-visible state.

The first milestone is a custom Wesnoth campaign. It avoids patching mainline campaigns while proving the important loop:

1. Archipelago generates a seed for `Battle for Wesnoth`.
2. The AP client connects to the server and receives item/location data.
3. Wesnoth records completed checks in campaign variables.
4. The client sends those checks to AP and applies received items back into Wesnoth state.
5. Wesnoth sends completion when the campaign goal is reached.

## Install the World During Development

In an Archipelago source checkout:

1. Copy `worlds/wesnoth` into `Archipelago/worlds/wesnoth`.
2. Run Archipelago from source.
3. Generate a template/options file for `Battle for Wesnoth`.
4. Generate a seed.

For an external `.apworld`, package the folder so the archive contains:

```text
wesnoth.apworld
└── wesnoth/
    ├── __init__.py
    ├── archipelago.json
    └── ...
```

The included `tools/build_apworld.ps1` does this from the framework folder.

## Install the Wesnoth Add-on Skeleton

Copy `wesnoth_addon/Battle_for_Wesnoth_AP` to Wesnoth's add-ons directory:

```text
<userdata>/data/add-ons/Battle_for_Wesnoth_AP
```

Then start Wesnoth and look for the `Battle for Wesnoth AP Prototype` campaign.

## Current Smoke Test

The current playable test is intentionally tiny:

- Checks:
  - `Tutorial: First Village`
  - `Tutorial: First Level Up`
  - `Tutorial: Training Chest`
- Items:
  - `Recruit: Bowman`
  - `Recruit: Mage`
  - `Extra Gold`

`Recruit: Bowman` lets the prototype campaign recruit Bowmen. `Recruit: Mage` lets it recruit Mages. `Extra Gold` gives side 1 a one-time 50 gold bonus. Defeating the enemy leader completes the slot.

## Running the Smoke Test

1. Generate a one-player `Battle for Wesnoth` seed from this checkout.
2. Install `wesnoth_addon/Battle_for_Wesnoth_AP` into Wesnoth's add-ons folder.
3. Start the AP server with the generated archive.
4. Start the client:

```powershell
python -m worlds.wesnoth.client.wesnoth_client --connect SERVER:PORT
```

The client also appears in Archipelago Launcher as `Battle for Wesnoth Client`.

The client writes a status file here:

```text
%USERPROFILE%\Documents\My Games\WesnothAP\bridge_state.json
```

Checks are read from the latest `Wesnoth AP-*` autosave in your Wesnoth user data folder. Received items are written to the installed add-on as `ap_items.json`, because Wesnoth Lua can read add-on files but does not expose general-purpose file writing.

You can override paths for the client with:

```powershell
python -m worlds.wesnoth.client.wesnoth_client --connect SERVER:PORT --wesnoth-userdir "C:\Users\you\Documents\My Games\Wesnoth1.18"
```

After completing a check in Wesnoth, end the turn or save so the client can see the updated save file.

## Current Design

The world currently treats Wesnoth as a campaign randomizer:

- Locations are scenario milestones such as villages, bosses, allied recruit events, and final objectives.
- Items are unlocks such as recruit permissions, alliances, leadership, extra gold, and consumable/support rewards.
- Rules model broad tactical requirements, not exact map tactics.

That is enough to validate the Archipelago integration before investing in deep campaign-specific logic.

## Next Implementation Steps

1. Replace prototype checks with real checks from the campaign you want to randomize.
2. Decide whether this stays a custom campaign or patches mainline campaigns.
3. Harden the bridge path after in-game testing:
   - confirm Wesnoth's Lua sandbox can write the default bridge file on your installed version;
   - fall back to a user-selected bridge path if needed;
   - replace the tiny JSON parser with a stronger add-on-side strategy if mainline Wesnoth exposes one.
4. Add regression tests once the world is copied into an Archipelago checkout.

## Notes

Archipelago world code is Python. Wesnoth content is WML/Lua. Wesnoth's normal Lua API is intentionally sandboxed, so direct sockets or arbitrary file writes may require either a Wesnoth engine patch, a native helper, or a save/state-file bridge.
