# Battle for Wesnoth Randomizer Setup Guide

## Required Software

- Archipelago 0.6.7 or newer
- Battle for Wesnoth
- The `wesnoth.apworld` package or this world copied into an Archipelago source checkout
- The `Battle_for_Wesnoth_AP` Wesnoth add-on

## Current Prototype Flow

1. Install the Archipelago world.
2. Install the Wesnoth add-on.
3. Generate a multiworld containing `Battle for Wesnoth`.
4. Start the Wesnoth AP client bridge:

```powershell
python -m worlds.wesnoth.client.wesnoth_client --connect SERVER:PORT
```

If the client cannot find your Wesnoth user data folder, pass it explicitly:

```powershell
python -m worlds.wesnoth.client.wesnoth_client --connect SERVER:PORT --wesnoth-userdir "C:\Users\you\Documents\My Games\Wesnoth1.18"
```

5. Start the Wesnoth campaign.
6. Complete campaign milestones, then end the turn or save so the client can read the updated autosave.
7. Open the training chest for the final smoke-test check, then defeat the prototype enemy leader to complete the slot.

The first smoke test uses `Tutorial: First Village`, `Tutorial: First Level Up`, and `Tutorial: Training Chest`.
