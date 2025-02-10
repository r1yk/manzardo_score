import json
from typing import List

from circle import smallest_circle


def window_function(all_homers: List[dict]):
    for n in range(2, 10):
        print("N =", n)
        homer_groups_of_n = []
        for start_index in range(0, len(all_homers) - n):
            homers = all_homers[start_index : start_index + n]
            enclosing_circle = smallest_circle(homers)
            homer_groups_of_n.append(enclosing_circle)

        if len(homer_groups_of_n):
            homer_groups_of_n.sort(key=lambda circle: circle.radius)
            print("SMALLEST:", homer_groups_of_n[0])


with open("data/player_data.json") as json_file:
    player_data: dict = json.load(json_file)
    # mookie = player_data.pop("607208")
    # window_function(mookie.get("homeruns"))

    for batter_id, batter_data in player_data.items():
        print(batter_id)
        window_function(batter_data.get("homeruns"))
