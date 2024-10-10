# data_loader.py

import os
from typing import List, Dict, Any
from utils.config_loader import load_config
from utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """
    A class for loading documents from local and remote sources.

    Attributes:
        sources (List[Dict[str, Any]]): A list of data source configurations.
    """

    def __init__(self, config_path: str):
        """
        Initializes the DataLoader with configurations.

        Args:
            config_path (str): Path to the data loader configuration file.
        """
        self.config = load_config(config_path)
        self.sources = self.config.get("data_sources", [])
        logger.info("DataLoader initialized with sources: %s", self.sources)

    def load_data(self) -> List[str]:
        """
        Loads data from all configured sources.

        Returns:
            List[str]: A list of loaded documents as strings.
        """
        documents = []
        for source in self.sources:
            source_type = source.get("type")
            if source_type == "local":
                documents.extend(self._load_local_files(source))
            elif source_type == "remote":
                documents.extend(self._load_remote_files(source))
            else:
                logger.warning("Unknown source type: %s", source_type)
        return documents

    def _load_local_files(self, source: Dict[str, Any]) -> List[str]:
        """
        Loads documents from the local file system.

        Args:
            source (Dict[str, Any]): Configuration for the local source.

        Returns:
            List[str]: A list of document contents.
        """
        directory = source.get("directory")
        file_extensions = source.get("file_extensions", [".txt", ".md"])
        documents = []

        if not directory or not os.path.exists(directory):
            logger.error("Directory does not exist: %s", directory)
            return documents

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            documents.append(content)
                            logger.debug("Loaded file: %s", file_path)
                    except Exception as e:
                        logger.error("Failed to read file %s: %s", file_path, e)
        return documents

    def _load_remote_files(self, source: Dict[str, Any]) -> List[str]:
        """
        Loads documents from remote sources.

        Args:
            source (Dict[str, Any]): Configuration for the remote source.

        Returns:
            List[str]: A list of document contents.
        """
        import requests

        urls = source.get("urls", [])
        documents = []

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                documents.append(response.text)
                logger.debug("Loaded remote file: %s", url)
            except requests.RequestException as e:
                logger.error("Failed to fetch URL %s: %s", url, e)
        return documents
