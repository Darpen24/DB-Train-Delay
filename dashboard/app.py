from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD_CSV = PROJECT_ROOT / "data" / "local" / "gold" / "route_reliability.csv"
SAMPLE_FALLBACK = PROJECT_ROOT / "data" / "samples" / "route_reliability_sample.csv"


st.set_page_config(page_title="DB Route Reliability", layout="wide")
st.title("DB Train Delay and Route Reliability")
st.caption(
    "Operational comparison of selected German rail routes using "
    "locally generated gold-layer metrics."
)


@st.cache_data
def load_data() -> pd.DataFrame:
    path = GOLD_CSV if GOLD_CSV.exists() else SAMPLE_FALLBACK
    return pd.read_csv(path)


df = load_data()

route_types = sorted(df["route_type"].dropna().unique())
selected_route_types = st.sidebar.multiselect("Route type", route_types, default=route_types)
selected_metric = st.sidebar.selectbox(
    "Ranking metric",
    ["reliability_score", "avg_delay_minutes", "cancellation_rate_pct", "delay_per_100_km"],
    index=0,
)
filtered = df[df["route_type"].isin(selected_route_types)].copy()
for column in [
    "avg_delay_minutes",
    "delay_frequency_pct",
    "cancellation_rate_pct",
    "delay_per_100_km",
    "reliability_score",
]:
    filtered[column] = pd.to_numeric(filtered[column], errors="coerce")

metric_cols = st.columns(4)
metric_cols[0].metric("Routes", len(filtered))
metric_cols[1].metric("Avg delay", f"{filtered['avg_delay_minutes'].mean():.1f} min")
metric_cols[2].metric("Delay frequency", f"{filtered['delay_frequency_pct'].mean():.1f}%")
metric_cols[3].metric("Cancellation rate", f"{filtered['cancellation_rate_pct'].mean():.1f}%")

top_route = filtered.sort_values("reliability_score", ascending=False).iloc[0]
bottom_route = filtered.sort_values("reliability_score", ascending=True).iloc[0]
st.markdown(
    f"**Most reliable route:** `{top_route['route_id']}`  |  "
    f"**Most disrupted route:** `{bottom_route['route_id']}`"
)

left, right = st.columns(2)
with left:
    fig = px.bar(
        filtered.sort_values(selected_metric, ascending=False),
        x="route_id",
        y=selected_metric,
        color="route_type",
        title="Route Comparison",
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

st.subheader("Observed Delay Drivers")
st.markdown(
    "- Long-distance services show larger absolute delays because "
    "schedule variance can accumulate across more stops.\n"
    "- Platform changes appear on Mannheim to Frankfurt and "
    "Heidelberg to Karlsruhe, which is a useful disruption signal.\n"
    "- The Munich to Hamburg sample includes a cancellation, which "
    "reduces reliability even without a recorded departure delay."
)
