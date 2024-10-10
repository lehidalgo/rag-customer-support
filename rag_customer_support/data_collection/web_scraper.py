from typing import List, Dict, Any
from utils.config_loader import load_config
from utils.logger import get_logger
from bs4 import BeautifulSoup
import requests
import time

logger = get_logger(__name__)


class WebScraper:
    """
    A class for scraping web content using BeautifulSoup.

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

    def scrape(self) -> List[str]:
        """
        Scrapes content from the configured starting URLs.

        Returns:
            List[str]: A list of scraped text content.
        """
        documents = []
        headers = {"User-Agent": self.user_agent}

        for url in self.start_urls:
            try:
                logger.debug("Scraping URL: %s", url)
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                content = self._parse_content(response.text)
                documents.append(content)
                logger.debug("Scraped content from: %s", url)
                time.sleep(self.delay)
            except requests.RequestException as e:
                logger.error("Failed to scrape URL %s: %s", url, e)

        return documents

    def _parse_content(self, html: str) -> str:
        """
        Parses HTML content and extracts text.

        Args:
            html (str): HTML content as a string.

        Returns:
            str: Extracted text content.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts and styles
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)
        return text
