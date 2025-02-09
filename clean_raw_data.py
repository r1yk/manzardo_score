import csv
import json


def clean_player_name(name: str) -> str:
    names = name.split(", ")
    if len(names) == 2:
        return f"{names[1]} {names[0]}"
    return name


savant_fields = (
    "game_date",
    "player_name",
    "batter",
    "pitcher",
    "outs_when_up",
    "inning",
    "hc_x",
    "hc_y",
)

# Strip out all the columns from the Baseball Savant CSV that we don't want/need.
# Write the results to data/cleaned_data.csv
with open("data/savant_data.csv", encoding="utf-8-sig") as raw_csv_file, open(
    "data/cleaned_data.csv", mode="w"
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
with open("data/cleaned_data.csv") as cleaned_csv_file, open(
    "data/sorted_data.csv", mode="w"
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
with open("data/sorted_data.csv") as sorted_csv_file, open(
    "data/player_data.json", mode="w", encoding="utf8"
) as player_data_json:
    grouped_by_player = {}
    csv_reader = csv.DictReader(sorted_csv_file, fieldnames=savant_fields)
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
