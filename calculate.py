import json
from typing import List, Dict

from circle import smallest_circle

descending = True


def window_function(all_homers: List[dict]) -> Dict[int, dict]:
    smallest_by_group_size = {}
    for n in range(2, 11):
        homer_groups_of_n = []
        for start_index in range(0, len(all_homers) - n):
            homers = all_homers[start_index : start_index + n]
            enclosing_circle = smallest_circle(homers)
            data = {"circle": enclosing_circle, "homers": homers}
            data["similarity_score"] = similarity_score(data)
            homer_groups_of_n.append(data)

        if len(homer_groups_of_n):
            homer_groups_of_n.sort(
                key=lambda data: data["similarity_score"], reverse=descending
            )
            smallest_by_group_size[n] = homer_groups_of_n[0]

    return smallest_by_group_size


def similarity_score(homerun_data: dict) -> float:
    homers = homerun_data["homers"]
    launch_angles = [float(hr["launch_angle"]) for hr in homers]
    exit_velos = [float(hr["launch_speed"]) for hr in homers]

    launch_angle_range = max(launch_angles) - min(launch_angles)
    exit_velo_range = max(exit_velos) - min(exit_velos)

    home_teams = [hr["home_team"] for hr in homers]
    game_pks = [hr["game_pk"] for hr in homers]
    pitchers = [hr["pitcher"] for hr in homers]

    same_stadium_bonus = len(set(home_teams)) == 1
    same_game_bonus = len(set(game_pks)) == 1
    same_pitcher_bonus = len(set(pitchers)) == 1

    bonuses = sum(
        [
            int(bonus)
            for bonus in [same_stadium_bonus, same_game_bonus, same_pitcher_bonus]
        ]
    )

    deductions = homerun_data["circle"].radius + launch_angle_range + exit_velo_range
    return 100 - (deductions / (1 + bonuses))


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


with open("data/player_data.json") as json_file, open(
    "data/results.json", mode="w"
) as results_file, open("data/sorted_results.json", mode="w") as sorted_results_file:
    player_data: dict = json.load(json_file)
    results_data = {}

    for batter_id, batter_data in player_data.items():
        results_data[batter_id] = window_function(batter_data.get("homeruns"))

    json.dump(results_data, results_file, indent=2, cls=Encoder)

    all_players_by_group_size = {}
    for batter_id, batter_data in results_data.items():
        for group_size, group_size_data in batter_data.items():
            all_group_size_data = all_players_by_group_size.get(group_size, [])
            all_group_size_data.append({"batter_id": batter_id, **group_size_data})
            all_players_by_group_size[group_size] = all_group_size_data

    # Sort each group size:
    for group_size, all_group_size_data in all_players_by_group_size.items():
        all_players_by_group_size[group_size] = sorted(
            all_group_size_data, key=lambda g: g["similarity_score"], reverse=descending
        )

    json.dump(all_players_by_group_size, sorted_results_file, indent=2, cls=Encoder)
