# Wesnoth Add-on Integration Layer

The `Battle_for_Wesnoth_AP` add-on now separates reusable Archipelago helpers from the prototype training scenario.

## Core Bridge Macros

`wesnoth_addon/Battle_for_Wesnoth_AP/macros/ap_checks.cfg` contains generic macros:

- `AP_LOAD_BRIDGE` reads AP client state from `ap_items.json`.
- `AP_MARK_LOCATION` records a location check in saved Wesnoth variables.
- `AP_HAS_ITEM` tests whether a received AP item is present.
- `AP_ALLOW_RECRUIT_ITEM` unlocks a recruit type when an AP item is received.
- `AP_GRANT_GOLD_ONCE` grants gold once when an AP item is received.
- `AP_REMOVE_ATTACK_UNLESS_ITEM` removes an attack until an AP item is received.
- `AP_PLACE_CHEST_CHECK` and `AP_CHEST_CHECK_EVENT` create pickup chest checks.
- `AP_COMPLETE_GOAL` marks the AP slot goal complete.

## Scenario Item Logic

`macros/ap_training_items.cfg` is intentionally scenario-specific. It maps the current smoke-test items to Wesnoth effects:

- `Recruit: Bowman`
- `Recruit: Mage`
- `Extra Gold`
- `Attack: Javelin`

Future campaigns should add their own item macro file instead of editing the core bridge macros.

## Current Limitation

The add-on can apply received items immediately when WML events fire, because the AP client writes `ap_items.json` into the add-on directory. A normal Wesnoth add-on still cannot open a socket or freely write outbound check data, so the AP client continues reading checks from saves/replays for now.
