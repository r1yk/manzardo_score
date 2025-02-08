import csv
import re


def clean_player_name(name: str) -> str:
    names = name.split(", ")
    if len(names) == 2:
        return f"{names[1]} {names[0]}"
    return name


def home_run_number(description: str) -> int:
    for hr_number_match in re.findall("\d+", description):
        return int(str(hr_number_match))
    return 0


field_to_index = {
    "game_date": 1,
    "player_name": 5,
    "batter_id": 6,
    "pitcher_id": 7,
    "description": 15,
    "coordinate_x": 37,
    "coordinate_y": 38,
}
# Using utf-8-sig treats the BOM (byte-order mark) in the raw savant data as metadata, not file content
# Otherwise there's a weird zero-width space that ends up in the cleaned data.
with open("./savant_data.csv", encoding="utf-8-sig") as raw_csv_file, open(
    "./cleaned_data.csv", mode="w"
) as cleaned_csv_file:
    csv_reader = csv.reader(raw_csv_file)
    csv_writer = csv.writer(cleaned_csv_file)
    for row in csv_reader:
        cleaned_row = [
            row[field_to_index[field]]
            for field in [
                "game_date",
                "player_name",
                "batter_id",
                "pitcher_id",
                "description",
                "coordinate_x",
                "coordinate_y",
            ]
        ]
        cleaned_row[1] = clean_player_name(cleaned_row[1])
        cleaned_row[4] = home_run_number(cleaned_row[4])

        csv_writer.writerow(cleaned_row)
