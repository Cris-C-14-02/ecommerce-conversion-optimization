import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "outputs" / "results"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

SEGMENT_ORDER = ["low", "medium", "high", "very_high"]


def load_results():
    segment_summary = pd.read_csv(RESULTS_DIR / "user_segment_summary.csv")
    coefficients = pd.read_csv(RESULTS_DIR / "model_coefficients.csv")
    ab_group_summary = pd.read_csv(RESULTS_DIR / "ab_test_group_summary.csv")

    with open(RESULTS_DIR / "model_summary.json", "r", encoding="utf-8") as file:
        model_summary = json.load(file)

    return segment_summary, coefficients, ab_group_summary, model_summary


def setup_style():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["savefig.bbox"] = "tight"


def plot_user_segments(segment_summary):
    df = segment_summary.copy()
    df["user_segment"] = pd.Categorical(df["user_segment"], categories=SEGMENT_ORDER, ordered=True)
    df = df.sort_values("user_segment")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    palette = ["#c7d2fe", "#93c5fd", "#60a5fa", "#1d4ed8"]

    sns.barplot(
        data=df,
        x="user_segment",
        y="avg_pred_prob",
        hue="user_segment",
        palette=palette,
        legend=False,
        ax=axes[0],
    )
    axes[0].set_title("Average Predicted Purchase Probability")
    axes[0].set_xlabel("User Segment")
    axes[0].set_ylabel("Predicted Probability")
    axes[0].tick_params(axis="x", rotation=15)

    sns.barplot(
        data=df,
        x="user_segment",
        y="actual_purchase_rate",
        hue="user_segment",
        palette=palette,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Actual Purchase Rate by Segment")
    axes[1].set_xlabel("User Segment")
    axes[1].set_ylabel("Actual Purchase Rate")
    axes[1].tick_params(axis="x", rotation=15)

    fig.suptitle("User Segment Performance", fontsize=20, y=1.02)
    fig.savefig(FIGURES_DIR / "user_segment_performance.png", dpi=200)
    plt.close(fig)


def plot_model_coefficients(coefficients):
    df = coefficients.copy().sort_values("coefficient", ascending=True)
    colors = ["#ef4444" if value < 0 else "#2563eb" for value in df["coefficient"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["feature"], df["coefficient"], color=colors)
    ax.axvline(0, color="#334155", linewidth=1)
    ax.set_title("Logistic Regression Feature Coefficients")
    ax.set_xlabel("Coefficient Value")
    ax.set_ylabel("Feature")
    fig.savefig(FIGURES_DIR / "model_coefficients.png", dpi=200)
    plt.close(fig)


def plot_ab_test_summary(ab_group_summary, model_summary):
    df = ab_group_summary.copy()
    fig, ax = plt.subplots(figsize=(9, 6))

    palette = {"control": "#94a3b8", "treatment": "#0f766e"}
    sns.barplot(
        data=df,
        x="ab_group",
        y="expected_conversion_rate",
        hue="ab_group",
        palette=palette,
        legend=False,
        ax=ax,
    )

    uplift = model_summary["ab_test_summary"]["relative_uplift"]
    ax.set_title(f"Expected Conversion Rate by A/B Group\nRelative uplift: {uplift:.2%}")
    ax.set_xlabel("Experiment Group")
    ax.set_ylabel("Expected Conversion Rate")
    fig.savefig(FIGURES_DIR / "ab_test_expected_conversion.png", dpi=200)
    plt.close(fig)


def plot_model_metrics(model_summary):
    metrics = model_summary["model_metrics"]
    df = pd.DataFrame(
        {
            "metric": ["accuracy", "precision", "recall", "roc_auc"],
            "value": [
                metrics["accuracy"],
                metrics["precision"],
                metrics["recall"],
                metrics["roc_auc"],
            ],
        }
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x="metric", y="value", hue="metric", palette="Blues_d", legend=False, ax=ax)
    ax.set_title("Model Performance Metrics")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    fig.savefig(FIGURES_DIR / "model_metrics.png", dpi=200)
    plt.close(fig)


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    setup_style()

    segment_summary, coefficients, ab_group_summary, model_summary = load_results()

    plot_user_segments(segment_summary)
    plot_model_coefficients(coefficients)
    plot_ab_test_summary(ab_group_summary, model_summary)
    plot_model_metrics(model_summary)

    print(f"Saved figures to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
