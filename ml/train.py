import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib


base_dir = Path(__file__).resolve().parents[0]
processed_path = base_dir / "data" / "processed" / "2025_monaco_processed.csv"
model_path = base_dir / "models" / "pit_model.pkl"

model_path.parent.mkdir(parents=True, exist_ok=True)

# load data
df = pd.read_csv(processed_path)


#split into features and target
X = df[[
    "lap",
    "stint",
    "tire_age",
    "lap_time",
    "rolling_lap_avg_3",
    "lap_time_delta",
    "position",
    "compound"
]]

y = df["pit_next_3_laps"]


# split into test and training data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


categorical = ["compound"]
numerical = [col for col in X.columns if col not in categorical]

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="mean"))
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numerical),
        ("cat", categorical_transformer, categorical)
    ]
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])



model.fit(X_train, y_train)

joblib.dump(model, model_path)
