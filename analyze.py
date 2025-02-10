import csv
import json
from typing import List, Dict
from circle import smallest_circle


savant_fields = (
    "game_date",
    "player_name",
    "batter",
    "pitcher",
    "outs_when_up",
    "inning",
    "hc_x",
    "hc_y",
    "launch_angle",
    "launch_speed",
    "home_team",
    "game_pk",
)


def clean_player_name(name: str) -> str:
    names = name.split(", ")
    if len(names) == 2:
        return f"{names[1]} {names[0]}"
    return name


# Strip out all the columns from the Baseball Savant CSV that we don't want/need.
# Write the results to data/cleaned_data.csv
with open("data/01_savant_data.csv", encoding="utf-8-sig") as raw_csv_file, open(
    "data/02_cleaned_data.csv", mode="w"
) as cleaned_csv_file:
    # ^^^ Using utf-8-sig treats the BOM (byte-order mark) in the raw savant data as metadata, not file content.
    # Otherwise there's a weird zero-width space that ends up in the cleaned data.
    csv_reader = csv.DictReader(raw_csv_file)
    csv_writer = csv.DictWriter(
        cleaned_csv_file, fieldnames=savant_fields, extrasaction="ignore"
    )
    csv_writer.writeheader()
    for row in csv_reader:
        row["player_name"] = clean_player_name(row["player_name"])
        csv_writer.writerow(row)

# Sort all the home runs chronologically ascending.
# Write the results to data/sorted_data.csv
with open("data/02_cleaned_data.csv") as cleaned_csv_file, open(
    "data/03_sorted_data.csv", mode="w"
) as sorted_csv_file:
    csv_reader = csv.DictReader(cleaned_csv_file)
    homeruns = sorted(
        [row for row in csv_reader],
        key=lambda hr: (hr["game_date"], hr["inning"], hr["outs_when_up"]),
    )

    csv_writer = csv.DictWriter(sorted_csv_file, fieldnames=savant_fields)
    csv_writer.writeheader()
    for homerun in homeruns:
        csv_writer.writerow(homerun)

# Group the sorted home runs by player
with open("data/03_sorted_data.csv") as sorted_csv_file, open(
    "data/04_player_data.json", mode="w", encoding="utf8"
) as player_data_json:
    grouped_by_player = {}
    csv_reader = csv.DictReader(sorted_csv_file)
    for row in csv_reader:
        # Skip the rare homers that don't have coordinate data for some reason
        if row["hc_x"] and row["hc_y"]:
            batter_id = row["batter"]
            player_data = grouped_by_player.get(
                batter_id, {"player_name": row["player_name"], "homeruns": []}
            )

            # Clean up some unnecessary data for each home run:
            del row["batter"]
            del row["player_name"]
            player_data["homeruns"].append(row)
            grouped_by_player[batter_id] = player_data

    json.dump(grouped_by_player, player_data_json, indent=2, ensure_ascii=False)

similarity_descending = True


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
                key=lambda data: data["similarity_score"], reverse=similarity_descending
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

    stadiums_bonus = 1 / len(set(home_teams))
    games_bonus = 1 / len(set(game_pks))
    pitchers_bonus = 1 / len(set(pitchers))

    bonuses = stadiums_bonus + games_bonus + pitchers_bonus

    deductions = homerun_data["circle"].radius + launch_angle_range + exit_velo_range
    return 100 - (deductions / (1 + bonuses))


class Encoder(json.JSONEncoder):
    """Allows custom data types (like Circle) to become JSON-serializable."""

    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


with open("data/04_player_data.json") as json_file, open(
    "data/05_all_results.json", mode="w"
) as results_file, open(
    f"data/06_{'top' if similarity_descending else 'bottom'}_results.json", mode="w"
) as top_results_file:
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

    # Sort each group size, and discard all but the top 5 results:
    for group_size, all_group_size_data in all_players_by_group_size.items():
        all_players_by_group_size[group_size] = sorted(
            all_group_size_data,
            key=lambda g: g["similarity_score"],
            reverse=similarity_descending,
        )[0:5]

    json.dump(all_players_by_group_size, top_results_file, indent=2, cls=Encoder)
