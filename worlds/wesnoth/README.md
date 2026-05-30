# Battle for Wesnoth Archipelago Framework

This is a starter framework for a Battle for Wesnoth Archipelago implementation.
It is split into three pieces:

- `worlds/wesnoth/`: the Archipelago world package that defines items, locations, options, rules, and slot data.
- `wesnoth_addon/Battle_for_Wesnoth_AP/`: a Wesnoth add-on skeleton for a custom AP-aware campaign.
- `client/`: a Python bridge/client sketch for syncing the AP server with Wesnoth-visible state.

The recommended first milestone is a custom Wesnoth campaign. It avoids patching mainline campaigns while proving the important loop:

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

## Current Design

The world currently treats Wesnoth as a campaign randomizer:

- Locations are scenario milestones such as villages, bosses, allied recruit events, and final objectives.
- Items are unlocks such as recruit permissions, alliances, leadership, extra gold, and consumable/support rewards.
- Rules model broad tactical requirements, not exact map tactics.

That is enough to validate the Archipelago integration before investing in deep campaign-specific logic.

## Next Implementation Steps

1. Replace prototype checks with real checks from the campaign you want to randomize.
2. Decide whether this stays a custom campaign or patches mainline campaigns.
3. Implement the bridge path:
   - simplest: external client reads/writes a state file exported by the add-on;
   - stronger: modify Wesnoth or embed a networking-capable module for direct communication.
4. Add regression tests once the world is copied into an Archipelago checkout.

## Notes

Archipelago world code is Python. Wesnoth content is WML/Lua. Wesnoth's normal Lua API is intentionally sandboxed, so direct sockets or arbitrary file writes may require either a Wesnoth engine patch, a native helper, or a save/state-file bridge.
