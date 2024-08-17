'''
Created on 13.08.2024

@author: wf
'''
"""
Created on 2024-08-13

@author: wf
"""

import os
from pathlib import Path

from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui

from sprinkler.version import Version
from sprinkler.sprinkler_sim import SprinklerSimulation


class NiceSprinklerWebServer(InputWebserver):
    """WebServer class that manages the server and handles Sprinkler operations."""

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2024 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right,
            version=Version(),
            default_port=9859,
            short_name="nicesprinkler",
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = NiceSprinklerSolution
        return server_config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self, config=NiceSprinklerWebServer.get_config())
        self.simulation = None

    def configure_run(self):
        self.config_path = (
            self.args.config
            if self.args.config
            else os.path.join(self.examples_path(), "default_config.json")
        )
        self.simulation = SprinklerSimulation(self.config_path)

    @classmethod
    def examples_path(cls) -> str:
        path = os.path.join(os.path.dirname(__file__), "../nicesprinkler_examples")
        path = os.path.abspath(path)
        return path


class NiceSprinklerSolution(InputWebSolution):
    """
    the NiceSprinkler solution
    """

    def __init__(self, webserver: NiceSprinklerWebServer, client: Client):
        """
        Initialize the solution

        Args:
            webserver (NiceSprinklerWebServer): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)
        self.simulation = webserver.simulation

    async def home(self):
        """Generates the home page with a 3D viewer and controls for the sprinkler."""
        self.setup_menu()
        with ui.column():
            with ui.scene(width=800, height=600).classes("w-full") as self.scene:
                self.simulation.setup_scene(self.scene)

            with ui.row():
                ui.button('Start Simulation', on_click=self.simulation.simulate_sprinkler)
                ui.button('Reset', on_click=self.reset_simulation)

        await self.setup_footer()

    async def reset_simulation(self):
        """Resets the simulation to its initial state."""
        self.scene.clear()
        self.simulation.setup_scene(self.scene)
        ui.notify('Simulation reset')

    def configure_settings(self):
        """Generates the settings page with options to modify sprinkler configuration."""
        ui.textarea("Configuration", value=self.simulation.config_str).classes("w-full").on('change', self.update_config)

    def update_config(self, e):
        """Updates the simulation configuration based on user input."""
        try:
            self.simulation.update_config(e.value)
            ui.notify('Configuration updated successfully')
        except Exception as ex:
            ui.notify(f'Error updating configuration: {str(ex)}', color='red')