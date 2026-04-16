import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs" / "results"

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ecommerce")

FEATURE_COLUMNS = [
    "view_count",
    "cart_count",
    "has_viewed",
    "has_carted",
    "view_to_cart_rate",
]
LABEL_COLUMN = "label_purchase"
ID_COLUMN = "visitorid"


def get_engine():
    if not MYSQL_USERNAME or not MYSQL_PASSWORD:
        raise ValueError(
            "MYSQL_USERNAME and MYSQL_PASSWORD must be set as environment variables."
        )

    return create_engine(
        f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )


def load_features(engine):
    query = f"SELECT * FROM user_features"
    df = pd.read_sql(query, engine)
    print(f"Loaded {len(df):,} user rows from MySQL.")
    return df


def prepare_dataframe(df):
    missing_columns = [
        column for column in [ID_COLUMN, *FEATURE_COLUMNS, LABEL_COLUMN] if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing expected columns: {missing_columns}")

    model_df = df[[ID_COLUMN, *FEATURE_COLUMNS, LABEL_COLUMN]].copy()
    model_df[FEATURE_COLUMNS] = model_df[FEATURE_COLUMNS].fillna(0)
    model_df[LABEL_COLUMN] = model_df[LABEL_COLUMN].fillna(0).astype(int)
    return model_df


def train_model(model_df):
    X = model_df[FEATURE_COLUMNS]
    y = model_df[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "positive_rate_train": round(float(y_train.mean()), 6),
        "positive_rate_test": round(float(y_test.mean()), 6),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 6),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 6),
    }

    coefficients = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "coefficient": pipeline.named_steps["model"].coef_[0],
        }
    ).sort_values("coefficient", ascending=False)

    return pipeline, metrics, coefficients


def score_users(model_df, pipeline):
    scored_df = model_df.copy()
    scored_df["pred_prob"] = pipeline.predict_proba(scored_df[FEATURE_COLUMNS])[:, 1]
    scored_df["user_segment"] = pd.qcut(
        scored_df["pred_prob"].rank(method="first"),
        q=4,
        labels=["low", "medium", "high", "very_high"],
    )
    scored_df["target_group"] = np.where(
        (scored_df["user_segment"].isin(["high", "very_high"]))
        & (scored_df["has_carted"] == 1)
        & (scored_df[LABEL_COLUMN] == 0),
        "remarketing_target",
        "general_population",
    )
    return scored_df


def build_segment_summary(scored_df):
    summary = (
        scored_df.groupby("user_segment", observed=False)
        .agg(
            users=(ID_COLUMN, "count"),
            avg_pred_prob=("pred_prob", "mean"),
            actual_purchase_rate=(LABEL_COLUMN, "mean"),
            avg_view_count=("view_count", "mean"),
            avg_cart_count=("cart_count", "mean"),
        )
        .reset_index()
    )
    summary["users"] = summary["users"].astype(int)
    return summary


def simulate_ab_test(scored_df):
    candidates = scored_df[scored_df["target_group"] == "remarketing_target"].copy()
    if candidates.empty:
        raise ValueError(
            "No remarketing target users were found. Check segmentation logic or source data."
        )

    candidates = candidates.sort_values("pred_prob", ascending=False).reset_index(drop=True)
    candidates["ab_group"] = np.where(candidates.index % 2 == 0, "treatment", "control")
    expected_uplift = 0.15
    baseline_min = 0.02
    baseline_max = 0.12

    score_min = candidates["pred_prob"].min()
    score_max = candidates["pred_prob"].max()
    score_range = score_max - score_min
    if score_range == 0:
        candidates["score_rank"] = 0.5
    else:
        candidates["score_rank"] = (candidates["pred_prob"] - score_min) / score_range

    # This is a forward-looking simulation, not an observed label.
    # We convert relative model score into a conservative expected baseline rate.
    candidates["expected_conversion_prob"] = (
        baseline_min + candidates["score_rank"] * (baseline_max - baseline_min)
    )
    treatment_mask = candidates["ab_group"] == "treatment"
    candidates.loc[treatment_mask, "expected_conversion_prob"] = np.clip(
        candidates.loc[treatment_mask, "expected_conversion_prob"] * (1 + expected_uplift),
        0,
        1,
    )

    simulation_summary = (
        candidates.groupby("ab_group", observed=False)
        .agg(
            users=(ID_COLUMN, "count"),
            avg_model_prob=("pred_prob", "mean"),
            expected_conversion_rate=("expected_conversion_prob", "mean"),
            avg_score_rank=("score_rank", "mean"),
        )
        .reset_index()
    )

    treatment_rate = simulation_summary.loc[
        simulation_summary["ab_group"] == "treatment", "expected_conversion_rate"
    ].iloc[0]
    control_rate = simulation_summary.loc[
        simulation_summary["ab_group"] == "control", "expected_conversion_rate"
    ].iloc[0]

    uplift_absolute = float(treatment_rate - control_rate)
    uplift_relative = float(uplift_absolute / control_rate) if control_rate else None

    ab_test_summary = {
        "target_users": int(len(candidates)),
        "expected_uplift_assumption": expected_uplift,
        "baseline_rate_assumption_min": baseline_min,
        "baseline_rate_assumption_max": baseline_max,
        "expected_treatment_conversion_rate": round(float(treatment_rate), 6),
        "expected_control_conversion_rate": round(float(control_rate), 6),
        "absolute_uplift": round(uplift_absolute, 6),
        "relative_uplift": round(uplift_relative, 6) if uplift_relative is not None else None,
    }

    return candidates, simulation_summary, ab_test_summary


def export_outputs(metrics, coefficients, scored_df, segment_summary, ab_candidates, ab_group_summary, ab_test_summary):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    coefficients.to_csv(OUTPUT_DIR / "model_coefficients.csv", index=False)
    scored_df.sort_values("pred_prob", ascending=False).to_csv(
        OUTPUT_DIR / "user_scoring_results.csv",
        index=False,
    )
    segment_summary.to_csv(OUTPUT_DIR / "user_segment_summary.csv", index=False)
    ab_candidates.to_csv(OUTPUT_DIR / "ab_test_candidates.csv", index=False)
    ab_group_summary.to_csv(OUTPUT_DIR / "ab_test_group_summary.csv", index=False)

    top_targets = (
        scored_df[scored_df["target_group"] == "remarketing_target"]
        .sort_values("pred_prob", ascending=False)
        .head(50)[[ID_COLUMN, "pred_prob", "user_segment", "view_count", "cart_count"]]
    )
    top_targets.to_csv(OUTPUT_DIR / "top_remarketing_targets.csv", index=False)

    summary_payload = {
        "model_metrics": metrics,
        "ab_test_summary": ab_test_summary,
        "coze_input": {
            "funnel_insight": "The largest drop-off is from product view to add-to-cart.",
            "priority_segment": "Carted but not purchased users with high predicted purchase probability.",
            "recommended_action": "Target the high and very_high carted non-purchasers with remarketing incentives.",
            "modeling_note": "Training excludes purchase-derived features to avoid target leakage.",
        },
    }
    with open(OUTPUT_DIR / "model_summary.json", "w", encoding="utf-8") as file:
        json.dump(summary_payload, file, indent=2)


def print_summary(metrics, segment_summary, ab_test_summary):
    print("\nModel metrics")
    for key, value in metrics.items():
        print(f"- {key}: {value}")

    print("\nUser segment summary")
    print(segment_summary.to_string(index=False))

    print("\nA/B simulation summary")
    for key, value in ab_test_summary.items():
        print(f"- {key}: {value}")


def main():
    print("Connecting to MySQL and loading engineered features...")
    engine = get_engine()
    df = load_features(engine)
    model_df = prepare_dataframe(df)

    print("Training logistic regression model...")
    pipeline, metrics, coefficients = train_model(model_df)

    print("Scoring all users and building segments...")
    scored_df = score_users(model_df, pipeline)
    segment_summary = build_segment_summary(scored_df)

    print("Running marketing A/B test simulation...")
    ab_candidates, ab_group_summary, ab_test_summary = simulate_ab_test(scored_df)

    print("Exporting outputs...")
    export_outputs(
        metrics,
        coefficients,
        scored_df,
        segment_summary,
        ab_candidates,
        ab_group_summary,
        ab_test_summary,
    )

    print_summary(metrics, segment_summary, ab_test_summary)
    print(f"\nFiles exported to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
