from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD_CSV = PROJECT_ROOT / "data" / "local" / "gold" / "route_reliability.csv"
SAMPLE_FALLBACK = PROJECT_ROOT / "data" / "samples" / "route_reliability_sample.csv"


st.set_page_config(page_title="DB Route Reliability", layout="wide")
st.title("DB Route Reliability")


@st.cache_data
def load_data() -> pd.DataFrame:
    path = GOLD_CSV if GOLD_CSV.exists() else SAMPLE_FALLBACK
    return pd.read_csv(path)


df = load_data()

route_types = sorted(df["route_type"].dropna().unique())
selected_route_types = st.sidebar.multiselect("Route type", route_types, default=route_types)
filtered = df[df["route_type"].isin(selected_route_types)]

metric_cols = st.columns(4)
metric_cols[0].metric("Routes", len(filtered))
metric_cols[1].metric("Avg delay", f"{filtered['avg_delay_minutes'].mean():.1f} min")
metric_cols[2].metric("Delay frequency", f"{filtered['delay_frequency_pct'].mean():.1f}%")
metric_cols[3].metric("Cancellation rate", f"{filtered['cancellation_rate_pct'].mean():.1f}%")

left, right = st.columns(2)
with left:
    fig = px.bar(
        filtered,
        x="route_id",
        y="avg_delay_minutes",
        color="route_type",
        title="Average Delay by Route",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.scatter(
        filtered,
        x="distance_km",
        y="delay_per_100_km",
        size="event_count",
        color="route_type",
        hover_name="route_id",
        title="Delay per 100 km",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Route Reliability Table")
st.dataframe(
    filtered.sort_values("reliability_score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

