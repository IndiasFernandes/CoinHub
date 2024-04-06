from hyperliquid.info import Info
from hyperliquid.utils import constants

info = Info(constants.TESTNET_API_URL, skip_ws=True)
user_state = info.user_state("0xa9dA24397F0B02eaa39cDBCae312559CaEe17985")
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
        else:
            print(value)

print_dict(user_state)