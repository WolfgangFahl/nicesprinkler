'''
Created on 13.08.2024

@author: wf
'''
# sprinkler/solution.py

from nicegui import ui, Client
from sprinkler.model import SprinklerModel
from sprinkler.controller import SprinklerController
from sprinkler.view import SprinklerView

class NiceSprinklerSolution:
    def __init__(self, webserver, client: Client):
        self.webserver = webserver
        self.client = client
        self.model = SprinklerModel(webserver.config_path)
        self.controller = SprinklerController(self.model, use_hardware=False)
        self.view = SprinklerView(self.controller)

    async def home(self):
        """Generates the home page with a 3D viewer and controls for the sprinkler."""
        self.view.setup_scene()

        with ui.row():
            ui.button('Start Simulation', on_click=self.view.simulate_sprinkler)
            ui.button('Reset', on_click=self.reset_simulation)

    async def reset_simulation(self):
        """Resets the simulation to its initial state."""
        self.view.scene.clear()
        self.view.setup_scene()
        ui.notify('Simulation reset')

    def configure_settings(self):
        """Generates the settings page with options to modify sprinkler configuration."""
        ui.textarea("Configuration", value=json.dumps(self.model.config, indent=2)).classes("w-full").on('change', self.update_config)

    def update_config(self, e):
        """Updates the simulation configuration based on user input."""
        try:
            new_config = json.loads(e.value)
            self.model.config = new_config
            self.reset_simulation()
            ui.notify('Configuration updated successfully')
        except Exception as ex:
            ui.notify(f'Error updating configuration: {str(ex)}', color='red')