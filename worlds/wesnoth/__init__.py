from worlds.LauncherComponents import Component, Type, components, launch

from .world import WesnothWorld as WesnothWorld


def launch_client(*args: str) -> None:
    from .client.wesnoth_client import launch as launch_wesnoth_client

    launch(launch_wesnoth_client, name="Battle for Wesnoth Client", args=args)


components.append(
    Component(
        "Battle for Wesnoth Client",
        func=launch_client,
        game_name="Battle for Wesnoth",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
