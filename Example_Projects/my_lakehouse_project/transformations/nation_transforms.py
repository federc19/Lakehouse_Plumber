from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F

def enrich_nation_data(df: DataFrame, spark: SparkSession, parameters: dict) -> DataFrame:

    enrich_value = parameters.get("enrich_value")

    df = df.withColumn("enriched_column", F.lit(enrich_value))

    return df
