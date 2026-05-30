# Architecture

## Why a Custom Campaign First

Battle for Wesnoth is open source, but an AP integration still needs two independent halves:

- an Archipelago world, which controls generation logic;
- a game-side integration, which detects checks and applies received items.

A custom campaign is the lowest-risk proving ground because Wesnoth add-ons are normal WML/Lua packages and can be installed without rebuilding the engine.

## Data Model

Locations should be milestones that the game can persist:

- scenario completed;
- enemy leader defeated;
- village or chest claimed;
- ally recruited;
- optional challenge completed.

Items should be effects that can be applied at any time:

- recruit permission;
- alliance/faction unlock;
- starting or bonus gold;
- recall capacity;
- healing or support reward;
- traps such as ambushes.

## Bridge Contract

The client and add-on agree on a small state schema:

```json
{
  "checked_locations": ["Tutorial: Secure the Keep"],
  "received_items": ["Recruit: Mage", "Extra Gold"],
  "goal_complete": false
}
```

The AP client owns network sync. Wesnoth owns game state. The bridge maps between those two worlds. For the first smoke test, the bridge is a JSON file watched by the Python client and read/written by the Wesnoth add-on.

## Open Design Questions

- Should the first release be a custom campaign, a mainline campaign patch, or a scenario pack?
- How deep should item logic go: broad recruit unlocks first, or exact campaign scenario logic?
- Should the client watch save files, use a bridge file, or require a patched Wesnoth build with networking?
- Which campaign should define v1 item and location names?
