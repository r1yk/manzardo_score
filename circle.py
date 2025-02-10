from dataclasses import dataclass
from typing import List, Set
import math
import random

random.seed()


@dataclass(frozen=True, eq=True)
class Circle:
    radius: float
    center: "Coordinate"


@dataclass(frozen=True, eq=True)
class Coordinate:
    x: float
    y: float

    def is_within(self, c: Circle) -> bool:
        return distance_between(self, c.center) <= c.radius


def distance_between(a: Coordinate, b: Coordinate):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def smallest_circle(homers: List[dict]) -> Circle:
    hit_coordinates = set(
        [Coordinate(x=float(homer["hc_x"]), y=float(homer["hc_y"])) for homer in homers]
    )
    return welzl(hit_coordinates, set())


def welzl(all_points: Set[Coordinate], boundary_points: Set[Coordinate]) -> Circle:
    """
    An implementation of Welzl's algorithm:
    https://en.wikipedia.org/wiki/Smallest-circle_problem#Welzl's_algorithm
    """
    if len(all_points) == 0 or len(boundary_points) == 3:
        return trivial(boundary_points)

    random_point = random_point_in_set(all_points)
    circle = welzl(all_points.difference({random_point}), boundary_points)

    if random_point.is_within(circle):
        return circle

    return welzl(
        all_points.difference({random_point}), boundary_points.union({random_point})
    )


def random_point_in_set(points: Set[Coordinate]) -> Coordinate:
    # TODO: Welzl's algorithm would be optimized if this actually returned a random point,
    # but the groups of home runs being evaluated are all small (between 2 and 10), so we're not really
    # worried about catastrophic worst-cast that becomes really computationally inefficient.
    random_index = math.floor(random.random() * len(points))
    return list(points)[random_index]


def trivial(boundary_points: Set[Coordinate]):
    if len(boundary_points) == 0:
        return Circle(radius=0, center=Coordinate(0, 0))

    elif len(boundary_points) == 1:
        points = list(boundary_points)
        return Circle(radius=0, center=points[0])

    elif len(boundary_points) == 2:
        points = list(boundary_points)
        return Circle(
            radius=distance_between(points[0], points[1]) / 2,
            center=midpoint(points[0], points[1]),
        )

    else:
        points = list(boundary_points)
        return circumcircle(a=points[0], b=points[1], c=points[2])


def midpoint(a: Coordinate, b: Coordinate) -> Coordinate:
    return Coordinate(x=(a.x + b.x) / 2, y=(a.y + b.y) / 2)


def circumcircle(a: Coordinate, b: Coordinate, c: Coordinate) -> Circle:
    # Compute the determinants:
    d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))

    if d == 0:
        raise ValueError(
            "The given points are collinear and do not form a valid triangle."
        )

    # Compute circumcenter coordinates
    cx = (
        (a.x**2 + a.y**2) * (b.y - c.y)
        + (b.x**2 + b.y**2) * (c.y - a.y)
        + (c.x**2 + c.y**2) * (a.y - b.y)
    ) / d
    cy = (
        (a.x**2 + a.y**2) * (c.x - b.x)
        + (b.x**2 + b.y**2) * (a.x - c.x)
        + (c.x**2 + c.y**2) * (b.x - a.x)
    ) / d

    circumcenter = Coordinate(cx, cy)
    radius = math.sqrt((a.x - cx) ** 2 + (a.y - cy) ** 2)
    return Circle(center=circumcenter, radius=radius)
