"""Sink write generator."""

from typing import Dict, List
from ...core.base_generator import BaseActionGenerator
from ...models.config import Action
from ...utils.error_formatter import LHPError, ErrorCategory


class SinkWriteGenerator(BaseActionGenerator):
    """Generate sink write actions."""

    def __init__(self):
        super().__init__()
        self.add_import("import dlt")

    def generate(self, action: Action, context: dict) -> str:
        """Generate sink code."""
        target_config = action.write_target
        if not target_config:
            raise ValueError(
                "Sink action must have write_target configuration"
            )

        # Extract configuration - handle both WriteTarget objects and dictionaries
        if hasattr(target_config, "name"):
            # WriteTarget object
            sink_name = getattr(target_config, "name", None) or f"{action.name}_sink"
            sink_format = getattr(target_config, "format", None)
            sink_options = getattr(target_config, "options", {})
        else:
            # Dictionary
            sink_name = target_config.get("name") or f"{action.name}_sink"
            sink_format = target_config.get("format")
            sink_options = target_config.get("options", {})

        if not sink_format:
            raise ValueError(
                f"Sink '{sink_name}' must have 'format' specified in write_target"
            )

        if not sink_options:
            raise ValueError(
                f"Sink '{sink_name}' must have 'options' specified in write_target"
            )

        # Generate the sink creation code
        sink_code = self._generate_sink_creation(sink_name, sink_format, sink_options)
        
        # Generate append flow if source is specified
        append_flow_code = ""
        if action.source:
            source_views = self._extract_source_views(action.source)
            if source_views:
                append_flow_code = self._generate_append_flow(sink_name, source_views[0])

        return f"{sink_code}\n\n{append_flow_code}".strip()

    def _generate_sink_creation(self, sink_name: str, sink_format: str, sink_options: Dict) -> str:
        """Generate the dlt.create_sink call."""
        # Format options as a Python dictionary
        options_str = self._format_options_dict(sink_options)
        
        return f'dlt.create_sink(name="{sink_name}", format="{sink_format}", options={options_str})'

    def _generate_append_flow(self, sink_name: str, source_view: str) -> str:
        """Generate the append flow for the sink."""
        flow_name = f"{sink_name}_append_flow"
        
        return f'''@dlt.append_flow(name="{flow_name}", target="{sink_name}")
def {flow_name}():
    return spark.readStream.table("{source_view}")'''

    def _extract_source_views(self, source) -> List[str]:
        """Extract source view names from the source configuration."""
        if isinstance(source, str):
            return [source]
        elif isinstance(source, list):
            return [str(item) if isinstance(item, str) else item.get("name", str(item)) for item in source]
        else:
            return []

    def _format_options_dict(self, options: Dict) -> str:
        """Format options dictionary as a Python dictionary string."""
        if not options:
            return "{}"
        
        formatted_options = []
        for key, value in options.items():
            if isinstance(value, str):
                formatted_options.append(f'"{key}": "{value}"')
            else:
                formatted_options.append(f'"{key}": {value}')
        
        return "{" + ", ".join(formatted_options) + "}" 