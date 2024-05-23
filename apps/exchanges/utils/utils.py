import os

import ccxt
import pandas as pd


def run_exchange(exchange_id, api_key, secret):
    if exchange_id == 'hyperliquid':
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
        })
    return exchange
def ensure_dir(path):
    """Ensure the directory exists, create it if it doesn't."""
    os.makedirs(path, exist_ok=True)

def file_exists(path):
    """Check if a file exists."""
    return os.path.exists(path)

def merge_and_save_data(new_data, file_path):
    """Merge new data with existing data and save to a file."""
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        existing_data.index = pd.to_datetime(existing_data.index)  # Ensure the index is datetime

        # Ensure new_data index is also datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(new_data.index):
            new_data.index = pd.to_datetime(new_data.index)

        # Concatenate, remove duplicates, and sort
        merged_data = pd.concat([existing_data, new_data]).drop_duplicates().sort_index()
    else:
        merged_data = new_data

    # Save merged data
    merged_data.to_csv(file_path)


def print_dict(d, indent=0):
    """
    Recursively prints nested dictionaries.
    Parameters:
    - d (dict): The dictionary to print.
    - indent (int): The current indentation level for pretty printing.
    """
    for key, value in d.items():
        print('    ' * indent + str(key) + ':', end=' ')
        if isinstance(value, dict):
            print()  # Move to next line before printing nested dictionary
            print_dict(value, indent + 1)  # Recursive call with increased indent
        elif isinstance(value, list):
            print()  # List will be processed item by item
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    print('    ' * (indent + 1) + f"Item {i + 1}:")
                    print_dict(item, indent + 2)
                else:
                    print('    ' * (indent + 1) + str(item))
        else:
            print(value)



def import_csv(filepath):
    """ Safely import CSV file to a list. """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return [line.strip().split(',') for line in file.readlines()]
    else:
        return []  # Return an empty list if file does not exist