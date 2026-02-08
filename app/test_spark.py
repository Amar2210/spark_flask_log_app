import spark_config  # must be FIRST import
from pyspark.sql import SparkSession
import sys

spark = SparkSession.builder \
    .appName("SparkTest") \
    .master("local[*]") \
    .getOrCreate()

print("Spark is running!")
print(f"Spark version: {spark.version}")
print(f"Python being used: {sys.executable}")

data = [("A", 10), ("B", 20), ("C", 30)]
df = spark.createDataFrame(data, ["name", "value"])
df.show()

spark.stop()
print("SUCCESS")