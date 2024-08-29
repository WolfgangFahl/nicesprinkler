import math
from dataclasses import dataclass, field

@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def to_tuple(self):
        return (self.x, self.y, self.z)

@dataclass
class JetParams:
    start_position: Point3D
    horizontal_angle: float
    vertical_angle: float
    pressure: float = 0.1  # bar
    nozzle_diameter: float = 25.4/2  # mm (default 1/2 inch)
    initial_velocity: float = field(init=False)

    def __post_init__(self):
        pressure_pascal = self.pressure * 100000  # Convert bar to Pascal
        density = 1000  # kg/m^3 (water density)
        velocity = math.sqrt(2 * pressure_pascal / density)  # m/s
        nozzle_radius_m = (self.nozzle_diameter / 2) / 1000  # Convert mm to m
        flow_area = math.pi * nozzle_radius_m**2  # m^2
        flow_rate = velocity * flow_area  # m^3/s
        self.initial_velocity = flow_rate / flow_area  # m/s

@dataclass
class JetSpline:
    start: Point3D
    control1: Point3D
    control2: Point3D
    end: Point3D

    def evaluate_spline(self, t):
        """Evaluate the Bezier spline at the given parameter values."""
        points = []
        spline=self
        for ti in t:
            p = (1-ti)**3 * spline.start + \
                3*(1-ti)**2*ti * spline.control1 + \
                3*(1-ti)*ti**2 * spline.control2 + \
                ti**3 * spline.end
            points.append((p.x, p.y, p.z))
        return points

class WaterJet:
    def __init__(self, jet_params: JetParams):
        self.jet_params = jet_params
        self.gravity = 9.8

    @classmethod
    def from_position(cls, x: float, y: float, z: float, h_angle: float, v_angle: float, pressure: float, nozzle_diameter: float = 25.4/2):
        return cls(JetParams(Point3D(x, y, z), h_angle, v_angle, pressure, nozzle_diameter))

    def _calculate_trajectory_params(self):
        jp = self.jet_params
        v_rad = math.radians(jp.vertical_angle)
        sin_v = math.sin(v_rad)
        cos_v = math.cos(v_rad)

        t_max = 2 * jp.initial_velocity * sin_v / self.gravity
        max_distance = jp.initial_velocity * t_max * cos_v
        max_height = jp.start_position.z + (jp.initial_velocity * sin_v)**2 / (2 * self.gravity)

        direction = Point3D(
            math.cos(math.radians(jp.horizontal_angle)),
            math.sin(math.radians(jp.horizontal_angle)),
            0
        )

        return max_distance, max_height, direction

    def calculate_jet(self) -> JetSpline:
        start = self.jet_params.start_position
        max_distance, max_height, direction = self._calculate_trajectory_params()

        end = start + direction * max_distance
        end.z = 0  # Assuming water lands on ground

        control1 = start + direction * (max_distance / 3)
        control1.z = max_height

        control2 = start + direction * (2 * max_distance / 3)
        control2.z = (max_height + end.z) / 2

        return JetSpline(start, control1, control2, end)