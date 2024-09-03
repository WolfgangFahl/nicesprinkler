"""
Created on 2024-09-01

@author: wf
"""

from nicegui import ui


class SimpleSlider:
    @classmethod
    def add_simple_slider(
        cls,
        min: float,
        max: float,
        value: float,
        target: object,
        bind_prop: str,
        width: str,
    ):
        """
        Adds a single slider to the UI.
        """
        slider = (
            ui.slider(min=min, max=max, value=value)
            .props("label-always")
            .bind_value(target, bind_prop)
            .classes(width)
        )
        return slider

    @classmethod
    def add_slider(
        cls,
        min: float,
        max: float,
        value: float or tuple,
        label: str,
        target: object,
        bind_prop: str,
        width: str = "w-32",
        minmax: bool = False,
    ):
        """
        Adds a slider or a pair of min-max sliders to the UI.

        Args:
        min (float): Minimum value of the slider(s).
        max (float): Maximum value of the slider(s).
        value (float or tuple): Initial value of the slider (for single slider) or a tuple (min_value, max_value) for min-max sliders.
        label (str): The label for the slider(s).
        target (object): the target object for the values
        bind_prop (str): The property to bind the slider(s) value(s) to.
        width (str, optional): The CSS class for the slider's width. Defaults to "w-32".
        minmax (bool, optional): Whether to create a pair of min-max sliders. Defaults to False.
        """
        with ui.row() as slider_row:
            ui.label(f"{label}:")
            if minmax:
                min_value, max_value = value
                min_slider = cls.add_simple_slider(
                    min, max, min_value, target, f"{bind_prop}_min", width
                )
                max_slider = cls.add_simple_slider(
                    min, max, max_value, target, f"{bind_prop}_max", width
                )
                return min_slider, max_slider
            else:
                return cls.add_simple_slider(min, max, value, target, bind_prop, width)


class GroupPos:
    """
    sliders to control the position of a group in a scene
    """

    def __init__(
        self,
        label: str,
        group,
        min_value: float = -100,
        max_value: float = 100,
        width: str = "w-32",
    ):
        self.group = group
        self.x = group.x
        self.y = group.y
        self.z = group.z
        with ui.row() as self.slider_row:
            self.label = ui.label(label)
            self.x_slider = SimpleSlider.add_slider(
                min_value, max_value, self.x, "x", self, "x", width
            )
            self.y_slider = SimpleSlider.add_slider(
                min_value, max_value, self.y, "y", self, "y", width
            )
            self.z_slider = SimpleSlider.add_slider(
                min_value, max_value, self.z, "z", self, "z", width
            )

        # Add on_change events to update the group position
        self.x_slider.on("change", self.update_group_pos)
        self.y_slider.on("change", self.update_group_pos)
        self.z_slider.on("change", self.update_group_pos)

    def update_group_pos(self, e):
        self.group.move(x=self.x, y=self.y, z=self.z)
