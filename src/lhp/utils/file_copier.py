"""File copying utilities for LakehousePlumber."""

import logging
import shutil
from pathlib import Path
from typing import Optional, List, Set


class FileCopier:
    """Utility class for copying Python function files to generated directories."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
        self.copied_files: Set[Path] = set()

    def copy_python_function_files(
        self, 
        module_path: str, 
        output_dir: Path,
        state_manager=None,
        source_yaml: Optional[Path] = None,
        environment: Optional[str] = None
    ) -> List[Path]:
        """
        Copy Python function files referenced by module_path to the output directory.
        
        Args:
            module_path: The module path from the YAML configuration (e.g., "functions/get_nation.py")
            output_dir: The output directory where files should be copied
            state_manager: Optional state manager for tracking copied files
            source_yaml: Optional source YAML path for state tracking
            environment: Optional environment for state tracking
            
        Returns:
            List of copied file paths
        """
        if not output_dir:
            return []

        copied_files = []
        
        try:
            # Convert module path to source file path
            source_file = self._resolve_source_file(module_path)
            if not source_file or not source_file.exists():
                self.logger.warning(f"Source file not found: {module_path}")
                return []

            # Determine the target directory structure
            target_dir, target_file = self._determine_target_structure(module_path, output_dir)
            
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            target_path = target_dir / target_file
            if target_path not in self.copied_files:
                shutil.copy2(source_file, target_path)
                self.copied_files.add(target_path)
                copied_files.append(target_path)
                
                self.logger.info(f"Copied {source_file} to {target_path}")
                
                # Track the copied file in state manager if provided
                if state_manager and source_yaml and environment:
                    self._track_copied_file(state_manager, target_path, source_yaml, environment)
            
        except Exception as e:
            self.logger.error(f"Error copying file {module_path}: {e}")
            
        return copied_files

    def _resolve_source_file(self, module_path: str) -> Optional[Path]:
        """
        Resolve the module path to an actual file path.
        
        Args:
            module_path: The module path from YAML (e.g., "functions/get_nation.py")
            
        Returns:
            Path to the source file, or None if not found
        """
        # Handle different path formats
        if module_path.startswith("/"):
            # Absolute path
            return Path(module_path)
        else:
            # Relative path from project root
            return self.project_root / module_path

    def _determine_target_structure(self, module_path: str, output_dir: Path) -> tuple[Path, str]:
        """
        Determine the target directory and filename for the copied file.
        
        Args:
            module_path: The module path from YAML (e.g., "functions/get_nation.py")
            output_dir: The base output directory
            
        Returns:
            Tuple of (target_directory, target_filename)
        """
        # Parse the module path to extract directory and filename
        path_parts = module_path.replace("\\", "/").split("/")
        
        if len(path_parts) == 1:
            # Just a filename (e.g., "get_nation.py")
            target_dir = output_dir
            target_file = path_parts[0]
        else:
            # Has directory structure (e.g., "functions/get_nation.py")
            # Copy the entire directory structure
            target_dir = output_dir
            for part in path_parts[:-1]:
                target_dir = target_dir / part
            target_file = path_parts[-1]
            
        return target_dir, target_file

    def _track_copied_file(self, state_manager, target_path: Path, source_yaml: Path, environment: str):
        """
        Track the copied file in the state manager.
        
        Args:
            state_manager: The state manager instance
            target_path: Path to the copied file
            source_yaml: Path to the source YAML file
            environment: Environment name
        """
        try:
            # Track the copied file as a generated file
            state_manager.track_generated_file(
                generated_path=target_path,
                source_yaml=source_yaml,
                environment=environment,
                pipeline="",  # Empty for copied files
                flowgroup="",  # Empty for copied files
                file_type="copied_function"  # Mark as copied function file
            )
        except Exception as e:
            self.logger.warning(f"Could not track copied file {target_path}: {e}")

    def get_copied_files(self) -> Set[Path]:
        """Get the set of files that have been copied in this session."""
        return self.copied_files.copy() 