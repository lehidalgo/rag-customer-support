# web_scraper.py

from typing import List, Dict, Any, Optional
from rag_customer_support.utils.config_loader import load_config
from rag_customer_support.utils.logger import get_logger
from bs4 import BeautifulSoup, Tag
import pickle
import requests
import time
import os

logger = get_logger(__name__)


class WebScraper:
    """
    A class for scraping web content, converting it to structured Markdown,
    and extracting metadata like image URLs and tables.

    Attributes:
        start_urls (List[str]): List of starting URLs to scrape.
        user_agent (str): User agent string for HTTP requests.
        delay (float): Delay between requests to avoid overloading servers.
    """

    def __init__(self, config_path: str):
        """
        Initializes the WebScraper with configurations.

        Args:
            config_path (str): Path to the web scraper configuration file.
        """
        self.config = load_config(config_path)
        self.start_urls = self.config.get("start_urls", [])
        self.user_agent = self.config.get("user_agent", "Mozilla/5.0")
        self.delay = self.config.get("delay", 1.0)
        logger.info("WebScraper initialized with start URLs: %s", self.start_urls)

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrapes content from the configured starting URLs.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing
            'content' (Markdown text) and 'metadata' (e.g., image URLs).
        """
        documents = []
        headers = {"User-Agent": self.user_agent}

        for url in self.start_urls:
            try:
                logger.debug("Scraping URL: %s", url)
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                content, metadata = self._parse_content(response.text, base_url=url)
                documents.append({"content": content, "metadata": metadata})
                logger.debug("Scraped content from: %s", url)
                time.sleep(self.delay)
            except requests.RequestException as e:
                logger.error("Failed to scrape URL %s: %s", url, e)

        return documents

    def _parse_content(self, html: str, base_url: str) -> tuple[str, Dict[str, Any]]:
        """
        Parses HTML content, converts it to Markdown, and extracts metadata.

        Args:
            html (str): HTML content as a string.
            base_url (str): Base URL of the page for resolving relative links.

        Returns:
            Tuple[str, Dict[str, Any]]: Markdown content and metadata dictionary.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts and styles
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        metadata = {"images": [], "tables": [], "urls": base_url}

        markdown_lines = []
        self._html_to_markdown(soup.body, markdown_lines, metadata, base_url)
        markdown_content = "\n".join(markdown_lines)
        return markdown_content, metadata

    def _html_to_markdown(
        self,
        element: Tag,
        markdown_lines: List[str],
        metadata: Dict[str, Any],
        base_url: str,
        indent_level: int = 0,
    ):
        """
        Recursively traverses the HTML DOM and converts elements to Markdown.

        Args:
            element (Tag): The current HTML element.
            markdown_lines (List[str]): Accumulator for Markdown lines.
            metadata (Dict[str, Any]): Accumulator for metadata like image URLs.
            base_url (str): Base URL for resolving relative links.
            indent_level (int): Current indentation level for nested structures.
        """
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Map HTML headers to Markdown headers
            header_level = int(element.name[1])
            header_prefix = "#" * header_level
            header_text = element.get_text(strip=True)
            markdown_lines.append(f"{header_prefix} {header_text}")
        elif element.name == "p":
            # Add paragraphs
            paragraph_text = element.get_text(strip=True)
            if paragraph_text:
                markdown_lines.append(paragraph_text)
        elif element.name == "ul":
            # Unordered lists
            for li in element.find_all("li", recursive=False):
                self._html_to_markdown(
                    li,
                    markdown_lines,
                    metadata,
                    base_url,
                    indent_level=indent_level + 1,
                )
        elif element.name == "ol":
            # Ordered lists
            for idx, li in enumerate(element.find_all("li", recursive=False), start=1):
                self._html_to_markdown(
                    li,
                    markdown_lines,
                    metadata,
                    base_url,
                    indent_level=indent_level + 1,
                )
        elif element.name == "li":
            # List items
            prefix = "  " * (indent_level - 1) + "- "
            li_text = element.get_text(strip=True)
            markdown_lines.append(f"{prefix}{li_text}")
            # Check for nested lists
            for child in element.find_all(["ul", "ol"], recursive=False):
                self._html_to_markdown(
                    child,
                    markdown_lines,
                    metadata,
                    base_url,
                    indent_level=indent_level + 1,
                )
        elif element.name in ["strong", "b"]:
            # Bold text
            bold_text = f"**{element.get_text(strip=True)}**"
            markdown_lines.append(bold_text)
        elif element.name in ["em", "i"]:
            # Italic text
            italic_text = f"*{element.get_text(strip=True)}*"
            markdown_lines.append(italic_text)
        elif element.name == "a":
            # Hyperlinks
            link_text = element.get_text(strip=True)
            href = element.get("href", "")
            full_url = requests.compat.urljoin(base_url, href)
            markdown_lines.append(f"[{link_text}]({full_url})")
        elif element.name == "img":
            # Images
            src = element.get("src", "")
            alt_text = element.get("alt", "")
            full_src = requests.compat.urljoin(base_url, src)
            markdown_lines.append(f"![{alt_text}]({full_src})")
            metadata["images"].append(full_src)
        elif element.name == "table":
            # Tables
            markdown_table = self._parse_table(element)
            markdown_lines.append(markdown_table)
            metadata["tables"].append(markdown_table)
        else:
            # Recursively process child elements
            for child in element.children:
                if isinstance(child, Tag):
                    self._html_to_markdown(
                        child,
                        markdown_lines,
                        metadata,
                        base_url,
                        indent_level=indent_level,
                    )

    def _parse_table(self, table: Tag) -> str:
        """
        Converts an HTML table to Markdown format.

        Args:
            table (Tag): The HTML table element.

        Returns:
            str: The table in Markdown format.
        """
        rows = []
        for tr in table.find_all("tr"):
            cells = []
            for th in tr.find_all("th"):
                cells.append(th.get_text(strip=True))
            for td in tr.find_all("td"):
                cells.append(td.get_text(strip=True))
            rows.append(cells)

        if not rows:
            return ""

        # Determine the number of columns
        num_columns = max(len(row) for row in rows)
        headers = rows[0] if rows else [""] * num_columns

        # Build Markdown table
        markdown_table = []
        # Header row
        header_line = "| " + " | ".join(headers) + " |"
        markdown_table.append(header_line)
        # Separator row
        separator_line = "| " + " | ".join(["---"] * num_columns) + " |"
        markdown_table.append(separator_line)
        # Data rows
        for row in rows[1:]:
            # Pad the row if it has fewer cells
            row += [""] * (num_columns - len(row))
            row_line = "| " + " | ".join(row) + " |"
            markdown_table.append(row_line)

        return "\n".join(markdown_table)

    def save_documents(
        self,
        documents: List[Dict[str, Any]],
        output_dir: str = "scraped_documents",
        to_pickle: bool = True,
    ):
        """
        Saves the scraped Markdown documents and metadata to the specified directory.

        Args:
            documents (List[Dict[str, Any]]): List of dictionaries with 'content' and 'metadata'.
            output_dir (str): Directory where the documents will be saved.
            to_pickle (bool): Whether to save the documents as pickle files. If False, the documents will be saved as markdown files.
        """
        os.makedirs(output_dir, exist_ok=True)
        if to_pickle:
            pickle_file_path = os.path.join(output_dir, "documents.pkl")
            with open(pickle_file_path, "wb") as pickle_file:
                pickle.dump(documents, pickle_file)
            logger.info("Saved documents to pickle file: %s", pickle_file_path)
        else:
            for idx, doc in enumerate(documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                base_filename = f"document_{idx + 1}"
                markdown_file_path = os.path.join(output_dir, f"{base_filename}.md")
                metadata_file_path = os.path.join(
                    output_dir, f"{base_filename}_metadata.yaml"
                )

                # Save content
                try:
                    with open(markdown_file_path, "w", encoding="utf-8") as md_file:
                        md_file.write(content)
                    logger.info("Saved document: %s", markdown_file_path)
                except Exception as e:
                    logger.error(
                        "Failed to save document %s: %s", markdown_file_path, e
                    )

                # Save metadata
                try:
                    import yaml

                    with open(metadata_file_path, "w", encoding="utf-8") as meta_file:
                        yaml.dump(metadata, meta_file)
                    logger.info("Saved metadata: %s", metadata_file_path)
                except Exception as e:
                    logger.error(
                        "Failed to save metadata %s: %s", metadata_file_path, e
                    )
