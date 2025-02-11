import csv
import json
import sys
from typing import List, Dict
from circle import smallest_circle


savant_fields = (
    "game_date",
    "player_name",
    "batter",
    "pitcher",
    "outs_when_up",
    "at_bat_number",
    "hc_x",
    "hc_y",
    "launch_angle",
    "launch_speed",
    "home_team",
    "game_pk",
    "plate_x",
    "plate_z",
)

year = sys.argv[1] if len(sys.argv) > 1 else 2024


def clean_player_name(name: str) -> str:
    names = name.split(", ")
    if len(names) == 2:
        return f"{names[1]} {names[0]}"
    return name


# Strip out all the columns from the Baseball Savant CSV that we don't want/need.
# Write the results to data/{year}/cleaned_data.csv
with open(f"data/{year}/savant_data.csv", encoding="utf-8-sig") as raw_csv_file, open(
    f"data/{year}/interim/cleaned_data.csv", mode="w"
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
with open(f"data/{year}/interim/cleaned_data.csv") as cleaned_csv_file, open(
    f"data/{year}/interim/sorted_data.csv", mode="w"
) as sorted_csv_file:
    csv_reader = csv.DictReader(cleaned_csv_file)
    homeruns = sorted(
        [row for row in csv_reader],
        key=lambda hr: (hr["game_date"], hr["game_pk"], hr["at_bat_number"]),
    )

    csv_writer = csv.DictWriter(sorted_csv_file, fieldnames=savant_fields)
    csv_writer.writeheader()
    for homerun in homeruns:
        csv_writer.writerow(homerun)

# Group the sorted home runs by player
with open(f"data/{year}/interim/sorted_data.csv") as sorted_csv_file, open(
    f"data/{year}/interim/player_data.json", mode="w", encoding="utf8"
) as player_data_json:
    grouped_by_player = {}
    csv_reader = csv.DictReader(sorted_csv_file)
    for row in csv_reader:
        # Skip the rare homers that don't have coordinate data for some reason
        if all([row["hc_x"], row["hc_y"], row["launch_angle"], row["launch_speed"]]):
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


def homerun_groups(all_homers: List[dict]) -> Dict[int, dict]:
    """
    A window function that analyzes consecutive home runs in groups of 2 through 10.
    """
    similarity_data_by_group_size = {}
    for n in range(2, 11):
        homer_groups_of_n = []
        for start_index in range(0, len(all_homers) - n):
            homers = all_homers[start_index : start_index + n]
            enclosing_circle = smallest_circle(homers)
            data = {"circle": enclosing_circle, "homers": homers}

            # Using the smallest enclosing circle and the Statcast data, calculate the custom "similarity score"
            # so that results can be ordered by this metric.
            data["similarity_score"] = similarity_score(data)
            data["homer_range"] = f"{start_index + 1}-{start_index + n}"
            homer_groups_of_n.append(data)

        if len(homer_groups_of_n):
            homer_groups_of_n.sort(
                key=lambda data: data["similarity_score"], reverse=similarity_descending
            )
            similarity_data_by_group_size[n] = homer_groups_of_n[0]

    return similarity_data_by_group_size


def similarity_score(homerun_data: dict) -> float:
    homers = homerun_data["homers"]
    launch_angles = [float(hr["launch_angle"]) for hr in homers]
    exit_velos = [float(hr["launch_speed"]) for hr in homers]
    plate_x_values = [float(hr["plate_x"]) for hr in homers]
    plate_z_values = [float(hr["plate_z"]) for hr in homers]

    launch_angle_range = max(launch_angles) - min(launch_angles)
    exit_velo_range = max(exit_velos) - min(exit_velos)
    plate_x_range = max(plate_x_values) - min(plate_x_values)
    plate_z_range = max(plate_z_values) - min(plate_z_values)

    home_teams = [hr["home_team"] for hr in homers]
    game_pks = [hr["game_pk"] for hr in homers]
    pitchers = [hr["pitcher"] for hr in homers]

    stadiums_bonus = (1 / len(set(home_teams))) * 4
    games_bonus = 1 / len(set(game_pks))
    pitchers_bonus = 1 / len(set(pitchers))

    bonuses = stadiums_bonus + games_bonus + pitchers_bonus

    deductions = (
        homerun_data["circle"].radius
        + launch_angle_range
        + exit_velo_range
        + plate_x_range
        + plate_z_range
    )
    return 100 - (deductions / (1 + bonuses))


class Encoder(json.JSONEncoder):
    """Allows custom data types (like Circle) to become JSON-serializable."""

    def default(self, obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


with open(f"data/{year}/interim/player_data.json") as json_file, open(
    f"data/{year}/interim/all_results.json", mode="w"
) as results_file, open(
    f"data/{year}/{'top' if similarity_descending else 'bottom'}_results.json",
    mode="w",
) as top_results_file:
    player_data: dict = json.load(json_file)
    results_data = {}

    for batter_id, batter_data in player_data.items():
        results_data[batter_id] = {
            **homerun_groups(batter_data.get("homeruns")),
        }

    json.dump(results_data, results_file, indent=2, cls=Encoder)

    all_players_by_group_size = {}
    for batter_id, batter_data in results_data.items():
        for group_size, group_size_data in batter_data.items():
            all_group_size_data = all_players_by_group_size.get(group_size, [])
            all_group_size_data.append(
                {
                    "batter_id": batter_id,
                    "player_name": player_data[batter_id]["player_name"],
                    **group_size_data,
                }
            )
            all_players_by_group_size[group_size] = all_group_size_data

    # Sort each group size, and discard all but the top 5 results:
    for group_size, all_group_size_data in all_players_by_group_size.items():
        all_players_by_group_size[group_size] = sorted(
            all_group_size_data,
            key=lambda g: g["similarity_score"],
            reverse=similarity_descending,
        )[0:5]

    json.dump(all_players_by_group_size, top_results_file, indent=2, cls=Encoder)
