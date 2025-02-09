from dataclasses import dataclass
from typing import List, Set
import math


@dataclass
class Circle:
    radius: float
    center: "Coordinate"


@dataclass(frozen=True, eq=True)
class Coordinate:
    x: float
    y: float

    def is_within(self, c: Circle) -> bool:
        distance_from_center = math.sqrt(
            (c.center.x - self.x) ** 2 + (c.center.y - self.y) ** 2
        )
        return distance_from_center <= c.radius


@dataclass
class Circle:
    radius: float
    center: Coordinate


def smallest_circle(homers: List[dict]) -> Circle:
    """ """
    hit_coordinates = set(
        [Coordinate(x=float(homer["hc_x"]), y=float(homer["hc_y"])) for homer in homers]
    )
    return welzl(hit_coordinates, set())


def welzl(all_points: Set[Coordinate], boundary_points: Set[Coordinate]) -> Circle:
    # print(all_points, boundary_points)

    if len(all_points) == 0 or len(boundary_points) == 3:
        return trivial(all_points, boundary_points)

    first_point = all_points.pop()
    circle = welzl(all_points, boundary_points)
    if first_point.is_within(circle):
        return circle

    return welzl(all_points, boundary_points.union({first_point}))


def trivial(all_points: Set[Coordinate], boundary_points: Set[Coordinate]):
    if len(all_points) == 0 or len(boundary_points) == 1:
        return Circle(radius=0, center=Coordinate(0, 0))
    elif len(boundary_points) == 2:
        return Circle(radius=50, center=Coordinate(0, 0))

    points = list(boundary_points)
    return circumcircle(A=points[0], B=points[1], C=points[2])


def circumcircle(A: Coordinate, B: Coordinate, C: Coordinate) -> Circle:
    # Compute the determinants
    D = 2 * (A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y))

    if D == 0:
        raise ValueError(
            "The given points are collinear and do not form a valid triangle."
        )

    # Compute circumcenter coordinates
    Ux = (
        (A.x**2 + A.y**2) * (B.y - C.y)
        + (B.x**2 + B.y**2) * (C.y - A.y)
        + (C.x**2 + C.y**2) * (A.y - B.y)
    ) / D
    Uy = (
        (A.x**2 + A.y**2) * (C.x - B.x)
        + (B.x**2 + B.y**2) * (A.x - C.x)
        + (C.x**2 + C.y**2) * (B.x - A.x)
    ) / D

    circumcenter = Coordinate(Ux, Uy)

    # Compute circumradius
    radius = math.sqrt((A.x - Ux) ** 2 + (A.y - Uy) ** 2)

    return Circle(center=circumcenter, radius=radius)
