import re
from typing import List, Dict, Optional, Any
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownParser:
    """
    A class to parse and analyze markdown content without using external markdown parsers.

    Attributes:
        content (str): The markdown content to be parsed.
        config (Dict): Configuration for markdown elements.
        elements (List[Dict[str, Any]]): Parsed markdown elements maintaining order and associations.
    """

    def __init__(self, content: str, config_path: Optional[str] = None):
        """
        Initializes the MarkdownParser with content and optional configuration.

        Args:
            content (str): The markdown content to parse.
            config_path (Optional[str]): Path to the YAML configuration file.
        """
        self.content = content
        self.config = self._load_config(config_path)
        self.compiled_patterns = self._compile_patterns()
        self.elements = self._parse_markdown()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Loads the YAML configuration file.

        Args:
            config_path (Optional[str]): Path to the YAML configuration file.

        Returns:
            Dict: Configuration dictionary.
        """
        default_config = {
            "markdown_elements": {
                "header": {
                    "pattern": r"^(#{1,6})\s+(.*)",
                    "description": "Header elements (e.g., #, ##)",
                },
                "ordered_list": {
                    "pattern": r"^(\d+\.)\s+(.*)",
                    "description": "Ordered list items",
                },
                "unordered_list": {
                    "pattern": r"^([-*+])\s+(.*)",
                    "description": "Unordered list items",
                },
                "image": {"pattern": r"!\[.*?\]\((.*?)\)", "description": "Images"},
                "link": {"pattern": r"\[.*?\]\((.*?)\)", "description": "Hyperlinks"},
                "paragraph": {
                    "pattern": r"^(?!#{1,6}\s|[-*+]\s|\d+\.\s|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)).+",
                    "description": "Paragraph text",
                },
            }
        }

        if config_path:
            try:
                with open(config_path, "r", encoding="utf-8") as file:
                    config = yaml.safe_load(file)
                    logger.info(f"Configuration loaded from {config_path}.")
                    return config
            except Exception as e:
                logger.error(f"Failed to load configuration file: {e}")
                logger.info("Using default configuration.")

        logger.info("Using default configuration.")
        return default_config

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compiles regex patterns for markdown elements.

        Returns:
            Dict[str, re.Pattern]: Dictionary of compiled regex patterns.
        """
        patterns = {}
        for element, props in self.config.get("markdown_elements", {}).items():
            try:
                patterns[element] = re.compile(props["pattern"])
                logger.debug(f"Compiled pattern for {element}: {props['pattern']}")
            except re.error as e:
                logger.error(f"Invalid regex pattern for {element}: {e}")
        return patterns

    def _parse_markdown(self) -> List[Dict[str, Any]]:
        """
        Parses the markdown content into structured elements.

        Returns:
            List[Dict[str, Any]]: List of parsed markdown elements with type, content, and parent associations.
        """
        elements = []
        current_parent = None

        lines = self.content.split("\n")
        for line in lines:
            line = line.rstrip()
            if not line.strip():
                continue  # Skip empty lines

            matched = False
            for element, pattern in self.compiled_patterns.items():
                match = pattern.match(line)
                if match:
                    if element == "header":
                        header_level = len(match.group(1))
                        header_text = match.group(2).strip()
                        current_parent = header_text
                        elements.append(
                            {
                                "type": f"header_level_{header_level}",
                                "content": header_text,
                                "parent": None,
                            }
                        )
                    elif element in ["ordered_list", "unordered_list"]:
                        list_item = match.group(2).strip()
                        elements.append(
                            {
                                "type": element,
                                "content": list_item,
                                "parent": current_parent,
                            }
                        )
                    elif element == "image":
                        image_url = match.group(1).strip()
                        elements.append(
                            {
                                "type": "image",
                                "content": image_url,
                                "parent": current_parent,
                            }
                        )
                    elif element == "link":
                        link_url = match.group(1).strip()
                        elements.append(
                            {
                                "type": "link",
                                "content": link_url,
                                "parent": current_parent,
                            }
                        )
                    elif element == "paragraph":
                        paragraph_text = line.strip()
                        elements.append(
                            {
                                "type": "paragraph",
                                "content": paragraph_text,
                                "parent": current_parent,
                            }
                        )
                    matched = True
                    logger.debug(f"Matched {element}: {line}")
                    break  # Stop checking other patterns if matched

            if not matched:
                # If line doesn't match any pattern, treat it as a paragraph
                elements.append(
                    {
                        "type": "paragraph",
                        "content": line.strip(),
                        "parent": current_parent,
                    }
                )
                logger.debug(f"Default to paragraph: {line}")

        logger.info("Parsed markdown content into elements.")
        return elements

    def summarize_structure(self) -> Dict[str, int]:
        """
        Summarizes the structure of markdown elements by counting their occurrences.

        Returns:
            Dict[str, int]: Dictionary with counts of each markdown element.
        """
        summary = {}
        for elem in self.elements:
            elem_type = elem.get("type")
            summary[elem_type] = summary.get(elem_type, 0) + 1
        logger.debug(f"Structure summary: {summary}")
        return summary

    def filter_elements(self, elements: List[str]) -> List[Dict[str, Any]]:
        """
        Filters the markdown elements to include only the specified types.

        Args:
            elements (List[str]): List of markdown element types to include.

        Returns:
            List[Dict[str, Any]]: Filtered list of markdown elements.
        """
        filtered = [elem for elem in self.elements if elem["type"] in elements]
        logger.info(f"Filtered elements to include: {elements}")
        return filtered

    def extract_links(self) -> List[str]:
        """
        Extracts all hyperlinks from the markdown content.

        Returns:
            List[str]: List of extracted hyperlink URLs.
        """
        links = [elem["content"] for elem in self.elements if elem["type"] == "link"]
        logger.info(f"Extracted {len(links)} links.")
        return links

    def extract_images(self) -> List[str]:
        """
        Extracts all image URLs from the markdown content.

        Returns:
            List[str]: List of extracted image URLs.
        """
        images = [elem["content"] for elem in self.elements if elem["type"] == "image"]
        logger.info(f"Extracted {len(images)} images.")
        return images

    def generate_toc(self) -> str:
        """
        Generates a table of contents based on headers in the markdown content.

        Returns:
            str: Markdown formatted table of contents.
        """
        headers = [
            elem for elem in self.elements if elem["type"].startswith("header_level_")
        ]
        toc_lines = ["## Table of Contents\n"]
        for header in headers:
            level = int(header["type"].split("_")[-1])
            title = header["content"]
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- [{title}](#{self._slugify(title)})")
        toc = "\n".join(toc_lines)
        logger.info("Generated table of contents.")
        return toc

    def _slugify(self, text: str) -> str:
        """
        Converts text to a slug suitable for markdown links.

        Args:
            text (str): The text to slugify.

        Returns:
            str: Slugified text.
        """
        slug = re.sub(r"[^\w\s-]", "", text).lower()
        slug = re.sub(r"\s+", "-", slug)
        return slug

    def replace_links(self, replacement: str) -> str:
        """
        Replaces all links in the markdown content with a replacement string.

        Args:
            replacement (str): The string to replace links with.

        Returns:
            str: Updated markdown content with links replaced.
        """
        updated_content = self.content
        for elem in self.elements:
            if elem["type"] == "link":
                # Replace the entire markdown link syntax [text](url) with the replacement
                pattern = re.escape(f"[{elem.get('content')}]({elem.get('content')})")
                updated_content = re.sub(
                    r"\[.*?\]\(" + re.escape(elem["content"]) + r"\)",
                    replacement,
                    updated_content,
                )
        logger.info("Replaced all links in the content.")
        return updated_content

    def extract_plain_text_with_associations(self) -> List[Dict[str, Any]]:
        """
        Extracts plain text from the markdown content, maintaining order and associating
        each text block with its parent element (e.g., headers).

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing element type and plain text.
        """
        plain_text_elements = []
        current_parent = None

        for elem in self.elements:
            elem_type = elem["type"]
            content = elem["content"]

            if elem_type.startswith("header_level_"):
                current_parent = content
                plain_text_elements.append(
                    {"type": elem_type, "content": content, "parent": None}
                )
            elif elem_type in [
                "paragraph",
                "ordered_list",
                "unordered_list",
                "blockquote",
                "code",
            ]:
                plain_text_elements.append(
                    {"type": elem_type, "content": content, "parent": current_parent}
                )
            elif elem_type in ["link", "image"]:
                # Optionally handle links and images if you want to include their URLs as plain text
                plain_text_elements.append(
                    {"type": elem_type, "content": content, "parent": current_parent}
                )
            # Add more element types as needed

        logger.info("Extracted plain text with associations.")
        return plain_text_elements

    def extract_plain_text(self) -> str:
        """
        Extracts plain text from the markdown content by removing markdown syntax,
        links, images, and other markdown elements.

        Returns:
            str: The extracted plain text.
        """
        plain_text_elements = self.extract_plain_text_with_associations()
        plain_text = "\n".join(
            [
                elem["content"]
                for elem in plain_text_elements
                if elem["type"] not in ["link", "image"]
            ]
        )
        logger.info("Extracted plain text from markdown content.")
        return plain_text

    def get_statistics(self) -> Dict[str, Any]:
        """
        Provides a comprehensive set of statistics about the markdown content.

        Returns:
            Dict[str, Any]: Dictionary containing various statistics.
        """
        stats = {
            "summary": self.summarize_structure(),
            "total_links": len(self.extract_links()),
            "total_images": len(self.extract_images()),
            "toc": self.generate_toc(),
            "plain_text_length": len(self.extract_plain_text()),
            "plain_text_with_associations": self.extract_plain_text_with_associations(),
        }
        logger.info("Compiled markdown statistics.")
        return stats
