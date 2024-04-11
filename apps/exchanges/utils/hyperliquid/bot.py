from datetime import datetime
import eth_account
from eth_account.signers.local import LocalAccount
import json
import os
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from apps.exchanges.models import ExchangeInfo
from apps.exchanges.utils.utils import print_dict


class BotAccount:
    def __init__(self, base_url=None, skip_ws=False):

        # Initialize the BotAccount class
        self.base_url = base_url
        self.skip_ws = skip_ws
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.account, self.config = self.load_account_config()
        self.address = self.get_account_address()

        # Initialize the Info class
        self.info = Info(self.base_url, self.skip_ws)

        # Initialize state information
        self.user_state = self.info.user_state(self.address)
        self.spot_meta = self.info.spot_meta()
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
        # print all variables
        print("Account address:", self.address)
        print("Config file path:", self.config_path)
        print("Config details:")
        print_dict(self.config)
        print("Exchange base URL:", self.base_url)
        print("Exchange account address:", self.exchange.account_address)
        # account
        print("Account:", self.account)
        print("Asset positions:")
        if self.user_state['assetPositions']:
            print_dict({'assetPositions': self.user_state['assetPositions']})
        else:
            print("No active positions.")
        print("Withdrawable amount:", self.user_state.get('withdrawable', 'N/A'))
        print("Spot meta:")
        print_dict(self.spot_meta)

        print("User state:")
        print(self.user_state)
        print("Margin summary:")
        print(self.margin_summary)

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

    # def that gets the self.info.all_mids() and prints it
    def all_coins(self):
        # build a list of coins
        self.info = Info(self.base_url, self.skip_ws)
        self.all_mids = self.info.all_mids()
        # print(f"All Mids: {self.all_mids}")
        return self.all_mids

    def test_functions(self):

        # Test and print results for various information functions
        self.info = Info(self.base_url, self.skip_ws)
        print("Testing Info functions...\n")

        # User State
        user_state = self.info.user_state(self.address)
        print(
            f"User State: Account value: {user_state['marginSummary']['accountValue']}, Withdrawable: {user_state['withdrawable']}")

        # Spot User State
        spot_user_state = self.info.spot_user_state(self.address)
        print(f"Spot User State: Balances: {spot_user_state['balances']}")

        # Open Orders
        open_orders = self.info.open_orders(self.address)
        print(f"Open Orders: {open_orders}")

        # Frontend Open Orders
        frontend_open_orders = self.info.frontend_open_orders(self.address)
        print(f"Frontend Open Orders: {frontend_open_orders}")

        # All Mids
        all_mids = self.info.all_mids()
        print(f"All Mids: {len(all_mids)} market identifiers available.")

        # User Fills
        user_fills = self.info.user_fills(self.address)
        print(f"User Fills: {len(user_fills)} fills recorded.")

        # Meta
        meta = self.info.meta()
        print(f"Meta: {len(meta['universe'])} tokens in the trading universe.")

        # Spot Meta
        spot_meta = self.info.spot_meta()
        print(f"Spot Meta: {len(spot_meta['tokens'])} tokens available for spot trading.")


        # self.funding_history = self.info.funding_history('BTCUSDT', 0)
        # self.user_funding_history = self.info.user_funding_history(self.address, 0)
        # self.l2_snapshot = self.info.l2_snapshot('BTCUSDT')
        # self.candles_snapshot = self.info.candles_snapshot('BTCUSDT', '5m', 0, 0)
        # self.query_order_by_oid = self.info.query_order_by_oid(self.address, 0)
        # self.query_order_by_cloid = self.info.query_order_by_cloid(self.address, 0)
        # self.query_referral_state = self.info.query_referral_state(self.address)
        # self.query_sub_accounts = self.info.query_sub_accounts(self.address)