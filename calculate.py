import json
from typing import List

from circle import smallest_circle


def window_function(all_homers: List[dict]):
    for n in range(2, 20):
        print("N =", n)
        homer_groups_of_n = []
        for start_index in range(0, len(all_homers) - n):
            homers = all_homers[start_index : start_index + n]
            smallest = smallest_circle(homers)
            # print(smallest)
            homer_groups_of_n.append(smallest)

        homer_groups_of_n.sort(key=lambda circle: circle.radius)
        print("SMALLEST:", homer_groups_of_n[0])


with open("data/player_data.json") as json_file:
    player_data: dict = json.load(json_file)
    mookie = player_data.pop("605141")
    window_function(mookie.get("homeruns"))
