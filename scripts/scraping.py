import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_customer_support.utils.logger import get_logger
from rag_customer_support.data_collection.web_scraper import WebScraper

logger = get_logger(__name__)

web_scraper = WebScraper(config_path="configs/web_scraper_config.yaml")
scraped_documents = web_scraper.scrape()
logger.info(f"Scraped {len(scraped_documents)} documents.")
web_scraper.save_documents(
    documents=scraped_documents, output_dir="../data/scraped_documents", to_pickle=True
)
