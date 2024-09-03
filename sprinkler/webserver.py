"""
Created on 13.08.2024

@author: wf
"""

import os

from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui

from sprinkler.sprinkler_core import SprinklerConfig, SprinklerSystem
from sprinkler.sprinkler_head import SprinklerHeadView
from sprinkler.sprinkler_sim import SprinklerSimulation
from sprinkler.stepper_view import StepperView
from sprinkler.version import Version


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
        self.sprinkler_system = None

        @ui.page("/remote")
        async def remote(client: Client):
            return await self.page(client, NiceSprinklerSolution.remote)

        @ui.page("/sprinkler-head")
        async def sprinkler_head(client: Client):
            return await self.page(client, NiceSprinklerSolution.sprinkler_head)

    def configure_run(self):
        """
        Configure the run based on command line arguments
        """
        examples_path = self.examples_path()
        if hasattr(self.args, "root_path"):
            self.root_path = self.args.root_path
        else:
            self.root_path = examples_path
        self.config_path = (
            self.args.config
            if os.path.isabs(self.args.config)
            else os.path.join(self.root_path, self.args.config)
        )
        self.stl_path = (
            self.args.stl
            if os.path.isabs(self.args.stl)
            else os.path.join(self.root_path, self.args.stl)
        )

        # Create SprinklerSystem
        self.sprinkler_system = SprinklerSystem(self.config_path, self.stl_path)
        stl_directory = os.path.dirname(self.stl_path)

        # Add the static files route for serving the STL files
        app.add_static_files("/examples", stl_directory)
        pass

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
        self.simulation = None

    def configure_menu(self):
        """
        configure additional non-standard menu entries
        """
        self.link_button(name="remote", icon_name="play_circle", target="/remote")
        self.link_button(name="head", icon_name="circle", target="/sprinkler-head")

    async def remote(self):
        def setup_remote():
            self.stepper_control = StepperView(self, self.webserver.sprinkler_system)
            self.stepper_control.setup_ui()

        await self.setup_content_div(setup_remote)

    async def sprinkler_head(self):
        def setup_sprinkler_head():
            self.sphv = SprinklerHeadView(self, self.webserver.sprinkler_system)
            self.sphv.setup_ui()

        await self.setup_content_div(setup_sprinkler_head)

    async def home(self):
        """Generates the home page with a 3D viewer and controls for the sprinkler."""
        self.setup_menu()
        with ui.column():
            self.simulation = SprinklerSimulation(self, self.webserver.sprinkler_system)
            self.simulation.setup_scene_frame()

        await self.setup_footer()

    def configure_settings(self):
        """Generates the settings page with options to modify sprinkler configuration."""
        config_str = self.webserver.sprinkler_system.config.to_yaml()
        ui.textarea("Configuration", value=config_str).classes("w-full").on(
            "change", self.update_config
        )

    def update_config(self, e):
        """Updates the simulation configuration based on user input."""
        try:
            new_config = SprinklerConfig.from_yaml(e.value)
            self.webserver.sprinkler_system.config = new_config
            self.simulation.sprinkler_system = self.webserver.sprinkler_system
            self.reset_simulation()
            ui.notify("Configuration updated successfully")
        except Exception as ex:
            ui.notify(f"Error updating configuration: {str(ex)}", color="red")
