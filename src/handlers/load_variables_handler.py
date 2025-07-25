"""
Load and save global variables from/to a JSON file.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)
logger.info("Load variables started")


def load_json(file_path="./config/variables.json"):
    """
    Load global variables from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing global variables.
    Returns:
        dict: A dictionary containing the global variables.
    """
    if not os.path.exists(file_path):
        logger.error("File %s not found. Using default values.", file_path)
        print("❌ File ", file_path, " not found. Using default values.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            variables = json.load(file)
            return variables
    except json.JSONDecodeError:
        logger.error(" Invalid JSON in file %s. Using default values.", file_path)
        print("❌ Invalid JSON in file ", file_path, ". Using default values.")
        return {}


def get_json_key_value(key, file_path="./config/variables.json"):
    """
    Safely load a value from a JSON file by key.
    Args:
        file_path (str): Path to the JSON file.
        key (str): Key to look for in the JSON data.
    Returns:
        The value associated with the key if found, otherwise None.
    """
    if not os.path.isfile(file_path):
        logger.warning(" Warning File does not exist: %s", file_path)
        print("⚠️ Warning File does not exist: ", file_path)
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(" Warning: Failed to parse JSON: %s", e)
        print("⚠️ Warning Failed to parse JSON: ", e)
        return None

    if key not in data:
        logger.warning(" Warning: Key %s not found in JSON.", key)
        print("⚠️ Warning Key ", key, " not found in JSON.")
        return None

    return data[key]


def get_int_variable(var_name, default=1800, file_path="./config/variables.json"):
    """
    Fetch an integer variable from the JSON file.
    If it is a string, attempt to convert it to an integer.
    If invalid or missing, return the default value.
    Args:
        var_name (str): The name of the variable to fetch.
        default (int): The default value to return if the variable is not found or invalid.
        file_path (str): Path to the JSON file containing global variables.
    Returns:
        int: The value of the variable as an integer, or the default value if not found or invalid.
    """
    variables = load_json(file_path)
    value = variables.get(var_name, default)  # Get the value or default

    # Try to convert strings to integers
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            logger.warning(
                " Warning: %s has an invalid integer format ('{value}'). "
                "Using default {default}.",
                var_name,
            )
            print(
                "⚠️ Warning: ",
                var_name,
                " has an invalid integer format (",
                value,
                ". Using default ",
                default,
            )
            return default

    logger.warning(
        " Warning: %s is not a valid type. Using default {default}.", var_name
    )
    print("⚠️ Warning: ", var_name, " is not a valid type. Using default ", default, ".")
    return default


def load_portfolio_from_file(file_path="./config/portfolio.json"):
    """
    Load portfolio data from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing portfolio data.
    Returns:
        list: A list containing the portfolio data.
    """
    if not os.path.exists(file_path):
        logger.error(
            " Portfolio file %s not found. Using an empty portfolio.", file_path
        )
        print("❌ Portfolio file ", file_path, " not found. Using an empty portfolio.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            portfolio = json.load(file)
            logger.info(" Portfolio loaded from %s.", file_path)
            print("✅ Portfolio loaded from ", file_path, ".")
            return portfolio
    except json.JSONDecodeError:
        logger.error(
            " Invalid JSON in portfolio file %s. Using an empty portfolio.", file_path
        )
        print(
            "❌ Invalid JSON in portfolio file ",
            file_path,
            ". Using an empty portfolio.",
        )
        return []
    # pylint:disable=broad-exception-caught
    except Exception as e:
        logger.error(
            " Error loading portfolio from %s: %s. Using an empty portfolio.",
            file_path,
            e,
        )
        print(
            "❌ Error loading portfolio from ",
            file_path,
            ": ",
            e,
            ". Using an empty portfolio.",
        )
        return []


def load_transactions(file_path="./config/transactions.json"):
    """
    Load transactions from JSON file.
    Args:
        file_path (str): Path to the JSON file containing transactions.
    Returns:
        list: A list of transactions, or an empty list if the file is missing or invalid.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_keyword_list(file_path="./config/keywords.json"):
    """
    Load a list of keywords from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing keywords.
    Returns:
        list: A list of keywords if the file is valid, otherwise an empty list.
    """
    if not os.path.exists(file_path):
        logger.error(" File %s not found. Returning an empty list.", file_path)
        print("❌ File ", file_path, " not found. Returning an empty list.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            keywords = json.load(file)
            if isinstance(keywords, list):
                print("✅ Loaded ", len(keywords), " keywords from ", file_path, ".")
                return keywords

            logger.warning(
                " Warning: Expected a list in %s, "
                "but got something else. Returning empty list.",
                file_path,
            )
            print(
                "⚠️ Warning: Expected a list in ",
                file_path,
                ", but got something else. Returning empty list.",
            )
            return []
    except json.JSONDecodeError:
        logger.error(" Invalid JSON in %s. Returning empty list.", file_path)
        print("❌ Invalid JSON in ", file_path, ". Returning empty list.")
        return []


def load_symbol_to_id(file_path="./config/symbol_to_id.json"):
    """
    Load the symbol-to-ID mapping from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing the symbol-to-ID mapping.
    Returns:
        dict: A dictionary mapping symbols to IDs,
        or an empty dictionary if the file is missing or invalid.
    """
    if not os.path.exists(file_path):
        logger.error(
            " Symbol-to-ID file %s not found. Using an empty mapping.", file_path
        )
        print("❌ Symbol-to-ID file ", file_path, " not found. Using an empty mapping.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            symbol_to_id = json.load(file)
            print(f"✅ Symbol-to-ID mapping loaded from '{file_path}'.")
            return symbol_to_id
    except json.JSONDecodeError:
        logger.error(
            " Invalid JSON in symbol-to-ID file %s. Using an empty mapping.", file_path
        )
        print(
            f"❌ Invalid JSON in symbol-to-ID file '{file_path}'. Using an empty mapping."
        )
        return {}


def get_all_symbols():
    """
    Reads a list of transactions from a JSON file and returns a list of unique symbols.
    Returns:
        list: A list of unique symbols found in the transactions.
    """
    transactions = load_transactions()

    if not isinstance(transactions, list) or len(transactions) == 0:
        logger.warning("Warning: JSON file is empty or not a list of transactions.")
        print("⚠️ Warning: JSON file is empty or not a list of transactions.")
        return []

    symbols = set()

    for tx in transactions:
        if isinstance(tx, dict) and "symbol" in tx:
            symbols.add(tx["symbol"])

    return list(symbols)


def load_rsi_categories(filepath="./config/rsi_categories.json"):
    """
    Load RSI categories from a JSON file and add a dynamic test function to each category.
    Args:
        filepath (str): Path to the JSON file containing RSI categories.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw_categories = json.load(f)

    # Add a dynamic `test` function to each category
    for cat in raw_categories:
        min_val = cat.get("min")
        max_val = cat.get("max")
        if min_val is not None and max_val is not None:
            cat["test"] = lambda v, mi=min_val, ma=max_val: mi <= v < ma
        elif min_val is not None:
            cat["test"] = lambda v, mi=min_val: v >= mi
        elif max_val is not None:
            cat["test"] = lambda v, ma=max_val: v <= ma
        else:
            cat["test"] = lambda v: False  # fallback
    return raw_categories
