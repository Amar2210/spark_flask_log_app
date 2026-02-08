import spark_config
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

spark = SparkSession.builder \
    .appName("LogAnalyzer") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".csv")]
file_path = os.path.join(RAW_DATA_DIR, csv_files[0])
df = spark.read.csv(file_path, header=True, inferSchema=True)

# 1. What do "bad" status values look like?
print("=== SAMPLE BAD STATUS VALUES (not standard HTTP codes) ===")
valid_statuses = ["200", "301", "302", "304", "400", "401", "403", "404", "405", "500", "502", "503"]
bad_status = df.filter(~col("status").isin(valid_statuses) & col("status").isNotNull())
print(f"Rows with non-standard status: {bad_status.count():,}")
bad_status.select("status", "protocol", "url", "type", "label").show(10, truncate=80)

# 2. What does type actually contain?
print("\n=== TOP 20 VALUES IN 'type' COLUMN ===")
df.groupBy("type").count().orderBy("count", ascending=False).show(20, truncate=False)

# 3. What does label actually contain?
print("\n=== TOP 20 VALUES IN 'label' COLUMN ===")
df.groupBy("label").count().orderBy("count", ascending=False).show(20, truncate=False)

# 4. What does protocol actually contain?
print("\n=== TOP 20 VALUES IN 'protocol' COLUMN ===")
df.groupBy("protocol").count().orderBy("count", ascending=False).show(20, truncate=False)

spark.stop()
print("DONE")