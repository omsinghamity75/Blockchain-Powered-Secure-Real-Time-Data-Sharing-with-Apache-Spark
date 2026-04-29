from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, expr, when


def build_session() -> SparkSession:
    return (
        SparkSession.builder.appName("SecureRealTimeDataSharing")
        .master("local[1]")
        .getOrCreate()
    )


def main() -> None:
    spark = build_session()
    spark.sparkContext.setLogLevel("ERROR")

    # `range` is created entirely on the JVM side, which avoids the Python
    # worker crash you were hitting on Windows with the Store Python build.
    dataset = (
        spark.range(0, 6)
        .withColumn("source", expr("concat('sensor-', CAST(id + 1 AS STRING))"))
        .withColumn(
            "owner",
            when((col("id") % 2) == 0, "team-alpha").otherwise("team-beta"),
        )
        .withColumn("temperature", (col("id") * 3 + 26).cast("int"))
        .withColumn("humidity", (col("id") * 2 + 55).cast("int"))
        .withColumn(
            "status",
            when(col("temperature") >= 32, "alert").otherwise("verified"),
        )
        .withColumn("processed_at", current_timestamp())
        .select(
            "source",
            "owner",
            "temperature",
            "humidity",
            "status",
            "processed_at",
        )
    )

    print("Secure real-time data sharing Spark output:")
    dataset.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
