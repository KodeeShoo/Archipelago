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

5. Start the Wesnoth campaign.
6. Complete campaign milestones to send checks.
7. Defeat the prototype enemy leader to complete the slot.

The first smoke test uses `Tutorial: First Village`, `Tutorial: First Level Up`, and `Tutorial: Enemy Leader Defeated`.
