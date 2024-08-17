'''
Created on 2024-08-13

@author: wf
'''
import math
import json
from nicegui import ui
from typing import List, Tuple

class SprinklerSimulation:
    def __init__(self, config_file: str = 'sprinkler_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.setup_scene()

    def setup_scene(self):
        self.scene = ui.scene(
            width=800,
            height=600,
            grid=True,
            background_color='#87CEEB'  # Sky blue
        ).classes('w-full h-64')

        # Add lawn
        lawn_width = self.config['lawn']['width']
        lawn_length = self.config['lawn']['length']
        with self.scene.group().move(y=-0.01):  # Slightly below zero to avoid z-fighting with the grid
            self.scene.box(lawn_width, 0.02, lawn_length).material('#7CFC00')  # Lawn green

        # Add boundaries
        self.add_boundary('left')
        self.add_boundary('right')
        self.add_boundary('back')

        # Add sprinkler
        sprinkler_pos = self.config['sprinkler']['position']
        with self.scene.group().move(x=sprinkler_pos['x'], y=sprinkler_pos['y'], z=sprinkler_pos['z']):
            self.scene.cylinder(0.1, 0.1, 0.5).material('#808080')  # Grey cylinder for sprinkler base
            self.sprinkler_head = self.scene.sphere(0.05).material('#4682B4').move(z=0.5)  # Steel blue sphere for sprinkler head

        self.scene.move_camera(x=lawn_width/2, y=-lawn_length/2, z=lawn_length/2, look_at_x=lawn_width/2, look_at_y=lawn_length/2, look_at_z=0)

    def add_boundary(self, side: str):
        boundary = self.config['boundaries'][side]
        lawn_width = self.config['lawn']['width']
        lawn_length = self.config['lawn']['length']

        if side == 'left':
            self.scene.box(0.1, boundary['height'], lawn_length).material('#8B4513').move(x=boundary['distance'], y=lawn_length/2, z=boundary['height']/2)
        elif side == 'right':
            self.scene.box(0.1, boundary['height'], lawn_length).material('#8B4513').move(x=lawn_width-boundary['distance'], y=lawn_length/2, z=boundary['height']/2)
        elif side == 'back':
            self.scene.box(lawn_width, boundary['height'], 0.1).material('#8B4513').move(x=lawn_width/2, y=lawn_length-boundary['distance'], z=boundary['height']/2)

    def calculate_spray_points(self) -> List[Tuple[float, float, float]]:
        spray_points = []
        sprinkler_pos = self.config['sprinkler']['position']
        max_distance = self.config['hose_performance']['max_distance']

        for h_angle in range(-90, 91, 5):  # horizontal angles from -90 to 90 in 5-degree steps
            for v_angle in range(10, 61, 5):  # vertical angles from 10 to 60 in 5-degree steps
                distance = self.calculate_spray_distance(v_angle)
                x = sprinkler_pos['x'] + distance * math.cos(math.radians(h_angle))
                y = sprinkler_pos['y'] + distance * math.sin(math.radians(h_angle))
                spray_height = sprinkler_pos['z'] + distance * math.tan(math.radians(v_angle))

                if self.is_point_within_boundaries(x, y, spray_height):
                    spray_points.append((h_angle, v_angle, distance))

        return spray_points

    def calculate_spray_distance(self, angle: float) -> float:
        # Simple projectile motion calculation
        v0 = math.sqrt(self.config['hose_performance']['max_distance'] * 9.8 / math.sin(2 * math.radians(self.config['hose_performance']['optimal_angle'])))
        t = 2 * v0 * math.sin(math.radians(angle)) / 9.8
        return v0 * math.cos(math.radians(angle)) * t

    def is_point_within_boundaries(self, x: float, y: float, spray_height: float) -> bool:
        if x < 0 or x > self.config['lawn']['width'] or y < 0 or y > self.config['lawn']['length']:
            return False

        # Check left boundary
        if x <= self.config['boundaries']['left']['distance'] and spray_height > self.config['boundaries']['left']['height']:
            return False

        # Check right boundary
        if x >= self.config['lawn']['width'] - self.config['boundaries']['right']['distance'] and spray_height > self.config['boundaries']['right']['height']:
            return False

        # Check back boundary
        if y >= self.config['lawn']['length'] - self.config['boundaries']['back']['distance'] and spray_height > self.config['boundaries']['back']['height']:
            return False

        return True

    def simulate_sprinkler(self):
        spray_points = self.calculate_spray_points()

        for h_angle, v_angle, distance in spray_points:
            # Move sprinkler head
            self.sprinkler_head.move(z=0.5)  # Reset to original position
            self.sprinkler_head.rotate(h_angle, 0, v_angle)

            # Show water spray
            sprinkler_pos = self.config['sprinkler']['position']
            end_x = sprinkler_pos['x'] + distance * math.cos(math.radians(h_angle))
            end_y = sprinkler_pos['y'] + distance * math.sin(math.radians(h_angle))
            end_z = sprinkler_pos['z'] + distance * math.tan(math.radians(v_angle))

            self.scene.line([sprinkler_pos['x'], sprinkler_pos['y'], sprinkler_pos['z'] + 0.5],
                            [end_x, end_y, end_z]).material('#1E90FF', opacity=0.5)  # Light blue, semi-transparent

            ui.timer(0.1, lambda: None)  # Small delay to visualize movement

async def main():
    simulation = SprinklerSimulation()

    ui.button('Start Simulation', on_click=simulation.simulate_sprinkler)

    await ui.run_javascript(
        f'scene_c{simulation.scene.id}.camera.position.set({simulation.config["lawn"]["width"]/2}, '
        f'{-simulation.config["lawn"]["length"]/2}, {simulation.config["lawn"]["length"]/2});'
        f'scene_c{simulation.scene.id}.camera.lookAt({simulation.config["lawn"]["width"]/2}, '
        f'{simulation.config["lawn"]["length"]/2}, 0);'
    )

ui.run(main)