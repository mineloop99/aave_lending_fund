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


def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_address_provider"]
    )
    # Address
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    # ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, sender, erc20_address, account):
    print("Approving ERC20 token ....")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(sender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of Eth deposited")
    print(f"You have {total_debt_eth} worth of Eth borrowed")
    print(f"You can borrow {total_collateral_eth} worth of Eth")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(data_feed):
    eth_price_feed = interface.IAggregatorV3(data_feed)
    latest_price = eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, "ether")
    print(f"DAI/ETH is {converted_price}/ETH")
    return float(latest_price)


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed~!")
