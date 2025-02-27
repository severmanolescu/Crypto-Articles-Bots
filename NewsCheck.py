import logging
import requests
import asyncio
import cloudscraper

from bs4 import BeautifulSoup

# Import scrapers
from sdk.scrapers.crypto_news_scraper import CryptoNewsScraper
from sdk.scrapers.cointelegraph_scraper import CointelegraphScraper
from sdk.scrapers.bitcoin_magazine_scraper import BitcoinMagazineScraper

# Import your SDK modules
from sdk.DataBase.DataBaseHandler import DataBaseHandler
from sdk import LoadVariables as LoadVariables
from sdk.SendTelegramMessage import TelegramMessagesHandler
from sdk.OpenAIPrompt import OpenAIPrompt

# Logging configuration with rotating file handler
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('log.log', maxBytes=100_000_000, backupCount=3)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

class CryptoNewsCheck:
    def __init__(self, db_path="./articles.db"):
        """
        Main orchestrator for scraping and notifying about new articles.
        """
        # Telegram/AI summary settings
        self.send_ai_summary = None
        self.openAIPrompt = None
        self.keywords = None
        self.telegram_not_important_chat_id = None
        self.telegram_important_chat_id = None
        self.telegram_api_token = None

        # Database handler (see sdk/DataBaseHandler.py)
        self.data_base = DataBaseHandler(db_path)

        # URLs for different news sources
        self.urls = {
            "crypto.news": "https://crypto.news/",
            "cointelegraph": "https://cointelegraph.com/",
            "bitcoinmagazine": "https://bitcoinmagazine.com/articles"
        }

        # Create a cloudscraper instance for scraping
        self.scraper = cloudscraper.create_scraper()

        # Retry settings
        self.max_retries = 5

        self.telegram_message = TelegramMessagesHandler()

    def reload_the_data(self):
        """
        Reload environment variables, API tokens, and so forth.
        """
        variables = LoadVariables.load()
        self.telegram_api_token = variables.get("TELEGRAM_API_TOKEN_ARTICLES", "")
        self.telegram_important_chat_id = variables.get("TELEGRAM_CHAT_ID_FULL_DETAILS", [])
        self.telegram_not_important_chat_id = variables.get("TELEGRAM_CHAT_ID_PARTIAL_DATA", [])
        self.keywords = LoadVariables.load_keyword_list()

        open_ai_api = variables.get('OPEN_AI_API', '')
        self.openAIPrompt = OpenAIPrompt(open_ai_api)
        self.send_ai_summary = variables.get("SEND_AI_SUMMARY", "")

        self.telegram_message.reload_the_data()

    async def fetch_page(self, url):
        """
        Fetch the page with retry logic and exponential backoff.
        Switch to `await asyncio.sleep(...)` for true async non-blocking retries.
        """
        for attempt in range(1, self.max_retries + 1):
            delay = 2 ** attempt
            try:
                response = self.scraper.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [403, 429]:
                    logging.warning(
                        f"Blocked or Rate Limited (Status {response.status_code})! "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)  # non-blocking delay
                else:
                    logging.warning(
                        f"Unexpected status code: {response.status_code}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"Connection error: {e}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            except requests.exceptions.Timeout:
                logging.warning(f"Request timed out. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            except requests.exceptions.RequestException as e:
                logging.warning(f"Other request error: {e}")
                break  # Stop retrying on other request errors

        logging.error(f"Max retries reached. Could not fetch {url}.")
        return None

    def scrape_articles(self, soup, source):
        """
        Decide which scraper to use based on the 'source' string.
        Each scraper class is responsible for returning a list of:
          { "headline": ..., "link": ..., "highlights": ... }
        """
        if source == "crypto.news":
            scraper = CryptoNewsScraper(self.keywords)
            return scraper.scrape(soup)

        elif source == "cointelegraph":
            scraper = CointelegraphScraper(self.keywords)
            return scraper.scrape(soup)

        elif source == "bitcoinmagazine":
            scraper = BitcoinMagazineScraper(self.keywords)
            return scraper.scrape(soup)

        return []

    async def generate_summary(self, link):
        """
        Generate article summary using OpenAI (if self.send_ai_summary is True).
        """
        return await self.openAIPrompt.generate_summary(link)

    async def check_news(self, source):
        """
        Orchestrates the scraping and notification for a single source.
        """
        page_content = await self.fetch_page(self.urls[source])
        if page_content:
            print(f"\n✅ Connected to {source} successfully!")
            logging.info(f"Connected to {source} successfully!")
            soup = BeautifulSoup(page_content, "html.parser")
            articles = self.scrape_articles(soup, source)

            if articles:
                print(f"📰 Found {len(articles)} articles from {source}.")
                logging.info(f"Found {len(articles)} articles from {source}.")
                for article in articles:
                    # Insert or ignore in DB
                    row_inserted = await self.data_base.save_article_to_db(
                        source,
                        article['headline'],
                        article['link'],
                        article['highlights']
                    )

                    # If brand-new article, optionally generate summary and send message
                    if row_inserted == 1:
                        summary_text = ""
                        if self.send_ai_summary == "True":
                            summary_text = await self.generate_summary(article['link'])
                            # Store summary in DB
                            await self.data_base.update_article_summary_in_db(article['link'], summary_text)

                        # Build the Telegram message
                        if summary_text:
                            message = (
                                f"📰 New Article Found!\n"
                                f"📌 {article['headline']}\n"
                                f"🔗 {article['link']}\n"
                                f"🤖 {summary_text}\n"
                                f"🔍 Highlights: {article['highlights']}\n"
                            )
                        else:
                            message = (
                                f"📰 New Article Found!\n"
                                f"📌 {article['headline']}\n"
                                f"🔗 {article['link']}\n"
                                f"🔍 Highlights: {article['highlights']}\n"
                            )

                        # Send Telegram message
                        await self.telegram_message.send_telegram_message(message, self.telegram_api_token)
                    else:
                        # Already in DB
                        logging.info(f"Skipping existing article: {article['link']}")
            else:
                logging.warning(f"No new articles found for {source}.")
        else:
            logging.error(f"Failed to fetch {source}.")

    async def run(self):
        """
        Initialize the DB if necessary, and launch the scrapers in parallel.
        """
        await self.data_base.init_db()  # create the table if not exist

        # Scrape all sources in parallel
        await asyncio.gather(
            self.check_news("crypto.news"),
            self.check_news("cointelegraph"),
            self.check_news("bitcoinmagazine")
        )