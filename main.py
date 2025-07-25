"""
main.py
This script is the main entry point for the Crypto Value Bot and News Check application.
"""

import argparse
import asyncio
import logging
from datetime import datetime
from typing import NoReturn

from src.bots.crypto_value_handler import CryptoValueBot
from src.handlers.load_variables_handler import get_int_variable
from src.handlers.logger_handler import setup_logger
from src.handlers.news_check_handler import CryptoNewsCheck


class Application:
    """
    Main application class that initializes and runs the Crypto Value Bot and News Check.
    """

    def __init__(self):
        setup_logger()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Main started")
        self.crypto_value_bot = CryptoValueBot()
        self.crypto_news_check = CryptoNewsCheck()
        self.is_running = True

    def reload_data(self) -> None:
        """Reload data for both bots"""
        self.crypto_value_bot.reload_the_data()
        self.crypto_news_check.reload_the_data()

    async def run_loop(self) -> NoReturn:
        """Main application loop"""
        while self.is_running:
            try:
                self.reload_data()
                sleep_time = get_int_variable("SLEEP_DURATION", 1800)

                print("\n🧐 Check for new articles!")
                await self.crypto_news_check.run()

                print("\n📤 Send crypto value!")
                self.crypto_value_bot.reload_the_data()
                await self.crypto_value_bot.fetch_data()

                now_date = datetime.now()
                time_str = now_date.strftime("%H:%M")

                self.logger.info(" Ran at: %s", time_str)
                self.logger.info(" Wait %.2f minutes", sleep_time / 60)

                print(f"\n⌛Checked at: {time_str}")
                print(f"⏳ Wait {sleep_time / 60:.2f} minutes!\n\n")
                await asyncio.sleep(sleep_time)

            # pylint: disable=broad-exception-caught
            except Exception as e:
                self.logger.error("Error in main loop: %s", str(e))
                await asyncio.sleep(5)


def main() -> None:
    """
    Main function handling command line arguments and application startup
    """
    parser = argparse.ArgumentParser(
        description="Recreate the news data base if needed."
    )
    parser.add_argument(
        "-r", "--recreate", action="store_true", help="Recreate the news data base"
    )
    args = parser.parse_args()

    app = Application()

    if args.recreate:
        print("Recreating the data base...")
        asyncio.run(app.crypto_news_check.recreate_data_base())
    else:
        asyncio.run(app.run_loop())


if __name__ == "__main__":
    main()
