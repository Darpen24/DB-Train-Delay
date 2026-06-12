from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as f


def create_spark(app_name: str = "db-train-delay") -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def build_silver_events(raw_events: DataFrame) -> DataFrame:
    return (
        raw_events.withColumn("planned_departure_ts", f.to_timestamp("planned_departure"))
        .withColumn("actual_departure_ts", f.to_timestamp("actual_departure"))
        .withColumn(
            "delay_minutes",
            f.when(f.col("cancelled"), None).otherwise(
                (
                    f.col("actual_departure_ts").cast("long")
                    - f.col("planned_departure_ts").cast("long")
                )
                / 60,
            ),
        )
        .withColumn("is_delayed", f.coalesce(f.col("delay_minutes"), f.lit(0)) >= f.lit(5))
        .withColumn(
            "platform_changed",
            (
                f.coalesce(f.col("planned_platform"), f.lit(""))
                != f.coalesce(f.col("actual_platform"), f.lit(""))
            )
            & ~f.col("cancelled"),
        )
        .withColumn("service_date", f.to_date("planned_departure_ts"))
        .withColumn("weekday", f.date_format("planned_departure_ts", "EEEE"))
        .withColumn("is_weekend", f.dayofweek("planned_departure_ts").isin([1, 7]))
    )


def build_route_reliability(silver_events: DataFrame, routes: DataFrame) -> DataFrame:
    events = silver_events.join(routes, on="route_id", how="left")
    return (
        events.groupBy(
            "route_id",
            "origin_name",
            "destination_name",
            "route_type",
            "train_category_focus",
            "distance_km",
        )
        .agg(
            f.count("*").alias("event_count"),
            f.avg("delay_minutes").alias("avg_delay_minutes"),
            f.expr("percentile_approx(delay_minutes, 0.5)").alias("median_delay_minutes"),
            f.sum(f.col("is_delayed").cast("int")).alias("delayed_events"),
            f.sum(f.col("cancelled").cast("int")).alias("cancellations"),
            f.sum(f.col("platform_changed").cast("int")).alias("platform_changes"),
        )
        .withColumn(
            "delay_frequency_pct",
            f.round(f.col("delayed_events") / f.col("event_count") * 100, 2),
        )
        .withColumn(
            "cancellation_rate_pct",
            f.round(f.col("cancellations") / f.col("event_count") * 100, 2),
        )
        .withColumn(
            "platform_change_rate_pct",
            f.round(f.col("platform_changes") / f.col("event_count") * 100, 2),
        )
        .withColumn(
            "delay_per_100_km",
            f.round(
                f.coalesce(f.col("avg_delay_minutes"), f.lit(0))
                / f.col("distance_km")
                * 100,
                2,
            ),
        )
    )
