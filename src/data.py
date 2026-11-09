from pathlib import Path

import pandas as pd

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "yellow_tripdata_2026_sample.parquet"
SPLIT_BY_MONTH = {5: "train", 6: "valid", 7: "test"}


def load_trips(path: Path = RAW_PATH) -> pd.DataFrame:
    trips = pd.read_parquet(path)

    trips["duration_min"] = (
        trips["tpep_dropoff_datetime"] - trips["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60
    trips["speed_mph"] = trips["trip_distance"] / (trips["duration_min"] / 60)

    valid = (
        (trips["duration_min"] >= 1) & (trips["duration_min"] <= 120)
        & (trips["trip_distance"] > 0) & (trips["trip_distance"] <= 40)
        & (trips["speed_mph"] > 0) & (trips["speed_mph"] < 70)
    )
    trips = trips[valid].copy()

    trips["is_crawl"] = (trips["speed_mph"] < 6).astype(int)
    trips["split"] = trips["tpep_pickup_datetime"].dt.month.map(SPLIT_BY_MONTH)
    trips = trips[trips["split"].notna()]

    return trips.reset_index(drop=True)