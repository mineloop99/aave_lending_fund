from brownie import network, accounts, config, interface
from web3 import Web3

LOCAL_BLOCKCHAIN_DEVELOPMENT = [
    "development",
    "ganache-local",
    "mainnet-fork",
    "mainnet-fork-dev",
]

DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_DEVELOPMENT:
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["private_key"])
