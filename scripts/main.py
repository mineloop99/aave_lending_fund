from brownie import config, network
from eth_utils import address
from scripts.get_weth import get_weth
from scripts.helper import (
    LOCAL_BLOCKCHAIN_DEVELOPMENT,
    approve_erc20,
    get_account,
    get_asset_price,
    get_borrowable_data,
    get_lending_pool,
    repay_all,
)
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.03, "ether")


def main():
    # get_weth() #get weth
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in LOCAL_BLOCKCHAIN_DEVELOPMENT:
        get_weth()
    lending_pool = get_lending_pool()

    # approve sending out ERC20
    try:
        approve_erc20(amount, lending_pool.address, erc20_address, account)
        print(lending_pool)
        print("Depositing...")
        tx = lending_pool.deposit(
            erc20_address, amount, account.address, 0, {"from": account}
        )
        tx.wait(1)
    except:
        pass
    # get borrowable data
    borrowable_eth, _ = get_borrowable_data(lending_pool, account)
    print("Lets's borrow!")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_data_feed"]
    )
    # Borrow_eth -> borrowable_dai * 95%
    amount_dai_to_borrow = Web3.toWei(
        (1 / dai_eth_price) * (borrowable_eth * 0.95), "ether"
    )

    amount_dai_to_repay = amount_dai_to_borrow
    print(f"Borrowing... {amount_dai_to_borrow} DAI")
    # Borrow!
    dai_address = config["networks"][network.show_active()]["dai_token"]
    try:
        borrow_tx = lending_pool.borrow(
            dai_address,
            amount_dai_to_borrow * 10 ** 18,
            1,
            0,
            account.address,
            {"from": account},
        )
        borrow_tx.wait(1)
    except:
        pass
    print("Borrowed!")
    # Repaying!
    _, total_debt = get_borrowable_data(lending_pool, account)
    amount_dai_to_repay = Web3.toWei((total_debt / dai_eth_price), "ether")
    print(f"Repaying... {amount_dai_to_repay} DAI")
    repay_all(amount_dai_to_repay * 10 ** 18, lending_pool, account)
    print("Deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!")
