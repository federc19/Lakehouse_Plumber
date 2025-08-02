"""Test sink write generator."""

import pytest
from lhp.generators.write.sink import SinkWriteGenerator
from lhp.models.config import Action, WriteTarget, WriteTargetType


class TestSinkWriteGenerator:
    """Test sink write generator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SinkWriteGenerator()

    def test_generate_delta_sink_with_table_name(self):
        """Test generating a delta sink with table name."""
        action = Action(
            name="test_sink",
            type="write",
            source="v_test_source",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                format="delta",
                options={"tableName": "catalog.schema.table"}
            )
        )

        result = self.generator.generate(action, {})
        
        expected_sink = 'dlt.create_sink(name="test_sink_sink", format="delta", options={"tableName": "catalog.schema.table"})'
        expected_flow = '''@dlt.append_flow(name="test_sink_sink_append_flow", target="test_sink_sink")
def test_sink_sink_append_flow():
    return spark.readStream.table("v_test_source")'''
        
        assert expected_sink in result
        assert expected_flow in result

    def test_generate_delta_sink_with_path(self):
        """Test generating a delta sink with path."""
        action = Action(
            name="test_sink",
            type="write",
            source="v_test_source",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                format="delta",
                options={"path": "/path/to/table"}
            )
        )

        result = self.generator.generate(action, {})
        
        expected_sink = 'dlt.create_sink(name="test_sink_sink", format="delta", options={"path": "/path/to/table"})'
        assert expected_sink in result

    def test_generate_kafka_sink(self):
        """Test generating a kafka sink."""
        action = Action(
            name="test_sink",
            type="write",
            source="v_test_source",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                format="kafka",
                options={
                    "kafka.bootstrap.servers": "host:port",
                    "topic": "my_topic"
                }
            )
        )

        result = self.generator.generate(action, {})
        
        expected_sink = 'dlt.create_sink(name="test_sink_sink", format="kafka", options={"kafka.bootstrap.servers": "host:port", "topic": "my_topic"})'
        assert expected_sink in result

    def test_generate_sink_without_source(self):
        """Test generating a sink without source (standalone sink)."""
        action = Action(
            name="test_sink",
            type="write",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                format="delta",
                options={"tableName": "catalog.schema.table"}
            )
        )

        result = self.generator.generate(action, {})
        
        expected_sink = 'dlt.create_sink(name="test_sink_sink", format="delta", options={"tableName": "catalog.schema.table"})'
        # Should not have append flow
        assert expected_sink in result
        assert "append_flow" not in result

    def test_generate_sink_with_custom_name(self):
        """Test generating a sink with custom name in write_target."""
        action = Action(
            name="test_sink",
            type="write",
            source="v_test_source",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                name="custom_sink_name",
                format="delta",
                options={"tableName": "catalog.schema.table"}
            )
        )

        result = self.generator.generate(action, {})
        
        expected_sink = 'dlt.create_sink(name="custom_sink_name", format="delta", options={"tableName": "catalog.schema.table"})'
        assert expected_sink in result

    def test_missing_format_raises_error(self):
        """Test that missing format raises an error."""
        action = Action(
            name="test_sink",
            type="write",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                options={"tableName": "catalog.schema.table"}
            )
        )

        with pytest.raises(ValueError, match="must have 'format' specified"):
            self.generator.generate(action, {})

    def test_missing_options_raises_error(self):
        """Test that missing options raises an error."""
        action = Action(
            name="test_sink",
            type="write",
            write_target=WriteTarget(
                type=WriteTargetType.SINK,
                format="delta"
            )
        )

        with pytest.raises(ValueError, match="must have 'options' specified"):
            self.generator.generate(action, {})

    def test_missing_write_target_raises_error(self):
        """Test that missing write_target raises an error."""
        action = Action(
            name="test_sink",
            type="write"
        )

        with pytest.raises(ValueError, match="must have write_target configuration"):
            self.generator.generate(action, {}) 