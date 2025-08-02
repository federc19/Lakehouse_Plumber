from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp, lit, monotonically_increasing_id

def update_table_metadata(df: DataFrame, spark: SparkSession, parameters: dict):
    """
    Update or insert metadata info for a table in Unity Catalog.

    Parameters:
        spark (SparkSession): Active Spark session.
        target_table (str): The name of the target table to track.
        tracker_table (str): The full name of the metadata tracker table (e.g., 'catalog.schema.metadata_tracker').
    """

    target_table = parameters.get("target_table")
    tracker_table = "fed.default.utility_table_watermark"

    # Define default watermark
    default_timestamp = "1900-01-01 00:00:00"

    spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {tracker_table} (
        id BIGINT GENERATED ALWAYS AS IDENTITY,
        table_name STRING,
        watermark TIMESTAMP,
        last_modified TIMESTAMP
        )
    """
    )
    
    # Use MERGE to insert or update the metadata
    spark.sql(f"""
        MERGE INTO {tracker_table} AS target
        USING (
            SELECT '{target_table}' AS table_name,
                   TIMESTAMP('{default_timestamp}') AS watermark,
                   current_timestamp() AS last_modified
        ) AS source
        ON target.table_name = source.table_name
        WHEN MATCHED THEN
            UPDATE SET target.watermark = current_timestamp(),
                       target.last_modified = current_timestamp()
        WHEN NOT MATCHED THEN
            INSERT (table_name, watermark, last_modified)
            VALUES (source.table_name, source.watermark, source.last_modified)
    """)

    df_watermark = spark.sql(f"SELECT * FROM {tracker_table} WHERE table_name = '{target_table}'")
    df = df.crossJoin(df_watermark)
    return df
