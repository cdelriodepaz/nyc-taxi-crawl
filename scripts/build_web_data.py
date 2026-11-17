"""Build docs/data.json, the data behind the project website (docs/index.html).

Run from the repository root, after `python data/get_data.py`:
    python scripts/build_web_data.py

Everything comes from our own code: load_trips() for the labelled trips and the
split, and the final logistic regression from src/pipeline.py, fitted on May.
"""
import itertools
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import RAW_PATH, load_trips  # noqa: E402
from src.pipeline import FINAL_GROUPS, GROUPS, logistic, make_features  # noqa: E402

RAW_DIR = ROOT / "data" / "raw"
OUT = ROOT / "docs" / "data.json"

trips = load_trips()
train, valid = trips[trips.split == "train"], trips[trips.split == "valid"]

# 1. The fitted model, as plain numbers the browser can use
model = logistic(FINAL_GROUPS).fit(make_features(train), train.is_crawl)
prep, lr = model.named_steps["prep"], model.named_steps["model"]
weights = dict(zip(prep.get_feature_names_out(), lr.coef_[0]))
scaler = prep.named_transformers_["num"].steps[1][1]
num_cols = [c for g in FINAL_GROUPS for c in GROUPS[g]["numeric"]]
numeric = {c: {"mean": float(scaler.mean_[i]), "scale": float(scaler.scale_[i]), "coef": float(weights[f"num__{c}"])}
           for i, c in enumerate(num_cols)}
ohe = prep.named_transformers_["cat"]
categorical = {}
for i, c in enumerate([c for g in FINAL_GROUPS for c in GROUPS[g]["categorical"]]):
    rare = set(ohe.infrequent_categories_[i]) if ohe.infrequent_categories_[i] is not None else set()
    categorical[c] = {"values": {str(int(v)): float(weights[f"cat__{c}_{v}"]) for v in ohe.categories_[i] if v not in rare},
                      "other": float(weights.get(f"cat__{c}_infrequent_sklearn", 0.0))}
params = {"intercept": float(lr.intercept_[0]), "numeric": numeric, "categorical": categorical, "airport_zones": [1, 132, 138]}

# 2. Threshold curve on June: [threshold, tp, fp, fn, tn]
p_valid = model.predict_proba(make_features(valid))[:, 1]
y_valid = valid.is_crawl.to_numpy()
curve = []
for t in np.round(np.arange(0.01, 1.0, 0.01), 2):
    warn = p_valid >= t
    curve.append([float(t), int((warn & (y_valid == 1)).sum()), int((warn & (y_valid == 0)).sum()),
                  int((~warn & (y_valid == 1)).sum()), int((~warn & (y_valid == 0)).sum())])

# 3. Crawl rate by pickup zone and time band, May only
hour = train.tpep_pickup_datetime.dt.hour
bands = {"all": (0, 23), "night": (0, 6), "morning": (7, 9), "day": (10, 18), "evening": (19, 23)}
zones = {}
for name, (a, b) in bands.items():
    stats = train[(hour >= a) & (hour <= b)].groupby("PULocationID").is_crawl.agg(["size", "mean"])
    for zone, row in stats.iterrows():
        zones.setdefault(str(int(zone)), {})[name] = [int(row["size"]), round(float(row["mean"]), 4)]

# 4. Zone shapes in latitude and longitude, simplified for the web
shapes = gpd.read_file(RAW_DIR / "taxi_zones" / "taxi_zones.shp").to_crs(4326)
shapes["geometry"] = shapes.geometry.simplify(0.0004, preserve_topology=True)


def rounded(coords):
    return [rounded(c) for c in coords] if isinstance(coords[0], list) else [round(coords[0], 4), round(coords[1], 4)]


features = []
for _, row in shapes.iterrows():
    geom = json.loads(gpd.GeoSeries([row.geometry]).to_json())["features"][0]["geometry"]
    geom["coordinates"] = rounded(geom["coordinates"])
    features.append({"type": "Feature", "properties": {"id": int(row.LocationID), "zone": row.zone, "borough": row.borough}, "geometry": geom})

# 5. Crawl rate by hour and by day, May and June
def rates(df, key):
    stats = df.groupby(key).is_crawl.agg(["size", "mean"])
    return [[int(i), int(r["size"]), round(float(r["mean"]), 4)] for i, r in stats.iterrows()]


time = {name: {"hour": rates(df, df.tpep_pickup_datetime.dt.hour), "day": rates(df, df.tpep_pickup_datetime.dt.day_of_week)}
        for name, df in [("may", train), ("june", valid)]}

# 6. Every combination of the five cleaning rules, on the raw file
raw = pd.read_parquet(RAW_PATH)
duration = (raw.tpep_dropoff_datetime - raw.tpep_pickup_datetime).dt.total_seconds() / 60
with np.errstate(divide="ignore", invalid="ignore"):
    speed = raw.trip_distance / (duration / 60)
crawl = (speed < 6).astype(int)
rules = [duration >= 1, duration <= 120, raw.trip_distance > 0, raw.trip_distance <= 40, speed < 70]
combos = {}
for bits in itertools.product([0, 1], repeat=5):
    keep = pd.Series(True, index=raw.index)
    for on, rule in zip(bits, rules):
        if on:
            keep &= rule
    combos["".join(map(str, bits))] = [int(keep.sum()), round(float(crawl[keep].mean()), 4)]

# 7. Zone names, and the typical May distance of each route with at least 10 trips
lookup = pd.read_csv(RAW_DIR / "taxi_zone_lookup.csv").set_index("LocationID")
names = {str(i): [r.Borough if isinstance(r.Borough, str) else "Outside NYC",
                  r.Zone if isinstance(r.Zone, str) else "Unknown zone"] for i, r in lookup.iterrows()}
routes = train.groupby(["PULocationID", "DOLocationID"]).trip_distance.agg(["size", "median"])
routes = routes[routes["size"] >= 10]
pairs = {f"{int(a)}-{int(b)}": round(float(r["median"]), 1) for (a, b), r in routes.iterrows()}

data = {"params": params, "curve": curve, "june": {"n": int(len(y_valid)), "pos": int(y_valid.sum()), "prauc": float(average_precision_score(y_valid, p_valid))},
        "zones": zones, "geo": {"type": "FeatureCollection", "features": features}, "time": time, "combos": combos,
        "lookup": names, "pairs": pairs}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(data, separators=(",", ":"), allow_nan=False))
print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB). June PR AUC: {data['june']['prauc']:.3f}")
