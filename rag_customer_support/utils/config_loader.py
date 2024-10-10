import yaml
from typing import Any, Dict
import os


def load_config(config_path: str) -> Dict[str, Any]:
    """Loads a YAML configuration file into a dictionary.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: Configuration parameters as a dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config
