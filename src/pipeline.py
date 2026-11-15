import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 42
AIRPORT_ZONES = [1, 132, 138]
FINAL_GROUPS = ["distance", "time", "zones"]

GROUPS = {
    "distance": {"numeric": ["trip_distance", "log_distance"], "categorical": []},
    "time": {"numeric": [], "categorical": ["hour", "day_of_week"]},
    "zones": {"numeric": ["same_zone", "airport_trip"], "categorical": ["PULocationID", "DOLocationID"]},
    "trip details": {"numeric": ["passenger_count"], "categorical": ["VendorID"]},
}


def make_features(df):
    pickup = df["tpep_pickup_datetime"]
    return pd.DataFrame({
        "trip_distance": df["trip_distance"],
        "log_distance": np.log1p(df["trip_distance"]),
        "hour": pickup.dt.hour,
        "day_of_week": pickup.dt.day_of_week,
        "PULocationID": df["PULocationID"],
        "DOLocationID": df["DOLocationID"],
        "same_zone": (df["PULocationID"] == df["DOLocationID"]).astype(int),
        "airport_trip": (df["PULocationID"].isin(AIRPORT_ZONES) | df["DOLocationID"].isin(AIRPORT_ZONES)).astype(int),
        "passenger_count": df["passenger_count"].replace(0, np.nan),
        "VendorID": df["VendorID"],
    })


def preprocessor(groups):
    numeric = [col for g in groups for col in GROUPS[g]["numeric"]]
    categorical = [col for g in groups for col in GROUPS[g]["categorical"]]
    steps = []
    if numeric:
        steps.append(("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), numeric))
    if categorical:
        steps.append(("cat", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50), categorical))
    return ColumnTransformer(steps)


def logistic(groups):
    return Pipeline([("prep", preprocessor(groups)), ("model", LogisticRegression(max_iter=2000))])


def tree(groups, depth):
    model = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=50, random_state=RANDOM_STATE)
    return Pipeline([("prep", preprocessor(groups)), ("model", model)])