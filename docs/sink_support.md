# Sink Support in Lakehouse Plumber

Lakehouse Plumber now supports the `dlt.create_sink()` API from Databricks Lakeflow Declarative Pipelines. This allows you to create sinks for writing data to external systems like Apache Kafka or Delta tables.

## Overview

The `create_sink()` function writes to an event streaming service such as Apache Kafka or Azure Event Hubs, or to a Delta table from a declarative pipeline. After creating a sink, you use it in an append flow to write data into the sink.

## Supported Sink Types

- **Delta Sinks**: Write to Delta tables (managed or external)
- **Kafka Sinks**: Write to Apache Kafka topics

## YAML Configuration

### Basic Sink Configuration

```yaml
- name: create_my_sink
  type: write
  source: v_my_source_view  # Optional - if provided, creates append flow
  write_target:
    type: sink
    format: delta  # or "kafka"
    options:
      tableName: "catalog.schema.table"  # For Delta sinks
      # or
      path: "/path/to/delta/table"       # For Delta sinks
      # or
      kafka.bootstrap.servers: "host:port"  # For Kafka sinks
      topic: "my_topic"                     # For Kafka sinks
```

### Delta Sink Examples

#### Delta Sink with Table Name
```yaml
- name: create_delta_sink_with_table_name
  type: write
  source: v_my_source
  write_target:
    type: sink
    format: delta
    options:
      tableName: "{catalog}.{schema}.my_sink_table"
```

#### Delta Sink with Path
```yaml
- name: create_delta_sink_with_path
  type: write
  source: v_my_source
  write_target:
    type: sink
    format: delta
    options:
      path: "/path/to/my/delta/table"
```

#### Standalone Delta Sink (No Source)
```yaml
- name: create_standalone_sink
  type: write
  write_target:
    type: sink
    format: delta
    options:
      tableName: "{catalog}.{schema}.standalone_sink"
```

### Kafka Sink Examples

#### Basic Kafka Sink
```yaml
- name: create_kafka_sink
  type: write
  source: v_my_source
  write_target:
    type: sink
    format: kafka
    options:
      kafka.bootstrap.servers: "host:port"
      topic: "my_topic"
```

#### Kafka Sink with Checkpoint Location
```yaml
- name: create_kafka_sink_with_checkpoint
  type: write
  source: v_my_source
  write_target:
    type: sink
    format: kafka
    options:
      kafka.bootstrap.servers: "host:port"
      topic: "my_topic"
      checkpointLocation: "/tmp/checkpoint/kafka_sink"
```

### Custom Sink Names

You can specify a custom name for your sink:

```yaml
- name: create_custom_sink
  type: write
  source: v_my_source
  write_target:
    type: sink
    name: "my_custom_sink_name"  # Custom name
    format: delta
    options:
      tableName: "{catalog}.{schema}.my_table"
```

## Generated Code

When you run `python -m lhp.cli.main generate --env dev`, the following code will be generated:

### Delta Sink Example
```python
# Generated code for delta sink with table name
dlt.create_sink(name="create_delta_sink_with_table_name_sink", format="delta", options={"tableName": "catalog.schema.my_sink_table"})

@dlt.append_flow(name="create_delta_sink_with_table_name_sink_append_flow", target="create_delta_sink_with_table_name_sink")
def create_delta_sink_with_table_name_sink_append_flow():
    return spark.readStream.table("v_my_source")
```

### Kafka Sink Example
```python
# Generated code for kafka sink
dlt.create_sink(name="create_kafka_sink_sink", format="kafka", options={"kafka.bootstrap.servers": "host:port", "topic": "my_topic"})

@dlt.append_flow(name="create_kafka_sink_sink_append_flow", target="create_kafka_sink_sink")
def create_kafka_sink_sink_append_flow():
    return spark.readStream.table("v_my_source")
```

## Validation

The system validates sink configurations to ensure:

### Required Fields
- `format`: Must be "delta" or "kafka"
- `options`: Must be specified

### Delta Sink Validation
- Must have either `path` or `tableName` in options

### Kafka Sink Validation
- Must have `kafka.bootstrap.servers` in options
- Must have `topic` in options

## Complete Example

Here's a complete example showing different sink configurations:

```yaml
# This pipeline demonstrates different sink configurations
pipeline: bronze_load
flowgroup: sink_examples

actions:
  - name: load_nation_for_sinks
    type: load
    operational_metadata: ["_processing_timestamp"]
    readMode: stream
    source:
      type: delta
      database: "{catalog}.{raw_schema}"
      table: nation
    target: v_nation_for_sinks
    description: "Load nation table for sink examples"

  - name: create_delta_sink_with_path
    type: write
    source: v_nation_for_sinks
    write_target:
      type: sink
      format: delta
      options:
        path: "/path/to/my/delta/table"

  - name: create_delta_sink_with_table_name
    type: write
    source: v_nation_for_sinks
    write_target:
      type: sink
      format: delta
      options:
        tableName: "{catalog}.{bronze_schema}.sinkTableForTracking"

  - name: create_kafka_sink
    type: write
    source: v_nation_for_sinks
    write_target:
      type: sink
      format: kafka
      options:
        kafka.bootstrap.servers: "host:port"
        topic: "my_topic"
        checkpointLocation: "/tmp/checkpoint/kafka_sink"

  - name: create_delta_sink_no_source
    type: write
    write_target:
      type: sink
      format: delta
      options:
        tableName: "{catalog}.{bronze_schema}.standalone_sink"
```

## Important Notes

1. **Append Flow Only**: Sinks only support append flows. Other flow types like `create_auto_cdc_flow` are not supported.

2. **Full Refresh**: Running a full refresh update does not clear data from sinks. Any reprocessed data will be appended to the sink, and existing data will not be altered.

3. **Expectations**: Lakeflow Declarative Pipelines expectations are not supported with the `sink` API.

4. **Table Names**: For Delta sinks, table names must be fully qualified:
   - Unity Catalog tables: `<catalog>.<schema>.<table>`
   - Hive metastore tables: `<schema>.<table>`

## Migration from Existing Code

If you have existing `dlt.create_sink()` calls in your code, you can migrate them to YAML configuration:

### Before (Direct Code)
```python
dlt.create_sink(
    name="my_sink",
    format="delta",
    options={"tableName": "catalog.schema.table"}
)

@dlt.append_flow(name="my_flow", target="my_sink")
def my_flow():
    return spark.readStream.table("my_source")
```

### After (YAML Configuration)
```yaml
- name: create_my_sink
  type: write
  source: my_source
  write_target:
    type: sink
    name: "my_sink"
    format: delta
    options:
      tableName: "catalog.schema.table"
```

This approach provides better maintainability, validation, and consistency with the rest of your Lakehouse Plumber pipeline configurations. 