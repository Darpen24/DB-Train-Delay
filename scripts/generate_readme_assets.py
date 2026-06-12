from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD_CSV = PROJECT_ROOT / "data" / "local" / "gold" / "route_reliability.csv"
IMAGE_DIR = PROJECT_ROOT / "docs" / "images"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(GOLD_CSV)
    for column in [
        "avg_delay_minutes",
        "cancellation_rate_pct",
        "delay_per_100_km",
        "reliability_score",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.sort_values("reliability_score", ascending=False).reset_index(drop=True)


def save_average_delay_chart(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 7))
    colors = {
        "short": "#2563eb",
        "medium": "#0f766e",
        "long": "#dc2626",
        "regional": "#7c3aed",
        "ice": "#ea580c",
    }
    bar_colors = [colors.get(route_type, "#4b5563") for route_type in df["route_type"]]
    values = df["avg_delay_minutes"].fillna(0)
    ax.bar(df["route_id"], values, color=bar_colors)
    ax.set_title("Average Delay by Route", fontsize=16, pad=18)
    ax.set_xlabel("Route")
    ax.set_ylabel("Average delay (minutes)")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "route-delay-overview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_delay_distance_chart(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(14, 7))
    colors = {
        "short": "#2563eb",
        "medium": "#0f766e",
        "long": "#dc2626",
        "regional": "#7c3aed",
        "ice": "#ea580c",
    }
    for _, row in df.iterrows():
        ax.scatter(
            row["distance_km"],
            row["delay_per_100_km"],
            s=max(row["event_count"], 1) * 180,
            color=colors.get(row["route_type"], "#4b5563"),
            alpha=0.8,
        )
        ax.annotate(
            row["route_id"],
            (row["distance_km"], row["delay_per_100_km"]),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=9,
        )
    ax.set_title("Delay per 100 km", fontsize=16, pad=18)
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Delay per 100 km")
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "delay-per-100km.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_table_image(df: pd.DataFrame) -> None:
    display = df[
        [
            "route_id",
            "route_type",
            "avg_delay_minutes",
            "cancellation_rate_pct",
            "delay_per_100_km",
            "reliability_score",
        ]
    ].copy()
    display = display.round(2).fillna("")
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.axis("off")
    table = ax.table(
        cellText=display.values,
        colLabels=display.columns,
        cellLoc="left",
        colLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)
    for (row, _col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1f2937")
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor("#f9fafb" if row % 2 == 0 else "white")
    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "route-reliability-table.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    save_average_delay_chart(df)
    save_delay_distance_chart(df)
    save_table_image(df)
    print(f"Saved README assets to {IMAGE_DIR}")


if __name__ == "__main__":
    main()
