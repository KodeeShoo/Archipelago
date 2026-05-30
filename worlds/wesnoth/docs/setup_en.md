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
4. Start the Wesnoth AP client bridge.
5. Start the Wesnoth campaign.
6. Complete campaign milestones to send checks.
7. Finish the Crownlands objective to complete the slot.

The bridge is still a framework. Until the client and add-on state sync are completed, use this world to validate generation logic and item/location names.
