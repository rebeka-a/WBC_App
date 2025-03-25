import json, yaml, posixpath
import pandas as pd
from io import StringIO

class DataHandler:
    def __init__(self, filesystem, root_path):
        """
        Initialize the DataHandler with an fsspec filesystem and a root path.

        Args:
            filesystem: An fsspec-compatible filesystem object.
            root_path: The root directory for file operations.
        """
        self.filesystem = filesystem
        self.root_path = root_path

    def join(self, *args):
        return posixpath.join(*args)

    def _resolve_path(self, relative_path):
        """
        Resolve the full path using the filesystem's path joining capabilities.

        Args:
            relative_path: The path relative to the root directory.

        Returns:
            The resolved absolute path.
        """
        return self.join(self.root_path, relative_path)

    def exists(self, relative_path):
        """
        Check if a file exists.

        Args:
            relative_path: The path relative to the root directory.

        Returns:
            True if the file exists, False otherwise.
        """
        full_path = self._resolve_path(relative_path)
        return self.filesystem.exists(full_path)

    def read_text(self, relative_path):
        """
        Read the contents of a text file.

        Args:
            relative_path: The path relative to the root directory.

        Returns:
            The content of the file as a string.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "r") as f:
            return f.read()

    def read_binary(self, relative_path):
        """
        Read the contents of a binary file.

        Args:
            relative_path: The path relative to the root directory.

        Returns:
            The content of the file as bytes.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "rb") as f:
            return f.read()

    def write_text(self, relative_path, content):
        """
        Write text content to a file.

        Args:
            relative_path: The path relative to the root directory.
            content: The text content to write.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "w") as f:
            f.write(content)

    def write_binary(self, relative_path, content):
        """
        Write binary content to a file.

        Args:
            relative_path: The path relative to the root directory.
            content: The binary content to write.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "wb") as f:
            f.write(content)

    def load(self, relative_path, initial_value=None, **load_args):
        """
        Load data from a file based on its extension.

        Args:
            relative_path: The path relative to the root directory.
            initial_value: The value to return if the file does not exist. If None, raises FileNotFoundError.
            **load_args: Additional arguments to pass to the file loader (pd.read_csv).
        Returns:
            Parsed data (e.g., DataFrame, dict, str, bytes) depending on the file type, or the initial value if provided.
        """
        if not self.exists(relative_path):
            if initial_value is not None:
                return initial_value
            raise FileNotFoundError(f"File does not exist: {relative_path}")

        ext = posixpath.splitext(relative_path)[-1].lower()
        if ext == ".json":
            return json.loads(self.read_text(relative_path))
        elif ext in [".yaml", ".yml"]:
            return yaml.safe_load(self.read_text(relative_path))
        elif ext == ".csv":
            return pd.read_csv(StringIO(self.read_text(relative_path)), **load_args)       
        elif ext == ".txt":
            return self.read_text(relative_path)
        else:
            return self.read_binary(relative_path)

    def save(self, relative_path, content):
        """
        Save data to a file based on its extension.

        Args:
            relative_path: The path relative to the root directory.
            content: The content to save (e.g., DataFrame, dict, str, bytes).

        Raises:
            ValueError: If the content type doesn't match the file extension.
        """
        full_path = self._resolve_path(relative_path)
        parent_dir = posixpath.dirname(full_path)

        # Ensure the parent directory exists
        if not self.filesystem.exists(parent_dir):
            self.filesystem.mkdirs(parent_dir, exist_ok=True)

        ext = posixpath.splitext(relative_path)[-1].lower()

        if isinstance(content, pd.DataFrame) and ext == ".csv":
            self.write_text(relative_path, content.to_csv(index=False))
        elif isinstance(content, (dict, list)) and ext == ".json":
            self.write_text(relative_path, json.dumps(content, indent=4))
        elif isinstance(content, (dict, list)) and ext in [".yaml", ".yml"]:
            self.write_text(relative_path, yaml.dump(content, default_flow_style=False))
        elif isinstance(content, str) and ext == ".txt":
            self.write_text(relative_path, content)
        elif isinstance(content, bytes):
            self.write_binary(relative_path, content)
        else:
            raise ValueError(f"Unsupported content type for extension {ext}")
