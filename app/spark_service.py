import spark_config
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, col, collect_set, round as spark_round
from pyspark.sql.functions import min as spark_min, max as spark_max, unix_timestamp
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DATA_DIR = os.path.join(BASE_DIR, "data", "clean")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")

# Create Spark session once
spark = SparkSession.builder \
    .appName("LogAnalyzer") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()


def load_clean_data():
    return spark.read.parquet(os.path.join(CLEAN_DATA_DIR, "logs_clean.parquet"))


def clean_and_save(file_path):
    """Read raw CSV, clean it, save as parquet"""
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    valid_protocols = ["HTTP/1.1", "HTTP/1.0"]
    valid_types = ["benign", "bot", "sqli", "scanning", "rce"]
    valid_labels = ["0", "1"]

    df_clean = df.filter(
        col("protocol").isin(valid_protocols) &
        col("type").isin(valid_types) &
        col("label").isin(valid_labels)
    )

    df_clean = df_clean \
        .drop("extra") \
        .withColumn("label", col("label").cast("integer")) \
        .withColumn("no", col("no").cast("long")) \
        .withColumn("size", col("size").cast("long")) \
        .withColumn("status", col("status").cast("integer"))

    os.makedirs(CLEAN_DATA_DIR, exist_ok=True)
    df_clean.write.mode("overwrite").parquet(
        os.path.join(CLEAN_DATA_DIR, "logs_clean.parquet")
    )

    return {
        "original_rows": df.count(),
        "clean_rows": df_clean.count(),
        "dropped_rows": df.count() - df_clean.count()
    }


def get_summary():
    df = load_clean_data()
    total = df.count()
    breakdown = df.groupBy("type") \
        .agg(count("*").alias("count")) \
        .withColumn("percentage", spark_round((col("count") / total) * 100, 2)) \
        .orderBy("count", ascending=False)

    rows = [row.asDict() for row in breakdown.collect()]
    return {"total_requests": total, "type_breakdown": rows}


def get_top_attackers(limit=20):
    df = load_clean_data()
    df_attacks = df.filter(col("type") != "benign")
    result = df_attacks.groupBy("ip") \
        .agg(
            count("*").alias("attack_count"),
            collect_set("type").alias("attack_types")
        ) \
        .orderBy("attack_count", ascending=False) \
        .limit(limit)

    rows = [row.asDict() for row in result.collect()]
    for row in rows:
        row["attack_types"] = list(row["attack_types"])
    return rows


def get_targeted_urls(limit=20):
    df = load_clean_data()
    df_attacks = df.filter(col("type") != "benign")
    result = df_attacks.groupBy("url", "type") \
        .agg(count("*").alias("attack_count")) \
        .orderBy("attack_count", ascending=False) \
        .limit(limit)

    return [row.asDict() for row in result.collect()]


def get_direct_access(limit=15):
    df = load_clean_data()
    df_attacks = df.filter(col("type") != "benign")
    direct = df_attacks.filter(
        (col("referrer").isNull()) | (col("referrer") == "-")
    )

    total_attacks = df_attacks.count()
    direct_count = direct.count()

    urls = direct.groupBy("url", "type") \
        .agg(count("*").alias("count")) \
        .orderBy("count", ascending=False) \
        .limit(limit)

    return {
        "total_attacks": total_attacks,
        "direct_access_attacks": direct_count,
        "percentage_direct": round((direct_count / total_attacks) * 100, 2),
        "top_urls": [row.asDict() for row in urls.collect()]
    }


def get_rate_analysis(limit=20):
    df = load_clean_data()
    result = df.groupBy("ip") \
        .agg(
            count("*").alias("total_requests"),
            spark_min("time").alias("first_seen"),
            spark_max("time").alias("last_seen")
        ) \
        .withColumn(
            "duration_seconds",
            unix_timestamp("last_seen") - unix_timestamp("first_seen")
        ) \
        .withColumn(
            "requests_per_minute",
            spark_round(
                col("total_requests") / (col("duration_seconds") / 60 + 1), 2
            )
        ) \
        .orderBy("requests_per_minute", ascending=False) \
        .limit(limit)

    rows = [row.asDict() for row in result.collect()]
    for row in rows:
        row["first_seen"] = str(row["first_seen"])
        row["last_seen"] = str(row["last_seen"])
    return rows