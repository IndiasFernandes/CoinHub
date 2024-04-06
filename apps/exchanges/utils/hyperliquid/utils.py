from datetime import datetime

import eth_account
from eth_account.signers.local import LocalAccount
import json
import os

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

from apps.exchanges.models import ExchangeInfo


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

class BotAccount:
    def __init__(self, base_url=None, skip_ws=False):
        self.base_url = base_url
        self.skip_ws = skip_ws
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.account, self.config = self.load_account_config()
        self.address = self.get_account_address()
        self.info = Info(self.base_url, self.skip_ws)
        self.user_state = self.info.user_state(self.address)
        self.margin_summary = self.user_state["marginSummary"]
        self.check_account_value()
        self.exchange = Exchange(self.account, self.base_url, account_address=self.address)
        print(f"Exchange created for account {self.address}")

    def load_account_config(self):
        with open(self.config_path) as f:
            config = json.load(f)
        account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
        return account, config


    def get_account_address(self):
        address = self.config["account_address"]
        if address == "":
            address = self.account.address
        print("Running with account address:", address)
        if address != self.account.address:
            print("Running with agent address:", self.account.address)
        return address

    def check_account_value(self):
        if float(self.margin_summary["accountValue"]) == 0:
            print("Not running the example because the provided account has no equity.")
            url = self.info.base_url.split(".", 1)[1]
            error_string = f"No accountValue:\nIf you think this is a mistake, make sure that {self.address} has a balance on {url}.\nIf the address shown is your API wallet address, update the config to specify the address of your account, not the address of the API wallet."
            raise Exception(error_string)
        else:
            print("Running the example because the provided account has equity.")

    def print_info(self):
        print("User state:")
        print_dict(self.user_state)
        print("Margin summary:")
        print_dict(self.margin_summary)
        print("User State:")
        print_dict(self.user_state)

    def update_exchange_info(self):
        # Assuming self.user_state is up to date
        self.user_state = self.info.user_state(self.address)
        self.margin_summary = self.user_state["marginSummary"]
        account_value = self.margin_summary["accountValue"]
        total_margin_used = self.margin_summary["totalMarginUsed"]
        total_net_position = self.margin_summary["totalNtlPos"]
        total_raw_usd = self.margin_summary["totalRawUsd"]
        withdrawable = self.user_state.get("withdrawable", 0)  # Fallback to 0 if not available

        # Update class attributes
        self.account_value = account_value
        self.total_margin_used = total_margin_used
        self.total_net_position = total_net_position
        self.total_raw_usd = total_raw_usd
        self.withdrawable = withdrawable

        # Create a new ExchangeInfo record
        exchange_info = ExchangeInfo.objects.create(
            timestamp=datetime.now(),
            account_value=account_value,
            total_margin_used=total_margin_used,
            total_net_position=total_net_position,
            total_raw_usd=total_raw_usd,
            withdrawable=withdrawable
        )
        print(f"Exchange information updated at {exchange_info.timestamp}")

#
def print_main(bot_account):
    print("\n=== Bot Account Overview ===\n")
    print(f"Account Address: {bot_account.address}")
    if hasattr(bot_account.account, 'address') and bot_account.account.address != bot_account.address:
        print(f"Agent Address: {bot_account.account.address}")

    print(f"\nConfig File Path: {bot_account.config_path}")
    print("\nConfig Details:")
    print_dict(bot_account.config)

    print("\nExchange Base URL:", bot_account.exchange.base_url)
    print("Exchange Account Address:", bot_account.exchange.account_address)

    print("\n=== Financial Overview ===")
    print("Margin Summary:")
    print_dict(bot_account.margin_summary)

    print("\nAsset Positions:")
    if bot_account.user_state['assetPositions']:
        print_dict({'assetPositions': bot_account.user_state['assetPositions']})
    else:
        print("No active positions.")

    print("\nWithdrawable Amount:", bot_account.user_state.get('withdrawable', 'N/A'))


# Assuming bot_account is an instance of BotAccount with all necessary information loaded

# # Example usage
# bot_account = BotAccount()
# # bot_account.print_info()
# print_main(bot_account)